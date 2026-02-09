/**
 * 秒懂金融视频 - 场景类型定义
 */

export interface SceneMeta {
  topic: string;
  title: string;
  fps: number;
  width: number;
  height: number;
}

export interface AudioInfo {
  path: string;
  duration_ms: number;
  word_timestamps?: WordTimestamp[] | null;
}

export interface WordTimestamp {
  word: string;
  start_ms: number;
  end_ms: number;
}

export interface CharacterInfo {
  type: string;
  path: string | null;
}

export interface IconInfo {
  name: string;
  path: string | null;
}

export interface Scene {
  id: string;
  type: SceneType;
  text: string;
  duration: number;
  character: CharacterInfo;
  icon: IconInfo | null;
  extra_icons?: IconInfo[];
  audio?: AudioInfo;
}

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

export interface VideoData {
  meta: SceneMeta;
  scenes: Scene[];
  audio: {
    files: Record<string, AudioInfo>;
    total_duration_ms: number;
  } | null;
}

// Scene type styling configurations
export const SCENE_STYLES: Record<SceneType, {
  backgroundColor: string;
  accentColor: string;
  textSize: number;
}> = {
  hook: {
    backgroundColor: "#FFFDF7",
    accentColor: "#FF6B35",
    textSize: 48,
  },
  title: {
    backgroundColor: "#FFFFFF",
    accentColor: "#2D3748",
    textSize: 64,
  },
  question: {
    backgroundColor: "#FFF5F5",
    accentColor: "#E53E3E",
    textSize: 44,
  },
  explain: {
    backgroundColor: "#FFFFFF",
    accentColor: "#3182CE",
    textSize: 40,
  },
  analogy: {
    backgroundColor: "#F0FFF4",
    accentColor: "#38A169",
    textSize: 42,
  },
  example: {
    backgroundColor: "#FFFFF0",
    accentColor: "#D69E2E",
    textSize: 40,
  },
  comparison: {
    backgroundColor: "#FAF5FF",
    accentColor: "#805AD5",
    textSize: 40,
  },
  summary: {
    backgroundColor: "#EBF8FF",
    accentColor: "#2B6CB0",
    textSize: 44,
  },
  cta: {
    backgroundColor: "#FFF5F7",
    accentColor: "#D53F8C",
    textSize: 48,
  },
};
