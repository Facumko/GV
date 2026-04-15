import { Composition } from 'remotion';
import { VideoClip } from './VideoClip';

// FIX: audioSrc debe ser una ruta que Remotion pueda resolver.
// Remotion sirve archivos desde la carpeta `public/` del proyecto.
// Copiá audio_001.mp3 a pipeline_es/capa3/public/audio_001.mp3
// y el render script en package.json ya lo referencia bien.
export const RemotionRoot = () => (
  <Composition
    id="VideoViral"
    component={VideoClip}
    durationInFrames={360}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={{
      audioSrc: 'audio_001.mp3',   // Remotion busca en /public/ automáticamente
    }}
  />
);