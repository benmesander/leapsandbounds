#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define VIDEO_FRAMERATE_NUMERATOR 30000
#define VIDEO_FRAMERATE_DENOMINATOR 1001
#define VIDEO_SEGMENT_LENGTH 1.001
#define VIDEO_SEGMENT_LENGTH_MS 1001
#define VIDEO_GOP_LENGTH 30

#define AUDIO_SAMPLE_RATE 48000
#define AUDIO_BLOCK_LEN 1024

int main(int argc, char **argv)
{
  const int duration = 86400; // seconds

    /* audio block length */
  double audio_blklen_ms = (double)AUDIO_BLOCK_LEN / AUDIO_SAMPLE_RATE * 1000;

  printf("audio_blklen_ms %f\n", audio_blklen_ms);

  /* short & long audio segments */

  double short_segment_blocks = floor((double)VIDEO_SEGMENT_LENGTH_MS / audio_blklen_ms);
  double long_segment_blocks = ceil((double)VIDEO_SEGMENT_LENGTH_MS / audio_blklen_ms);

  printf ("short %f long %f\n", short_segment_blocks, long_segment_blocks);

  double audio_short_len_ms = short_segment_blocks * AUDIO_BLOCK_LEN / AUDIO_SAMPLE_RATE * 1000;
  double audio_long_len_ms = long_segment_blocks * AUDIO_BLOCK_LEN / AUDIO_SAMPLE_RATE * 1000;

  printf ("short len %f long len %f\n", audio_short_len_ms, audio_long_len_ms);


  unsigned video_time_ms = 0;
  unsigned video_dur_ms = VIDEO_SEGMENT_LENGTH_MS;
  double audio_time_ms = 0;
  double audio_dur_ms = 0;

  for (int i = 0; i < duration; i++) {
    video_time_ms += video_dur_ms;
    if (i % 13) {  // pattern: 12 long, 1 short
      audio_dur_ms = audio_long_len_ms;
    } else {
      audio_dur_ms = audio_short_len_ms;
    }
    audio_time_ms += audio_dur_ms;
    printf("v: %u %u a: %f %f d: %f\n", video_time_ms, video_dur_ms, audio_time_ms, audio_dur_ms, video_time_ms - audio_time_ms);
  }

  exit(0);
}
