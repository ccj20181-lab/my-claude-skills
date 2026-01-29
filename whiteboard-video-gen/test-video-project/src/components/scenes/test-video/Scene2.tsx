import { AbsoluteFill, Img, staticFile } from "remotion";
import { whiteboardTheme } from "../../../styles/whiteboard-theme";
import { useWhiteboardAnimations } from "../../../hooks/useWhiteboardAnimations";

/**
 * 概念解释
 * Duration: 5s
 */
export const Scene2 = () => {
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
        {typewriter("我们正在测试自动化生成流程。", 15)}
      </div>

      {/* Assets */}
      
      <Img
        src={staticFile("assets/generated/test-video/robot_painting.png")}
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
    </AbsoluteFill>
  );
};
