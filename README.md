# Quick-Cut Video Generator

A simple Python script to generate videos from text files and images with narration using text-to-speech.

## Features

- Automatically pairs text files with corresponding images
- Multiple TTS (Text-to-Speech) options:
  - Google TTS (online)
  - Microsoft Edge TTS (online, high-quality, optimized for Chinese)
  - pyttsx3 (offline)
- Creates a video slideshow with images and narration
- Optional caption burning to overlay text directly on the video
- Generate SRT or VTT subtitle files for accessibility and embedding
- Handles JPG, JPEG, and PNG images
- Natural sorting of filenames (1.txt, 2.txt, 10.txt, etc.)
- Optional crossfade transitions between slides
- Optional background music with adjustable volume
- Customizable pause duration between narrations
- Multi-language support (including Traditional Chinese, Simplified Chinese, and many others)
- Adjustable speech rate/speed for faster or slower narration
- Customizable video resolution (default: 720p/1280x720)
- Utility options to list supported languages and available fonts

## Requirements

- Python 3.6 or higher
- Internet connection (for Google TTS or Microsoft Edge TTS) or pyttsx3 for offline TTS
- ImageMagick (required only if using the --burn-captions feature)

## Installation

1. Clone this repository or download the script:

   ```
   git clone https://github.com/yourusername/quick-cut.git
   cd quick-cut
   ```

2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Optional: If you want to use offline text-to-speech, install pyttsx3:

   ```
   pip install pyttsx3
   ```

