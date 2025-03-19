#!/bin/bash

# Example commands for quick_cut.py
# This script demonstrates the different options available

# Basic usage with minimal options
python quick_cut.py sample_data --output basic_output.mp4

# With transitions and pauses
python quick_cut.py sample_data --output with_transitions_and_pause.mp4 --transition 0.7 --pause 1.5

# With longer pause, no transitions
python quick_cut.py sample_data --output with_long_pause.mp4 --transition 0 --pause 3.0

# With faster narration (speed 1.5x)
python quick_cut.py sample_data --output faster_speech.mp4 --speed 1.5

# With slower narration (speed 0.75x)
python quick_cut.py sample_data --output slower_speech.mp4 --speed 0.75

# With higher resolution (1080p)
python quick_cut.py sample_data --output high_res.mp4 --width 1920 --height 1080

# With smaller resolution (480p) for lower file size
python quick_cut.py sample_data --output lower_res.mp4 --width 854 --height 480

# With burned-in captions (default position at bottom)
python quick_cut.py sample_data --output with_captions.mp4 --burn-captions

# With burned-in captions at the top with larger font
python quick_cut.py sample_data --output captions_top.mp4 --burn-captions --caption-position top --caption-font-size 40

# With custom font for captions (helpful if default font has issues)
python quick_cut.py sample_data --output custom_font.mp4 --burn-captions --caption-font "DejaVu-Sans"

# Generate SRT subtitle file alongside the video
python quick_cut.py sample_data --output with_srt.mp4 --generate-subtitles

# Generate VTT (WebVTT) subtitle file for web videos
python quick_cut.py sample_data --output with_vtt.mp4 --generate-subtitles --subtitle-format vtt

# Generate both burned-in captions and subtitle file
python quick_cut.py sample_data --output with_both.mp4 --burn-captions --generate-subtitles

# For Traditional Chinese (make sure your text files are UTF-8 encoded)
# python quick_cut.py sample_data --output chinese_tw.mp4 --language zh-TW

# For Simplified Chinese with burned-in captions (specify a font that supports Chinese)
# python quick_cut.py sample_data --output chinese_captions.mp4 --language zh-CN --burn-captions --caption-font "Noto Sans SC"

# For Traditional Chinese with burned-in captions and custom font path
# python quick_cut.py sample_data --output chinese_tw_captions.mp4 --language zh-TW --burn-captions --caption-font "/path/to/chinese_font.ttf"

# List all supported languages
# python quick_cut.py --list-languages

# With background music (uncomment to use)
# python quick_cut.py sample_data --output with_music.mp4 --music path/to/your/music.mp3 --music-volume 0.15

# For offline text-to-speech (requires pyttsx3 package)
# python quick_cut.py sample_data --output offline_tts.mp4 --offline-tts

echo "Generated video files: basic_output.mp4, with_transitions_and_pause.mp4, with_long_pause.mp4, faster_speech.mp4, slower_speech.mp4, high_res.mp4, lower_res.mp4, with_captions.mp4, captions_top.mp4, with_srt.mp4, with_vtt.mp4, with_both.mp4"
echo "Optional outputs: chinese_tw.mp4, chinese_captions.mp4, chinese_tw_captions.mp4 (if uncommented)" 