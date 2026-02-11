/**
 * 场景容器组件
 * Scene container with all visual elements
 */

import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";
import { Scene as SceneType, SCENE_STYLES } from "../types/scene";
import { whiteboardTheme } from "../theme/whiteboard";
import { Branding } from "./Branding";
import { TitleText } from "./TextBubble";
import { Transition } from "./Transitions";
import { Subtitle } from "./Subtitle";
import { IconCloud } from "./IconCloud";
import { Character } from "./Character";
import { HandDraw } from "./HandDraw";
import type { SceneMeta } from "../types/scene";

interface SceneProps {
  data: SceneType;
  meta: SceneMeta;
  audioPath?: string;
  durationInFrames: number;
  showSubtitle?: boolean;
}

export const Scene: React.FC<SceneProps> = ({
  data,
  meta,
  audioPath,
  durationInFrames,
  showSubtitle = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const sceneStyle = SCENE_STYLES[data.type];
  const { layout } = whiteboardTheme;
  const zones = (layout as any).zones;

  const renderBackdropIcon = () => {
    const iconPath = data.icon?.path;
    if (!iconPath) return null;

    const opacity = interpolate(frame, [0, 18], [0, 0.08], {
      extrapolateRight: "clamp",
    });
    const drift = Math.sin(frame / 90) * 10;
    const scale = 1.06 + Math.sin(frame / 120) * 0.01;

    return (
      <Img
        src={staticFile(iconPath)}
        style={{
          position: "absolute",
          left: "50%",
          top: "48%",
          width: 1100,
          height: "auto",
          opacity,
          transform: `translate(-50%, -50%) rotate(-10deg) translateX(${drift}px) scale(${scale})`,
          filter: "grayscale(0.15) blur(0.2px)",
        }}
      />
    );
  };

  const renderPrimaryIcon = () => {
    const iconPath = data.icon?.path;
    if (!iconPath) return null;

    const opacity = interpolate(frame, [0, 10], [0, 1], {
      extrapolateRight: "clamp",
    });

    const scale = spring({
      frame,
      fps,
      config: {
        damping: 14,
        stiffness: 120,
      },
    });

    const float = Math.sin(frame / 18) * 6;
    const breathe = 1 + Math.sin(frame / 80) * 0.01;

    // Title scenes get a centered icon; others use zones.hero.centerY.
    const isTitle = data.type === "title";
    const heroTop = zones?.hero?.centerY ?? 480;
    const style: React.CSSProperties = isTitle
      ? {
          left: "50%",
          top: 170,
          transform: `translateX(-50%) translateY(${float}px) scale(${scale * 0.94})`,
          width: 420,
          opacity: 0.26,
        }
      : {
          left: "50%",
          top: heroTop - 150,
          transform: `translateX(-50%) translateY(${float}px) rotate(${(1 - scale) * -7}deg) scale(${(0.9 + scale * 0.14) * breathe})`,
          width: Math.min(data.type === "hook" || data.type === "cta" ? 700 : 640, layout.width - layout.padding.horizontal * 2),
        };

    return (
      <Img
        src={staticFile(iconPath)}
        style={{
          position: "absolute",
          height: "auto",
          opacity: isTitle ? style.opacity : opacity,
          filter: "drop-shadow(0 6px 14px rgba(0, 0, 0, 0.10))",
          ...style,
        }}
      />
    );
  };

  const renderComparisonIcons = () => {
    if (data.type !== "comparison") return null;
    const primary = data.icon?.path;
    const secondary = (data.extra_icons || []).find((i) => i?.path)?.path;
    if (!primary && !secondary) return null;

    const enter = spring({ frame, fps, config: { damping: 16, stiffness: 110 } });
    const opacity = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });
    const float = Math.sin(frame / 17) * 5;

    const common: React.CSSProperties = {
      position: "absolute",
      top: 310,
      width: 430,
      height: "auto",
      opacity,
      filter: "drop-shadow(0 10px 18px rgba(0, 0, 0, 0.10))",
    };

    return (
      <>
        {primary ? (
          <Img
            src={staticFile(primary)}
            style={{
              ...common,
              left: 80,
              transform: `translateY(${float}px) rotate(-6deg) scale(${0.92 + enter * 0.1})`,
            }}
          />
        ) : null}
        {secondary ? (
          <Img
            src={staticFile(secondary)}
            style={{
              ...common,
              right: 80,
              transform: `translateY(${-float}px) rotate(6deg) scale(${0.92 + enter * 0.1})`,
            }}
          />
        ) : null}
      </>
    );
  };

  const transitionType =
    data.type === "hook" ? "zoom" :
    data.type === "title" ? "scaleFromCenter" :
    data.type === "question" ? "slideUp" :
    data.type === "explain" ? "slideLeft" :
    data.type === "analogy" ? "slideRight" :
    data.type === "example" ? "flipY" :
    data.type === "comparison" ? "wipe" :
    data.type === "summary" ? "slideDown" :
    data.type === "cta" ? "scaleFromCenter" :
    "fade";

  const extraIcons = (data.extra_icons || []).filter((i) => i?.path);

  const showTitleLayout = data.type === "title";

  const driftX = Math.sin(frame / 140) * 6;
  const driftY = Math.cos(frame / 160) * 5;

  return (
    <Transition type={transitionType as any} duration={12} durationInFrames={durationInFrames}>
      <AbsoluteFill
        style={{
          backgroundColor: sceneStyle.backgroundColor,
        }}
      >
        {/* Background pattern for whiteboard effect - REMOVED for clean white look */}
        {/* <div
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage: `
              linear-gradient(rgba(0,0,0,0.02) 1px, transparent 1px),
              linear-gradient(90deg, rgba(0,0,0,0.02) 1px, transparent 1px)
            `,
            backgroundSize: "40px 40px",
            backgroundPosition: `${Math.floor(Math.sin(frame / 120) * 10)}px ${Math.floor(
              Math.cos(frame / 140) * 10
            )}px`,
          }}
        /> */}

        {/* Branding (logo + watermark) */}
        <Branding />

        {/* Backdrop and IconCloud removed for clean visual design */}

        {/* Hero icons */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            transform: `translate(${driftX}px, ${driftY}px)`,
          }}
        >
          {data.type === "comparison" ? renderComparisonIcons() : renderPrimaryIcon()}
        </div>

        {/* Hand-drawn emphasis — prefer LLM-specified visual_action, fallback to type map */}
        {(() => {
          const handDrawMap: Record<string, "circle" | "underline" | "arrow" | "checkmark" | "cross" | "bracket"> = {
            hook: "circle",
            question: "underline",
            analogy: "arrow",
            example: "checkmark",
            comparison: "cross",
            summary: "circle",
            cta: "underline",
            explain: "arrow",
          };
          const drawType = data.visual_action && data.visual_action !== "none"
            ? data.visual_action
            : handDrawMap[data.type];
          if (!drawType) return null;
          const heroY = zones?.hero?.centerY ?? 480;
          return (
            <div style={{ position: "absolute", left: "50%", top: heroY - 60, transform: "translateX(-50%)" }}>
              <HandDraw type={drawType as any} color={sceneStyle.accentColor} strokeWidth={6} duration={22} />
            </div>
          );
        })()}

        {/* Host avatar / Character */}
        <Character
          type={data.character?.type}
          position={data.type === "cta" ? "bottom-right" : "bottom-left"}
          size={350}
          durationInFrames={durationInFrames}
        />

        {/* Title scene text - REMOVED per user request for ONLY subtitles */}
        {/* {showTitleLayout ? (
          <div style={{ position: "absolute", left: 0, right: 0, top: 180 }}>
            <TitleText title={meta.title} subtitle={data.text} />
          </div>
        ) : null} */}

        {/* Subtitle (single source of text to avoid duplicates) */}
        {showSubtitle ? (
          <Subtitle
            text={data.text}
            durationInFrames={durationInFrames}
            accentColor={sceneStyle.accentColor}
            style={data.type === "hook" || data.type === "cta" ? "subtitle" : "compact"}
          />
        ) : null}

        {/* Audio */}
        {audioPath && <Audio src={staticFile(audioPath)} />}
      </AbsoluteFill>
    </Transition>
  );
};
