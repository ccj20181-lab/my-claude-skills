export interface ScriptMetadata {
  id: string;
  title: string;
  duration: number;
  author?: string;
  createdAt?: string;
  tags?: string[];
}

export interface ScriptAssetRef {
  name: string;
  description: string;
  exists?: boolean;
}

export type SceneType =
  | 'hook'
  | 'title'
  | 'story'
  | 'problem'
  | 'concept'
  | 'metaphor'
  | 'process'
  | 'summary'
  | 'outro';

export interface ScriptScene {
  index: number;
  type: SceneType;
  title: string;
  duration: number;
  narration: string;
  visual?: string;
  assets: ScriptAssetRef[];
}

export interface Script {
  metadata: ScriptMetadata;
  scenes: ScriptScene[];
  rawContent: string;
}

export interface ScriptParseResult {
  success: boolean;
  script?: Script;
  errors?: string[];
}
