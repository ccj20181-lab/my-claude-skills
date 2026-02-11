/**
 * 字幕组件（短视频字幕风格）
 * - 同场景只显示这一处文案，避免重复框
 * - 自动按标点/长度切分，控制每页最多两行，并在场景时长内分页播放
 */

import React, { useMemo } from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { whiteboardTheme } from "../theme/whiteboard";

type SubtitleStyle = "subtitle" | "compact";

const PUNCT = new Set(["，", "。", "！", "？", "；", "：", "、", ",", ".", "!", "?", ";", ":"]);

const normalizeText = (raw: string) =>
  raw
    .replace(/\s+/g, " ")
    .replace(/\s*([，。！？；：、,.!?;:])\s*/g, "$1")
    .trim();

const splitToPhrases = (text: string): string[] => {
  const out: string[] = [];
  let buf = "";
  for (const ch of text) {
    buf += ch;
    if (PUNCT.has(ch)) {
      out.push(buf);
      buf = "";
    }
  }
  if (buf.trim()) out.push(buf);
  return out.filter(Boolean);
};

const chunkByLen = (s: string, maxLen: number): string[] => {
  if (s.length <= maxLen) return [s];
  const out: string[] = [];
  let i = 0;
  while (i < s.length) {
    out.push(s.slice(i, i + maxLen));
    i += maxLen;
  }
  return out;
};

const buildLines = (text: string, maxCharsPerLine: number): string[] => {
  const phrases = splitToPhrases(text);
  const lines: string[] = [];
  let line = "";

  const pushLine = () => {
    const v = line.trim();
    if (v) lines.push(v);
    line = "";
  };

  for (const p0 of phrases.length ? phrases : [text]) {
    for (const p of chunkByLen(p0, Math.max(8, Math.floor(maxCharsPerLine * 1.35)))) {
      if (!line) {
        line = p;
        continue;
      }
      if ((line + p).length <= maxCharsPerLine) {
        line += p;
      } else {
        pushLine();
        line = p;
      }
    }
  }

  pushLine();
  return lines;
};

const buildPages = (text: string, maxCharsPerLine: number, maxPages: number): string[] => {
  // Try to fit pages by slightly increasing max chars if needed.
  for (let m = maxCharsPerLine; m <= maxCharsPerLine + 6; m++) {
    const lines = buildLines(text, m);
    const pages: string[] = [];
    for (let i = 0; i < lines.length; i += 2) {
      pages.push(i + 1 < lines.length ? `${lines[i]}\n${lines[i + 1]}` : lines[i]);
    }
    if (pages.length <= maxPages) return pages;
  }

  // Fallback: hard-cap to maxPages by merging tail.
  const lines = buildLines(text, maxCharsPerLine + 6);
  const pages: string[] = [];
  for (let i = 0; i < lines.length; i += 2) {
    pages.push(i + 1 < lines.length ? `${lines[i]}\n${lines[i + 1]}` : lines[i]);
  }
  if (pages.length <= maxPages) return pages;
  const head = pages.slice(0, maxPages - 1);
  const tail = pages.slice(maxPages - 1).join(" ");
  head.push(tail);
  return head;
};

const renderHighlightedText = (text: string, accentColor: string) => {
  // Highlight numbers/percentages for finance readability.
  const parts: Array<{ t: string; hl: boolean }> = [];
  const re = /(\d+(?:\.\d+)?%?)/g;
  let last = 0;
  let m: RegExpExecArray | null;
  // eslint-disable-next-line no-cond-assign
  while ((m = re.exec(text))) {
    if (m.index > last) parts.push({ t: text.slice(last, m.index), hl: false });
    parts.push({ t: m[1], hl: true });
    last = m.index + m[1].length;
  }
  if (last < text.length) parts.push({ t: text.slice(last), hl: false });

  return (
    <>
      {parts.map((p, i) =>
        p.hl ? (
          <span
            key={`${i}-${p.t}`}
            style={{
              padding: "0 6px",
              borderRadius: 10,
              backgroundColor: `${accentColor}22`,
              boxShadow: `inset 0 -3px 0 ${accentColor}55`,
            }}
          >
            {p.t}
          </span>
        ) : (
          <span key={`${i}-${p.t}`}>{p.t}</span>
        )
      )}
    </>
  );
};

