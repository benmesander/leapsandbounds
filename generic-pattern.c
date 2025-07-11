#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

// Example:
// ./generic-pattern 1001 86400 48000 1024 LLLLLLLLLLLLS >output

int main(int argc, char **argv)
{
  if (argc != 6) {
    fprintf(stderr, "usage: %s video-segment-len-ms num-segments audio-sample-rate audio-samples-per-block pattern\nwhere pattern is of the form LLLLLLLLLLLLS (long and short audio segments)\n",
	    argv[0]);
    exit(1);
  }

  const unsigned video_len_ms = atoi(argv[1]);
  const unsigned num_segments = atoi(argv[2]);
  const unsigned audio_sample_rate = atoi(argv[3]);
  const unsigned audio_samples_per_block = atoi(argv[4]);
  const char *pattern = argv[5];

  const double audio_len_ms = (double)audio_samples_per_block / (double)audio_sample_rate * 1000.0;
  const double short_segment_blocks = floor((double)video_len_ms / audio_len_ms);
  const double long_segment_blocks = ceil((double)video_len_ms / audio_len_ms);
  const double audio_short_len_ms = short_segment_blocks * audio_samples_per_block / audio_sample_rate * 1000.0;
  const double audio_long_len_ms = long_segment_blocks *  audio_samples_per_block / audio_sample_rate * 1000.0;
  
  printf("video segment length (ms): %u\t\t\tnumber of segments: %u\n", video_len_ms, num_segments);
  printf("audio sample rate: %u\t\t\taudio samples per block: %u\n", audio_sample_rate, audio_samples_per_block);
  printf("number of audio blocks in short segment: %u\tin long segment: %u\n",
	 (unsigned)short_segment_blocks, (unsigned)long_segment_blocks);
  printf("duration of short audio segment (ms): %f\nduration of long segment (ms): %f\n",
	 audio_short_len_ms, audio_long_len_ms);
  printf("pattern of long/short audio segments: %s\n", pattern);
  printf("================================================================================\n");

  const unsigned patternlen = strlen(pattern);
  unsigned video_time_ms = 0;
  double audio_time_ms = 0;
  double audio_dur_ms = 0;

  for (int i=0; i < num_segments; i++) {
    video_time_ms += video_len_ms;

    switch (pattern[i % patternlen]) {
    case 'L':
      audio_dur_ms = audio_long_len_ms;
      break;
    case 'S':
      audio_dur_ms = audio_short_len_ms;
      break;
    default:
      fprintf(stderr, "invalid character in pattern: %s\n", pattern);
      exit(1);
    }
    audio_time_ms += audio_dur_ms;

    printf("v: %u %u a: %f %f v-a: %f\n", video_time_ms, video_len_ms, audio_time_ms, audio_dur_ms, video_time_ms - audio_time_ms);

  }



  exit(0);


#if 0
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
#endif
  exit(0);
}
