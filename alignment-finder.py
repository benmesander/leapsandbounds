#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculates the pattern of long ('L') and short ('S') audio segments 
required to periodically align with video segments in a media manifest.

This tool is designed for multimedia software developers working with
streaming protocols like DASH, where audio and video segments may have
slightly different durations, leading to drift over time. This program
determines the optimal sequence of audio segments to ensure periodic,
perfect synchronization with the video timeline.

All time-based calculations are performed using rational numbers to
avoid floating-point inaccuracies.

Example Usage:
python3 find_alignment_pattern.py 30000/1001 30 48000 1024
"""

import argparse
import math
import sys
from fractions import Fraction


def parse_rational(value_str: str) -> Fraction:
    """
    Parses a string representation of a number into a Fraction.
    The string can be an integer (e.g., '30') or a fraction (e.g., '30000/1001').

    Args:
        value_str: The string to parse.

    Returns:
        A Fraction object representing the number.
    """
    if '/' in value_str:
        try:
            numerator, denominator = value_str.split('/', 1)
            return Fraction(int(numerator), int(denominator))
        except (ValueError, ZeroDivisionError) as e:
            raise argparse.ArgumentTypeError(f"Invalid fraction '{value_str}': {e}")
    try:
        return Fraction(int(value_str))
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid integer value: '{value_str}'")

# ---

def calculate_durations(
    video_frame_rate: Fraction,
    video_frames_per_segment: int,
    audio_sample_rate: int,
    audio_samples_per_block: int
) -> tuple[Fraction, Fraction, Fraction]:
    """
    Calculates the durations of video, short audio, and long audio segments.

    Args:
        video_frame_rate: The video frame rate as a Fraction.
        video_frames_per_segment: The number of frames in a video segment.
        audio_sample_rate: The audio sample rate in Hz.
        audio_samples_per_block: The number of samples per audio codec block.

    Returns:
        A tuple containing the video segment length, the short audio segment
        length, and the long audio segment length, all as Fraction objects.
    """
    if not video_frame_rate or not audio_sample_rate:
        raise ValueError("Frame rate and sample rate must be non-zero.")

    # Duration (seconds) = Frames / (Frames / Second)
    video_segment_len = Fraction(video_frames_per_segment) / video_frame_rate

    # Duration (seconds) = Samples / (Samples / Second)
    audio_block_len = Fraction(audio_samples_per_block, audio_sample_rate)

    if not audio_block_len:
         raise ValueError("Audio block duration cannot be zero. Check sample rate and block size.")

    # Determine the number of audio blocks that fit into one video segment
    num_blocks_rational = video_segment_len / audio_block_len

    # The short segment has a block count rounded down, the long one rounded up
    audio_short_segment_blocks = math.floor(num_blocks_rational)
    audio_long_segment_blocks = math.ceil(num_blocks_rational)
    
    # Calculate the final audio segment durations
    audio_short_segment_len = audio_short_segment_blocks * audio_block_len
    audio_long_segment_len = audio_long_segment_blocks * audio_block_len

    return video_segment_len, audio_short_segment_len, audio_long_segment_len

# ---

def find_alignment_pattern(
    video_seg_len: Fraction,
    audio_short_seg_len: Fraction,
    audio_long_seg_len: Fraction
) -> str:
    """
    Simulates a media timeline to find the audio segment pattern that
    eventually aligns perfectly with the video timeline.

    Args:
        video_seg_len: The duration of a single video segment.
        audio_short_seg_len: The duration of a "short" audio segment.
        audio_long_seg_len: The duration of a "long" audio segment.

    Returns:
        A string pattern of 'L' and 'S' characters representing the sequence.
    """
    # Handle the edge case where audio and video segments can align perfectly
    # from the start. In this case, floor() and ceil() produce the same value.
    if audio_short_seg_len == audio_long_seg_len:
        if audio_short_seg_len == video_seg_len:
            print(
                "Note: Audio segment duration can perfectly match video segment duration.",
                file=sys.stderr
            )
            # The pattern is trivial; one segment aligns perfectly.
            # We choose 'L' by convention as it's selected in a tie-break.
            return "L"
        # If they are equal but not equal to video, the logic proceeds normally.

    video_time = Fraction(0)
    audio_time = Fraction(0)
    pattern = []
    
    # A practical limit to prevent accidental infinite loops. The alignment
    # is mathematically guaranteed, but this is a safeguard.
    MAX_ITERATIONS = 5_000_000 

    for _ in range(MAX_ITERATIONS):
        # Advance the video timeline by one segment
        video_time += video_seg_len
        
        # Calculate the error if we choose the long audio segment vs. the short one
        # Error is defined as (video_time - next_audio_time)
        next_audio_time_long = audio_time + audio_long_seg_len
        error_long = video_time - next_audio_time_long

        next_audio_time_short = audio_time + audio_short_seg_len
        error_short = video_time - next_audio_time_short

        # Choose the segment type that minimizes the absolute error.
        # In case of a tie, we prefer the long segment ('L').
        if abs(error_long) <= abs(error_short):
            audio_time = next_audio_time_long
            pattern.append('L')
        else:
            audio_time = next_audio_time_short
            pattern.append('S')
            
        # If the timelines have converged, the pattern is complete
        if video_time == audio_time:
            return "".join(pattern)
    
    raise RuntimeError(f"Alignment not found within {MAX_ITERATIONS} iterations.")

# ---

def main():
    """
    Main entry point for the script. Parses command-line arguments,
    runs the calculation, and prints the resulting pattern.
    """
    parser = argparse.ArgumentParser(
        description="Calculate the audio segment alignment pattern for a DASH manifest.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "video_frame_rate",
        type=parse_rational,
        help="Video frame rate, e.g., '30' or '30000/1001'."
    )
    parser.add_argument(
        "video_frames_per_segment",
        type=int,
        help="Number of video frames per segment, e.g., '60'."
    )
    parser.add_argument(
        "audio_sample_rate",
        type=int,
        help="Audio sample rate in Hz, e.g., '48000'."
    )
    parser.add_argument(
        "audio_samples_per_block",
        type=int,
        help="Number of audio samples per codec block, e.g., '1024' for AAC."
    )
    
    args = parser.parse_args()
    
    try:
        vid_len, audio_s_len, audio_l_len = calculate_durations(
            args.video_frame_rate,
            args.video_frames_per_segment,
            args.audio_sample_rate,
            args.audio_samples_per_block
        )
        
        pattern = find_alignment_pattern(vid_len, audio_s_len, audio_l_len)
        print(pattern)
        
    except (ValueError, RuntimeError, argparse.ArgumentTypeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
    
