export type AssetCategory =
  | 'character'
  | 'icon'
  | 'decoration'
  | 'background'
  | 'object';

export type AssetStatus =
  | 'exists'
  | 'missing'
  | 'generating'
  | 'generated'
  | 'failed';

export type GenerationPriority = 'high' | 'medium' | 'low';

export interface AssetRequirement {
  id: string;
  category: AssetCategory;
  name: string;
  description: string;
  status: AssetStatus;
  existingPath?: string;
  generation?: {
    prompt: string;
    priority: GenerationPriority;
  };
  usedInScenes: string[];
}

export interface AssetManifest {
  videoId: string;
  generatedAt: string;
  totalCount: number;
  existsCount: number;
  missingCount: number;
  assets: AssetRequirement[];
}

export interface AssetGenerationResult {
  assetId: string;
  success: boolean;
  outputPath?: string;
  error?: string;
  duration?: number;
}

export interface GenerationProgress {
  total: number;
  completed: number;
  succeeded: number;
  failed: number;
  current?: string;
}
