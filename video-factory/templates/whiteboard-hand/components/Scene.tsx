import { AbsoluteFill, Img, staticFile, useVideoConfig, useCurrentFrame } from "remotion";
import { whiteboardTheme } from "./whiteboard-theme";
import { useWhiteboardAnimations } from "./Animations";
import React from "react";

export const Scene: React.FC<{
  type: string;
  data: any;
  imagePath: string;
}> = ({ type, data, imagePath }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { popIn, fadeIn, slideUp, float } = useWhiteboardAnimations(frame, fps);

  // Common Container
  const Container = ({ children }: { children: React.ReactNode }) => (
    <AbsoluteFill style={{
      backgroundColor: whiteboardTheme.colors.background,
      fontFamily: whiteboardTheme.typography.fontFamily,
      justifyContent: 'center',
      alignItems: 'center'
    }}>
      {children}
    </AbsoluteFill>
  );

  // Render logic based on type
  if (type === 'title') {
    return (
      <Container>
        <Img
          src={staticFile(imagePath)}
          style={{
            width: 300, height: 300,
            transform: `scale(${popIn(0)}) translateY(${float(0.05)}px)`
          }}
          onError={(e) => {
             console.warn(`Failed to load image: ${imagePath}`);
             (e.target as HTMLImageElement).style.display = 'none';
          }}
        />
        <div style={{
          fontSize: whiteboardTheme.typography.fontSize.title,
          color: whiteboardTheme.colors.primary,
          marginTop: 40,
          opacity: fadeIn(10),
          transform: `translateY(${slideUp(10)}px)`
        }}>
          {data.title}
        </div>
        <div style={{
           fontSize: whiteboardTheme.typography.fontSize.subtitle,
           color: whiteboardTheme.colors.secondary,
           opacity: fadeIn(20)
        }}>
          {data.subtitle}
        </div>
      </Container>
    );
  }

  // Default Content Scene
  return (
    <Container>
      <Img
        src={staticFile(imagePath)}
        style={{
          width: 550, height: 550,
          objectFit: 'contain',
          transform: `scale(${popIn(0)})`
        }}
        onError={(e) => {
             console.warn(`Failed to load image: ${imagePath}`);
             (e.target as HTMLImageElement).style.display = 'none';
        }}
      />
      <div style={{
        position: 'absolute',
        bottom: 200,
        padding: 40,
        backgroundColor: whiteboardTheme.colors.cardBg,
        border: `3px solid ${whiteboardTheme.colors.cardBorder}`,
        borderRadius: 20,
        maxWidth: 800,
        fontSize: whiteboardTheme.typography.fontSize.body,
        opacity: fadeIn(15),
        transform: `translateY(${slideUp(15)}px)`
      }}>
        {data.text || data.points?.join(', ')}
      </div>
    </Container>
  );
};
