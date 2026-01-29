import { AbsoluteFill, Img, staticFile } from "remotion";
import { whiteboardTheme } from "../../../styles/whiteboard-theme";
import { useWhiteboardAnimations } from "../../../hooks/useWhiteboardAnimations";

/**
 * 开场钩子
 * Duration: 5s
 */
export const Scene1 = () => {
  const { popIn, slideUp, fadeIn, typewriter, float } = useWhiteboardAnimations();

  return (
    <AbsoluteFill style={{
      backgroundColor: whiteboardTheme.colors.background,
      fontFamily: whiteboardTheme.typography.fontFamily.primary,
    }}>
      {/* Narration Text */}
      <div style={{
        position: 'absolute',
        top: whiteboardTheme.video.safeArea.vertical,
        left: whiteboardTheme.video.safeArea.horizontal,
        right: whiteboardTheme.video.safeArea.horizontal,
        fontSize: whiteboardTheme.typography.fontSize.lg,
        color: whiteboardTheme.colors.textPrimary,
        textAlign: 'center',
        lineHeight: whiteboardTheme.typography.lineHeight.relaxed,
        opacity: fadeIn(10),
        transform: `translateY(${slideUp(10, 20)}px)`
      }}>
        {typewriter("你好，这是一个测试视频。", 15)}
      </div>

      {/* Assets */}
      
      <Img
        src={staticFile("assets/generated/test-video/xiaoming_waving.png")}
        style={{
          position: 'absolute',
          top: '50%',
          left: '20%',
          width: '25%',
          transform: `
            translate(-50%, -50%)
            scale(${popIn(15)})
            translateY(${float(0.05 + 0 * 0.01, 10)}px)
          `,
          objectFit: 'contain',
        }}
      />

      <Img
        src={staticFile("assets/generated/test-video/bg_geometry.png")}
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          width: '25%',
          transform: `
            translate(-50%, -50%)
            scale(${popIn(30)})
            translateY(${float(0.05 + 1 * 0.01, 10)}px)
          `,
          objectFit: 'contain',
        }}
      />
    </AbsoluteFill>
  );
};