4. Optional: If you want to use caption burning, install ImageMagick:

   - For macOS: `brew install imagemagick`
   - For Ubuntu/Debian: `sudo apt-get install imagemagick`
   - For Windows: Download from [ImageMagick website](https://imagemagick.org/script/download.php)

   After installation, ensure it's in your system PATH.

## Usage

1. Create a directory with your text files and images:

   - Each text file (e.g., `1.txt`, `2.txt`) should contain the caption/narration
   - Each image file (e.g., `1.jpg`, `1.jpeg`, or `1.png`, `2.jpg`, `2.jpeg`, or `2.png`) corresponds to a text file

2. Basic usage:

   ```
   python quick_cut.py /path/to/your/directory
   ```

3. Advanced options:

   ```
   # Specify output path
   python quick_cut.py /path/to/your/directory --output custom_output.mp4

   # Add crossfade transitions (0.7 seconds)
   python quick_cut.py /path/to/your/directory --transition 0.7

   # Add background music
   python quick_cut.py /path/to/your/directory --music /path/to/music.mp3

   # Adjust background music volume (0.0-1.0)
   python quick_cut.py /path/to/your/directory --music /path/to/music.mp3 --music-volume 0.15

   # Disable transitions
   python quick_cut.py /path/to/your/directory --transition 0

   # Use different TTS methods
   python quick_cut.py /path/to/your/directory --tts-method gtts  # Google TTS
   python quick_cut.py /path/to/your/directory --tts-method edge  # Microsoft Edge TTS (default)
   python quick_cut.py /path/to/your/directory --tts-method pyttsx3  # Offline TTS

   # Adjust speech rate using TTS-specific speed control
   python quick_cut.py /path/to/your/directory --tts-speed 1.5  # 50% faster speech

   # Specify a voice for Edge TTS (especially useful for Chinese)
   python quick_cut.py /path/to/your/directory --tts-method edge --tts-voice zh-CN-XiaoxiaoNeural
   python quick_cut.py /path/to/your/directory --tts-method edge --tts-voice zh-TW-HsiaoChenNeural

   # Use offline text-to-speech (requires pyttsx3)
   python quick_cut.py /path/to/your/directory --offline-tts

   # Set pause duration between narrations (2 seconds)
   python quick_cut.py /path/to/your/directory --pause 2.0

   # Use Traditional Chinese for narration
   python quick_cut.py /path/to/your/directory --language zh-TW

   # Speed up the speech (1.5x faster)
   python quick_cut.py /path/to/your/directory --speed 1.5

   # Slow down the speech (0.8x slower)
   python quick_cut.py /path/to/your/directory --speed 0.8

   # Change output resolution to 1080p
   python quick_cut.py /path/to/your/directory --width 1920 --height 1080

   # Create a smaller video (480p)
   python quick_cut.py /path/to/your/directory --width 854 --height 480

   # Burn captions directly onto the video
   python quick_cut.py /path/to/your/directory --burn-captions

   # Customize caption appearance
   python quick_cut.py /path/to/your/directory --burn-captions --caption-font-size 40 --caption-position top

   # Use a specific font for captions (provide a file path or installed font name)
   python quick_cut.py /path/to/your/directory --burn-captions --caption-font "DejaVu-Sans"

   # Generate SRT subtitle file
   python quick_cut.py /path/to/your/directory --generate-subtitles

   # Generate VTT (WebVTT) subtitle file for web videos
   python quick_cut.py /path/to/your/directory --generate-subtitles --subtitle-format vtt

   # List all supported languages
   python quick_cut.py --list-languages

   # List all available fonts for captions
   python quick_cut.py --list-fonts

   # List available voices for Edge TTS
   python quick_cut.py --list-voices
   ```

## Example Directory Structure

```
input_directory/
├── 1.txt
├── 1.jpg (or 1.jpeg or 1.png)
├── 2.txt
├── 2.png (or 2.jpg or 2.jpeg)
├── 3.txt
├── 3.jpg (or 3.jpeg or 3.png)
...
```

## Command-Line Options

| Option                 | Short | Description                                                                          |
| ---------------------- | ----- | ------------------------------------------------------------------------------------ |
| `--output`             | `-o`  | Output video file path (default: output.mp4)                                         |
| `--transition`         | `-t`  | Duration of transition between slides in seconds (default: 0.5, 0 for no transition) |
| `--music`              | `-m`  | Background music file path                                                           |
| `--music-volume`       | `-v`  | Volume of background music from 0.0 to 1.0 (default: 0.1)                            |
| `--offline-tts`        | `-ol` | Use offline text-to-speech (requires pyttsx3)                                        |
| `--pause`              | `-p`  | Duration of pause between narrations in seconds (default: 1.0)                       |
| `--language`           | `-l`  | Language for text-to-speech (default: en)                                            |
| `--speed`              | `-s`  | Speech rate factor (1.0 is normal, 1.5 is 50% faster, 0.75 is 25% slower)            |
| `--width`              | `-w`  | Width of the output video in pixels (default: 1280)                                  |
| `--height`             | `-H`  | Height of the output video in pixels (default: 720)                                  |
| `--burn-captions`      |       | Burn text captions directly onto the video                                           |
| `--caption-font-size`  |       | Font size for burned-in captions (default: 30)                                       |
| `--caption-position`   |       | Position of burned-in captions: top, middle, or bottom (default: bottom)             |
| `--caption-font`       |       | Font name or file path for captions (e.g., "DejaVu-Sans" or "/path/to/font.ttf")     |
| `--generate-subtitles` |       | Generate a subtitle file alongside the video                                         |
| `--subtitle-format`    |       | Format for subtitle file: srt or vtt (default: srt)                                  |
| `--tts-speed`          | `-ts` | TTS speech rate (0.5-2.0, default=1.0)                                               |
| `--tts-method`         | `-tm` | TTS method to use: gtts (Google), edge (Microsoft Edge), pyttsx3 (offline)           |
| `--tts-voice`          | `-tv` | TTS voice to use (available for edge TTS method)                                     |
| `--list-languages`     |       | List all supported languages and exit                                                |
| `--list-fonts`         |       | List all available fonts for caption rendering and exit                              |
| `--list-voices`        |       | List available voices for Edge TTS and exit                                          |

## Standard Video Resolutions

| Name  | Resolution | Command                      |
| ----- | ---------- | ---------------------------- |
| 480p  | 854x480    | `--width 854 --height 480`   |
| 720p  | 1280x720   | (default)                    |
| 1080p | 1920x1080  | `--width 1920 --height 1080` |
| 1440p | 2560x1440  | `--width 2560 --height 1440` |
| 4K    | 3840x2160  | `--width 3840 --height 2160` |

## Supported Languages

The script supports many languages for text-to-speech, including:

- English (en)
- Traditional Chinese (zh-TW)
- Simplified Chinese (zh-CN)
- Japanese (ja)
- Korean (ko)
- French (fr)
- German (de)
- Spanish (es)
- And more...

To view all supported languages, run:

```
python quick_cut.py --list-languages
```

## Notes

- By default, the text-to-speech conversion requires an internet connection as it uses Google's TTS service.
- For offline usage, install pyttsx3 (`pip install pyttsx3`) and use the `--offline-tts` option.
- The caption burning feature requires ImageMagick to be installed. If not installed, the script will create videos without captions.
- For Chinese, Japanese, Korean or other non-Latin scripts, you'll need fonts that support these characters. Consider installing:
  - Noto Sans fonts (`Noto Sans CJK` for Chinese/Japanese/Korean)
  - Arial Unicode MS (comes with Microsoft Office)
  - Use `--caption-font` to specify a full path to a font file that supports your language
- Subtitle files (SRT/VTT) are generated with precise timing based on the actual audio durations.
- The order of slides in the video is determined by the natural sorting of the text file names.
- If a text file doesn't have a matching image file, a warning will be displayed, and it will be skipped.
- The script looks for image files in the order: .jpg, .jpeg, .png
- Background music will loop if shorter than the video duration, or be trimmed if longer.
- Each slide will have silence at the end based on the pause duration to create a natural break between narrations.
- Make sure your text files are saved with UTF-8 encoding for proper handling of non-English characters.
- Adjusting speech speed can help make narration more natural or fit more content into shorter durations.
- Images will be automatically resized to match the specified output resolution while maintaining their aspect ratio.
- Burned-in captions are overlaid with a semi-transparent black background for better readability.
- If captions aren't displaying correctly, try specifying a different font with `--caption-font`.
