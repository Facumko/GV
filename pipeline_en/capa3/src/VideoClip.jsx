import { Audio, useCurrentFrame, useVideoConfig, interpolate } from 'remotion';
import subtitulos from '../../data/timestamps_001.json';

const WINDOW = 4; // palabras visibles a la vez

export const VideoClip = ({ audioSrc }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  // Índice de la palabra actual
  const idxActual = subtitulos.findIndex(
    (p) => t >= p.start && t <= p.end
  );

  // Ventana: centrada en la palabra actual
  const centro = idxActual >= 0 ? idxActual : subtitulos.findIndex(p => t < p.start);
  const inicio = Math.max(0, centro - 1);
  const ventana = subtitulos.slice(inicio, inicio + WINDOW);

  // Fade in al inicio
  const opacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <div style={{
      width: '100%',
      height: '100%',
      background: 'linear-gradient(160deg, #0f0f0f 0%, #1a1a2e 50%, #0f0f0f 100%)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      opacity,
    }}>
      <Audio src={audioSrc} />

      {/* Línea de subtítulos */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'center',
        gap: 12,
        padding: '0 60px',
        maxWidth: '90%',
      }}>
        {ventana.map((p, i) => {
          const esCurrent = inicio + i === idxActual;
          return (
            <span
              key={`${p.start}-${i}`}
              style={{
                fontSize: esCurrent ? 90 : 72,
                fontWeight: 900,
                fontFamily: 'Arial Black, sans-serif',
                textTransform: 'uppercase',
                color: esCurrent ? '#FFE600' : 'rgba(255,255,255,0.5)',
                textShadow: esCurrent
                  ? '0 0 30px rgba(255,230,0,0.6), 2px 2px 0px #000'
                  : '2px 2px 0px #000',
                letterSpacing: 2,
                transition: 'all 0.1s ease',
                transform: esCurrent ? 'scale(1.08)' : 'scale(1)',
                display: 'inline-block',
              }}
            >
              {p.word}
            </span>
          );
        })}
      </div>

      {/* Barra de progreso */}
      <div style={{
        position: 'absolute',
        bottom: 80,
        width: '70%',
        height: 4,
        backgroundColor: 'rgba(255,255,255,0.15)',
        borderRadius: 2,
      }}>
        <div style={{
          height: '100%',
          width: `${(t / (subtitulos[subtitulos.length - 1]?.end || 1)) * 100}%`,
          backgroundColor: '#FFE600',
          borderRadius: 2,
        }} />
      </div>
    </div>
  );
};