import { Audio, useCurrentFrame, useVideoConfig } from 'remotion';
import subtitulos from '../../data/timestamps_001.json';

export const VideoClip = ({ audioSrc }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const tiempoActual = frame / fps;

  const palabraActual = subtitulos.find(
    (p) => tiempoActual >= p.start && tiempoActual <= p.end
  );

  return (
    <div style={{
      width: '100%', height: '100%',
      backgroundColor: '#000',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
    }}>
      <Audio src={audioSrc} />
      <h1 style={{
        color: 'white', fontSize: 80, textAlign: 'center',
        padding: 40, textTransform: 'uppercase',
      }}>
        {palabraActual ? palabraActual.word : ''}
      </h1>
    </div>
  );
};