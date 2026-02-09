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
import { HostAvatar } from "./HostAvatar";
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

    // Title scenes get a centered icon; others get a larger hero.
    const isTitle = data.type === "title";
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
          top: data.type === "hook" ? 330 : 320,
          transform: `translateX(-50%) translateY(${float}px) rotate(${(1 - scale) * -7}deg) scale(${(0.9 + scale * 0.14) * breathe})`,
          width: data.type === "hook" || data.type === "cta" ? 700 : 640,
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
    data.type === "question" ? "slideUp" :
    data.type === "comparison" ? "wipe" :
    data.type === "cta" ? "slideLeft" :
    "fade";

  const extraIcons = (data.extra_icons || []).filter((i) => i?.path);

  const showTitleLayout = data.type === "title";

  const driftX = Math.sin(frame / 140) * 6;
  const driftY = Math.cos(frame / 160) * 5;

  return (
    <Transition type={transitionType as any} duration={12}>
      <AbsoluteFill
        style={{
          backgroundColor: sceneStyle.backgroundColor,
        }}
      >
        {/* Background pattern for whiteboard effect */}
        <div
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
        />

        {/* Branding (logo + watermark) */}
        <Branding />

        {/* Large low-opacity icon backdrop to increase material presence */}
        {renderBackdropIcon()}

        {/* Icon cloud (aux visuals) */}
        <IconCloud sceneType={data.type} icons={extraIcons} />

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

        {/* Hand-drawn emphasis for key scenes */}
        {data.type === "hook" || data.type === "summary" ? (
          <div style={{ position: "absolute", left: "50%", top: 330, transform: "translateX(-50%)" }}>
            <HandDraw type="circle" color={sceneStyle.accentColor} strokeWidth={6} duration={22} />
          </div>
        ) : null}

        {/* Host avatar */}
        <HostAvatar
          emotion={data.character?.type}
          position={data.type === "cta" ? "bottom-right" : "bottom-left"}
          size={260}
        />

        {/* Title scene text */}
        {showTitleLayout ? (
          <div style={{ position: "absolute", left: 0, right: 0, top: 180 }}>
            <TitleText title={meta.title} subtitle={data.text} />
          </div>
        ) : null}

        {/* Subtitle (single source of text to avoid duplicates) */}
        {!showTitleLayout && showSubtitle ? (
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
