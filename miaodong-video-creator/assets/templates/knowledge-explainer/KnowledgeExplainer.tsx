// Knowledge-Explainer Template - 金融小知识科普模板
// 3:4 竖屏 (1080×1440) 专用

import { AbsoluteFill, Img, useCurrentFrame, useVideoConfig, staticFile, interpolate, spring } from "remotion";

// 视频配置
export const VIDEO_WIDTH = 1080;
export const VIDEO_HEIGHT = 1440;
export const VIDEO_FPS = 30;

// 品牌色彩
export const COLORS = {
  primary: "#1a1a2e",      // 深蓝背景
  secondary: "#16213e",    // 次要背景
  accent: "#ffd700",       // 金色强调
  text: "#ffffff",         // 白色文字
  textSecondary: "#e0e0e0", // 次要文字
  highlight: "#6c5ce7",    // 紫色高亮
};

// 字体配置
export const FONTS = {
  title: "64px",
  subtitle: "48px",
  body: "36px",
  small: "28px",
};

// 场景类型
interface Scene {
  id: string;
  image: string;
  startFrame: number;
  durationFrames: number;
  type: "title" | "content" | "summary" | "ending";
  content: {
    mainTitle?: string;
    subTitle?: string;
    text?: string;
    points?: string[];
    highlightWords?: string[];
  };
}

// 示例场景配置
export const defaultScenes: Scene[] = [
  {
    id: "opening",
    image: "scenes/scene_01.png",
    startFrame: 0,
    durationFrames: 150,
    type: "title",
    content: {
      mainTitle: "秒懂金融",
      subTitle: "今天聊聊IPO"
    }
  },
  {
    id: "explanation",
    image: "scenes/scene_02.png",
    startFrame: 150,
    durationFrames: 360,
    type: "content",
    content: {
      text: "IPO就是首次公开募股，是指一家企业第一次将它的股份向公众出售，通俗说就是上市了。",
      highlightWords: ["首次", "公开", "募股", "上市"]
    }
  },
  {
    id: "example",
    image: "scenes/scene_03.png",
    startFrame: 510,
    durationFrames: 450,
    type: "content",
    content: {
      text: "小明开了家烤鸭店，生意火爆开了好几家连锁，想要大干一场，就需要上市融资..."
    }
  },
  {
    id: "keypoints",
    image: "scenes/scene_04.png",
    startFrame: 960,
    durationFrames: 300,
    type: "summary",
    content: {
      points: [
        "IPO = 首次公开募股 = 上市",
        "帮企业融资、扩大规模",
        "股票打新是投资者参与方式"
      ]
    }
  },
  {
    id: "ending",
    image: "scenes/scene_05.png",
    startFrame: 1260,
    durationFrames: 90,
    type: "ending",
    content: {
      text: "关注秒懂金融，每天学点财经知识"
    }
  }
];

// 标题场景组件
export const TitleScene: React.FC<{ scene: Scene; progress: number }> = ({ scene, progress }) => {
  const opacity = interpolate(progress, [0, 0.2], [0, 1], { extrapolateRight: "clamp" });
  const scale = interpolate(progress, [0, 0.3], [0.8, 1], { extrapolateRight: "clamp" });

  return (
    <div
      style={{
        position: "absolute",
        top: "40%",
        left: 0,
        right: 0,
        textAlign: "center",
        opacity,
        transform: `scale(${scale})`,
      }}
    >
      <div
        style={{
          fontSize: FONTS.title,
          fontWeight: "bold",
          color: COLORS.accent,
          marginBottom: 20,
          textShadow: "2px 2px 8px rgba(0,0,0,0.5)",
        }}
      >
        {scene.content.mainTitle}
      </div>
      {scene.content.subTitle && (
        <div
          style={{
            fontSize: FONTS.subtitle,
            color: COLORS.text,
            textShadow: "1px 1px 4px rgba(0,0,0,0.5)",
          }}
        >
          {scene.content.subTitle}
        </div>
      )}
    </div>
  );
};

