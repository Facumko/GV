import { Composition } from 'remotion';
import { VideoClip } from './VideoClip';

export const RemotionRoot = () => (
  <Composition
    id="VideoViral"
    component={VideoClip}
    durationInFrames={360}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={{
      audioSrc: '../data/audio_001.mp3',
      timestampsPath: '../data/timestamps_001.json',
    }}
  />
);