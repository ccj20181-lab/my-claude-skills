/**
 * 财经视频AI - 简化的场景类型定义
 * 完全依赖AI生成的插画，无火柴人组件
 */

export interface SceneMeta {
  topic: string;
  title: string;
  fps: number;
  width: number;
  height: number;
}

export interface BookOutro {
  enabled: boolean;
  image: string;
  text: string;
  duration: number;
}

export interface WordTimestamp {
  word: string;
  start_ms: number;
  end_ms: number;
}

export interface AudioInfo {
  path: string;
  duration_ms: number;
  word_timestamps?: WordTimestamp[] | null;
}

export type VisualAction =
  | "circle"
  | "underline"
  | "arrow"
  | "checkmark"
  | "highlight"
  | "none";

export type SceneType =
  | "hook"
  | "title"
  | "question"
  | "explain"
  | "analogy"
  | "example"
  | "comparison"
  | "summary"
  | "cta";

export interface Scene {
  id: string;
  type: SceneType;
  text: string;
  duration: number;
  // AI生成的插画路径
  image: string;
  // 可选的手绘动画效果
  visual_action?: VisualAction;
  // 音频信息
  audio?: AudioInfo;
}

export interface VideoData {
  meta: SceneMeta;
  scenes: Scene[];
  audio: {
    files: Record<string, AudioInfo>;
    total_duration_ms: number;
  } | null;
  book_outro?: BookOutro;
}

// 场景类型对应的转场效果
export const SCENE_TRANSITIONS: Record<SceneType, string> = {
  hook: "zoom",
  title: "scaleFromCenter",
  question: "slideUp",
  explain: "fade",
  analogy: "slideRight",
  example: "slideLeft",
  comparison: "wipe",
  summary: "slideDown",
  cta: "scaleFromCenter",
};