// 内容场景组件
export const ContentScene: React.FC<{ scene: Scene; progress: number }> = ({ scene, progress }) => {
  const text = scene.content.text || "";
  const charCount = Math.floor(text.length * Math.min(1, progress * 2));
  const displayText = text.substring(0, charCount);

  return (
    <div
      style={{
        position: "absolute",
        bottom: 150,
        left: 60,
        right: 60,
        padding: 30,
        backgroundColor: "rgba(0,0,0,0.7)",
        borderRadius: 20,
        backdropFilter: "blur(10px)",
      }}
    >
      <div
        style={{
          fontSize: FONTS.body,
          color: COLORS.text,
          lineHeight: 1.6,
        }}
      >
        {displayText}
        {charCount < text.length && (
          <span style={{ opacity: 0.5 }}>|</span>
        )}
      </div>
    </div>
  );
};

// 总结场景组件
export const SummaryScene: React.FC<{ scene: Scene; progress: number }> = ({ scene, progress }) => {
  const points = scene.content.points || [];

  return (
    <div
      style={{
        position: "absolute",
        bottom: 150,
        left: 40,
        right: 40,
      }}
    >
      {points.map((point, index) => {
        const pointProgress = interpolate(
          progress,
          [index * 0.25, (index + 1) * 0.25],
          [0, 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        );

        return (
          <div
            key={index}
            style={{
              padding: "20px 30px",
              marginBottom: 15,
              backgroundColor: "rgba(108, 92, 231, 0.9)",
              borderRadius: 15,
              opacity: pointProgress,
              transform: `translateX(${(1 - pointProgress) * 50}px)`,
            }}
          >
            <div
              style={{
                fontSize: FONTS.body,
                color: COLORS.text,
                fontWeight: "bold",
              }}
            >
              {`${index + 1}. ${point}`}
            </div>
          </div>
        );
      })}
    </div>
  );
};

// 结尾场景组件
export const EndingScene: React.FC<{ scene: Scene; progress: number }> = ({ scene, progress }) => {
  const opacity = interpolate(progress, [0, 0.3], [0, 1], { extrapolateRight: "clamp" });
  const scale = interpolate(progress, [0.7, 1], [1, 1.05], { extrapolateLeft: "clamp" });

  return (
    <div
      style={{
        position: "absolute",
        bottom: 200,
        left: 0,
        right: 0,
        textAlign: "center",
        opacity,
        transform: `scale(${scale})`,
      }}
    >
      <div
        style={{
          fontSize: FONTS.subtitle,
          color: COLORS.accent,
          fontWeight: "bold",
          textShadow: "2px 2px 8px rgba(0,0,0,0.5)",
        }}
      >
        {scene.content.text}
      </div>
    </div>
  );
};

// 主视频组件
export const KnowledgeExplainer: React.FC<{ scenes?: Scene[] }> = ({ scenes = defaultScenes }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 查找当前场景
  const currentScene = scenes.find(
    (scene) =>
      frame >= scene.startFrame &&
      frame < scene.startFrame + scene.durationFrames
  ) || scenes[0];

  // 计算场景内进度
  const sceneProgress =
    (frame - currentScene.startFrame) / currentScene.durationFrames;

  // 根据场景类型渲染对应组件
  const renderSceneContent = () => {
    switch (currentScene.type) {
      case "title":
        return <TitleScene scene={currentScene} progress={sceneProgress} />;
      case "content":
        return <ContentScene scene={currentScene} progress={sceneProgress} />;
      case "summary":
        return <SummaryScene scene={currentScene} progress={sceneProgress} />;
      case "ending":
        return <EndingScene scene={currentScene} progress={sceneProgress} />;
      default:
        return <ContentScene scene={currentScene} progress={sceneProgress} />;
    }
  };

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.primary,
      }}
    >
      {/* 背景图片 */}
      <Img
        src={staticFile(currentScene.image)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
        }}
      />

      {/* 场景内容 */}
      {renderSceneContent()}

      {/* 品牌水印 */}
      <div
        style={{
          position: "absolute",
          top: 40,
          right: 40,
          fontSize: FONTS.small,
          color: COLORS.accent,
          opacity: 0.8,
        }}
      >
        秒懂金融
      </div>
    </AbsoluteFill>
  );
};

export default KnowledgeExplainer;