export const Subtitle: React.FC<{
  text: string;
  durationInFrames: number;
  accentColor?: string;
  style?: SubtitleStyle;
}> = ({ text, durationInFrames, accentColor = whiteboardTheme.colors.accent.blue, style = "subtitle" }) => {
  const frame = useCurrentFrame();
  const { typography, spacing, borderRadius, layout } = whiteboardTheme;

  const cleaned = useMemo(() => normalizeText(text), [text]);

  const maxCharsPerLine = style === "subtitle" ? 16 : 20;
  const pages = useMemo(() => buildPages(cleaned, maxCharsPerLine, 3), [cleaned, maxCharsPerLine]);

  const total = Math.max(1, durationInFrames);
  const minPerPage = 42; // >= 1.4s at 30fps, prevent rapid flicker
  const pageCount = Math.max(1, pages.length);
  const basePerPage = Math.max(minPerPage, Math.floor(total / pageCount));

  const ranges = useMemo(() => {
    const out: Array<{ start: number; end: number }> = [];
    let cur = 0;
    for (let i = 0; i < pageCount; i++) {
      const remain = total - cur;
      const pagesLeft = pageCount - i;
      const take = i === pageCount - 1 ? remain : Math.min(remain - (pagesLeft - 1) * minPerPage, basePerPage);
      out.push({ start: cur, end: cur + Math.max(minPerPage, take) });
      cur = out[out.length - 1].end;
    }
    // Clamp last end to total.
    out[out.length - 1].end = total;
    return out;
  }, [basePerPage, minPerPage, pageCount, total]);

  const pageIndex = Math.min(
    ranges.findIndex((r) => frame >= r.start && frame < r.end),
    pageCount - 1
  );
  const idx = pageIndex < 0 ? 0 : pageIndex;
  const page = pages[idx] ?? cleaned;
  const r = ranges[idx] ?? { start: 0, end: total };
  const local = Math.max(0, frame - r.start);
  const pageDur = Math.max(1, r.end - r.start);

  const enter = 10;
  const exit = 10;
  const opacityIn = interpolate(local, [0, enter], [0, 1], { extrapolateRight: "clamp" });
  const opacityOut = interpolate(local, [Math.max(0, pageDur - exit), pageDur], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const opacity = opacityIn * opacityOut;

  const rise = interpolate(local, [0, enter], [18, 0], { extrapolateRight: "clamp" });

  // Bounce micro-effect on entrance: scale 0.97 → 1.02 → 1
  const bounceScale = interpolate(local, [0, 6, 12, 18], [0.97, 1.03, 0.99, 1], {
    extrapolateRight: "clamp",
  });

  const fontSize = style === "compact" ? 34 : 38;
  const revealFrames = Math.min(Math.max(14, Math.round(page.replace(/\s/g, "").length * 1.05)), Math.round(pageDur * 0.45));
  const visibleChars = Math.floor(interpolate(local, [0, revealFrames], [0, page.length], { extrapolateRight: "clamp" }));
  const displayText = page.slice(0, visibleChars);

  return (
    <div
      style={{
        position: "absolute",
        left: layout.padding.horizontal,
        right: layout.padding.horizontal,
        bottom: 100,
        transform: `translateY(${rise}px) scale(${bounceScale})`,
        opacity,
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          width: "100%",
          display: "flex",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            width: "100%",
            maxWidth: 980,
            padding: `${spacing.sm}px ${spacing.md}px`,
            borderRadius: borderRadius.full,
            background: "linear-gradient(180deg, rgba(17, 24, 39, 0.55), rgba(17, 24, 39, 0.72))",
            border: "1px solid rgba(255, 255, 255, 0.18)",
            boxShadow: "0 14px 30px rgba(0,0,0,0.18)",
          }}
        >
          <div style={{ display: "flex", gap: 14, alignItems: "center", justifyContent: "center" }}>
            <div
              style={{
                width: 10,
                height: 42,
                borderRadius: 999,
                backgroundColor: accentColor,
                boxShadow: `0 0 0 6px ${accentColor}22`,
                flex: "0 0 auto",
              }}
            />
            <div
              style={{
                fontFamily: typography.fontFamily.body,
                fontSize,
                lineHeight: 1.25,
                fontWeight: typography.fontWeight.bold,
                color: "#FFFFFF",
                textAlign: "center",
                whiteSpace: "pre-line",
                textShadow: "0 2px 10px rgba(0,0,0,0.35)",
                letterSpacing: 0.2,
              }}
            >
              {renderHighlightedText(displayText, accentColor)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

