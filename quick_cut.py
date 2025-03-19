#!/usr/bin/env python3
import os
import glob
import re
from gtts import gTTS
from moviepy.editor import *
import argparse
import tempfile
import subprocess
import sys
import time  # Add time module for timing functionality
import asyncio  # For EdgeTTS

# Add EdgeTTS import
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

# Add PIL/Pillow compatibility patch for newer versions
try:
    from PIL import Image
    if not hasattr(Image, 'ANTIALIAS'):
        # For Pillow >= 9.0.0
        Image.ANTIALIAS = Image.Resampling.LANCZOS
except (ImportError, AttributeError):
    pass

# Check if ImageMagick is installed (needed for TextClip)
def is_imagemagick_installed():
    """Check if ImageMagick is installed and available in the path"""
    try:
        # Try to run 'convert -version' (ImageMagick command)
        result = subprocess.run(
            ['convert', '-version'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return 'ImageMagick' in result.stdout
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

IMAGEMAGICK_AVAILABLE = is_imagemagick_installed()

# For offline TTS
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

# Supported languages dictionary with description
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'zh-TW': 'Traditional Chinese',
    'zh-CN': 'Simplified Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'fr': 'French',
    'de': 'German',
    'es': 'Spanish',
    'it': 'Italian',
    'ru': 'Russian',
    'pt': 'Portuguese',
    'th': 'Thai',
    'vi': 'Vietnamese'
}

# EdgeTTS voice options for various languages
EDGE_TTS_VOICES = {
    'zh-TW': ['zh-TW-HsiaoChenNeural', 'zh-TW-YunJheNeural', 'zh-TW-HsiaoYuNeural'],
    'zh-CN': ['zh-CN-XiaoxiaoNeural', 'zh-CN-YunxiNeural', 'zh-CN-YunyangNeural', 'zh-CN-XiaohanNeural', 'zh-CN-XiaomoNeural'],
    'en': ['en-US-AriaNeural', 'en-US-GuyNeural', 'en-GB-SoniaNeural'],
    'ja': ['ja-JP-NanamiNeural', 'ja-JP-KeitaNeural'],
    'ko': ['ko-KR-SoonBokNeural', 'ko-KR-InJoonNeural'],
    'fr': ['fr-FR-DeniseNeural', 'fr-FR-HenriNeural'],
    'de': ['de-DE-KatjaNeural', 'de-DE-ConradNeural'],
    'es': ['es-ES-AlvaroNeural', 'es-ES-ElviraNeural'],
    'it': ['it-IT-ElsaNeural', 'it-IT-DiegoNeural'],
    'ru': ['ru-RU-SvetlanaNeural', 'ru-RU-DmitryNeural'],
    'pt': ['pt-BR-FranciscaNeural', 'pt-BR-AntonioNeural'],
    'th': ['th-TH-PremwadeeNeural', 'th-TH-NiwatNeural'],
    'vi': ['vi-VN-HoaiMyNeural', 'vi-VN-NamMinhNeural']
}

# Language-specific font recommendations
LANGUAGE_FONTS = {
    # CJK fonts (Chinese, Japanese, Korean)
    'zh-TW': ['Noto Sans TC', 'Microsoft JhengHei', 'SimSun', 'Arial Unicode MS'],
    'zh-CN': ['Noto Sans SC', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS'],
    'ja': ['Noto Sans JP', 'MS Gothic', 'Meiryo', 'Arial Unicode MS'],
    'ko': ['Noto Sans KR', 'Malgun Gothic', 'Gulim', 'Arial Unicode MS'],
    # Cyrillic
    'ru': ['Noto Sans', 'Arial', 'DejaVu Sans'],
    # Thai
    'th': ['Noto Sans Thai', 'Tahoma', 'Arial Unicode MS'],
    # Default Latin script fonts
    'default': ['Arial', 'DejaVu-Sans', 'Verdana', 'Helvetica', None]
}

def natural_sort_key(s):
    """Sort strings containing numbers naturally"""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]

def get_file_pairs(directory):
    """Find all text files and their corresponding images in the directory"""
    text_files = sorted(glob.glob(os.path.join(directory, "*.txt")), key=natural_sort_key)
    pairs = []
    
    for text_file in text_files:
        basename = os.path.splitext(os.path.basename(text_file))[0]
        # Look for corresponding image (jpg, jpeg, or png)
        jpg_file = os.path.join(directory, f"{basename}.jpg")
        jpeg_file = os.path.join(directory, f"{basename}.jpeg")
        png_file = os.path.join(directory, f"{basename}.png")
        
        if os.path.exists(jpg_file):
            pairs.append((text_file, jpg_file))
        elif os.path.exists(jpeg_file):
            pairs.append((text_file, jpeg_file))
        elif os.path.exists(png_file):
            pairs.append((text_file, png_file))
        else:
            print(f"Warning: No matching image found for {text_file}")
    
    return pairs

def text_to_speech_gtts(text, output_file, lang='en', speed_factor=1.0):
    """Convert text to speech using Google TTS and save as audio file"""
    try:
        # Use a temporary file if we need to adjust speed
        temp_file = None
        if speed_factor != 1.0:
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False).name
            target_file = temp_file
        else:
            target_file = output_file
            
        # Generate the speech
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(target_file)
        
        # Apply speed adjustment if needed
        if speed_factor != 1.0:
            # Load the audio to adjust its speed
            audio = AudioFileClip(temp_file)
            # Apply speed effect (speedx)
            audio_sped = audio.fx(vfx.speedx, speed_factor)
            # Save to the final output file
            audio_sped.write_audiofile(output_file, verbose=False, logger=None)
            # Clean up the temporary file
            audio.close()
            audio_sped.close()
            os.remove(temp_file)
            
        return output_file
    except Exception as e:
        print(f"Error generating speech for language '{lang}': {e}")
        print("Falling back to English...")
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_file)
        return output_file

def text_to_speech_pyttsx3(text, output_file, lang='en', speed_factor=1.0):
    """Convert text to speech using pyttsx3 (offline) and save as audio file"""
    engine = pyttsx3.init()
    
    # Get temporary WAV file path
    temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name
    
    # Configure the voice (optional adjustments)
    # Default rate is typically around 200 words per minute
    base_rate = 150  # Slightly slower than default
    adjusted_rate = int(base_rate * speed_factor)
    engine.setProperty('rate', adjusted_rate)    # Speed of speech
    engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
    
    print(f"  Using speech rate: {adjusted_rate} (speed factor: {speed_factor})")
    
    # Try to set a voice for the selected language (pyttsx3 has limited language support)
    voices = engine.getProperty('voices')
    if lang != 'en':
        print(f"  Trying to find a voice for language '{lang}'")
        # Try to find a voice for the selected language
        for voice in voices:
            if lang in voice.id.lower() or lang.split('-')[0] in voice.id.lower():
                engine.setProperty('voice', voice.id)
                break
        else:
            print(f"Warning: Could not find a voice for language '{lang}'. Using default voice.")
    
    # Save to WAV file first
    engine.save_to_file(text, temp_wav)
    engine.runAndWait()
    
    # Convert WAV to MP3 using moviepy
    audio = AudioFileClip(temp_wav)
    audio.write_audiofile(output_file, verbose=False, logger=None)
    
    # Clean up temporary file
    os.remove(temp_wav)
    
    return output_file

async def text_to_speech_edge_async(text, output_file, lang='en', voice=None, speed_factor=1.0):
    """Convert text to speech using Microsoft Edge TTS and save as audio file"""
    try:
        # Set default voice based on language if not specified
        if voice is None:
            if lang in EDGE_TTS_VOICES and len(EDGE_TTS_VOICES[lang]) > 0:
                voice = EDGE_TTS_VOICES[lang][0]  # Use first available voice for the language
            else:
                # Fallback to English if the language is not supported
                print(f"Language '{lang}' not found in EdgeTTS voices, falling back to English")
                voice = "en-US-AriaNeural"
        
        # Calculate rate string based on speed factor
        # EdgeTTS accepts rate values with sign: +0%, +50%, -50% etc.
        if speed_factor > 1.0:
            rate = f"+{int((speed_factor-1)*100)}%"
        elif speed_factor < 1.0:
            rate = f"-{int((1-speed_factor)*100)}%"
        else:
            rate = "+0%"
        
        print(f"  Using EdgeTTS voice: {voice}, rate: {rate}")
        
        # Create TTS communicator with the selected voice and speech rate
        tts = edge_tts.Communicate(text, voice, rate=rate)
        
        # Generate and save audio
        await tts.save(output_file)
        
        return output_file
    except Exception as e:
        print(f"Error generating speech with Edge TTS: {e}")
        print("Falling back to Google TTS...")
        return text_to_speech_gtts(text, output_file, lang, speed_factor)

def text_to_speech_edge(text, output_file, lang='en', voice=None, speed_factor=1.0):
    """Synchronous wrapper for Edge TTS"""
    return asyncio.run(text_to_speech_edge_async(text, output_file, lang, voice, speed_factor))

def text_to_speech(text, output_file, method='gtts', offline=False, lang='en', voice=None, speed_factor=1.0):
    """Convert text to speech using the selected method"""
    if method == 'edge' and EDGE_TTS_AVAILABLE:
        return text_to_speech_edge(text, output_file, lang, voice, speed_factor)
    elif method == 'pyttsx3' and PYTTSX3_AVAILABLE:
        return text_to_speech_pyttsx3(text, output_file, lang, speed_factor)
    elif method == 'gtts' or method not in ['edge', 'pyttsx3']:
        if method not in ['gtts', 'edge', 'pyttsx3']:
            print(f"Warning: Unknown TTS method '{method}'. Using Google TTS instead.")
        if offline and PYTTSX3_AVAILABLE:
            print("Offline mode requested. Using pyttsx3.")
            return text_to_speech_pyttsx3(text, output_file, lang, speed_factor)
        else:
            if offline and not PYTTSX3_AVAILABLE:
                print("Warning: Offline TTS requested but pyttsx3 not available. Using Google TTS instead.")
                print("To enable offline TTS, install pyttsx3: pip install pyttsx3")
            return text_to_speech_gtts(text, output_file, lang, speed_factor)

def format_timestamp_srt(seconds):
    """Convert seconds to SRT timestamp format: HH:MM:SS,mmm"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{milliseconds:03d}"

def format_timestamp_vtt(seconds):
    """Convert seconds to VTT timestamp format: HH:MM:SS.mmm"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}.{milliseconds:03d}"

def create_subtitle_file(file_pairs, output_path, pause_duration=1.0, format='srt'):
    """Generate a subtitle file (SRT or VTT) from the text files and timing information"""
    if format not in ['srt', 'vtt']:
        raise ValueError(f"Unsupported subtitle format: {format}")
    
    # Calculate base name for subtitle file
    base_name = os.path.splitext(output_path)[0]
    subtitle_path = f"{base_name}.{format}"
    
    # Determine the timestamp formatting function
    timestamp_formatter = format_timestamp_srt if format == 'srt' else format_timestamp_vtt
    
    # Calculate timing for each slide
    current_time = 0
    subtitle_items = []
    
    for i, (text_file, _) in enumerate(file_pairs):
        # Read caption
        with open(text_file, 'r', encoding='utf-8') as f:
            caption = f.read().strip()
        
        # Estimate audio duration based on text length (more accurate if the files are already processed)
        # For now, estimate ~0.3 seconds per word (rough estimate)
        words = caption.split()
        estimated_duration = max(len(words) * 0.3, 1.0)  # At least 1 second
        
        start_time = current_time
        end_time = start_time + estimated_duration
        
        # Add to subtitle list with index (for SRT)
        subtitle_items.append((i + 1, start_time, end_time, caption))
        
        # Update current time for next subtitle
        current_time = end_time + pause_duration
    
    # Write the subtitle file
    with open(subtitle_path, 'w', encoding='utf-8') as f:
        # Write header for VTT
        if format == 'vtt':
            f.write("WEBVTT\n\n")
        
        # Write each subtitle entry
        for index, start_time, end_time, text in subtitle_items:
            if format == 'srt':
                # SRT format: index, timestamp range, text, blank line
                f.write(f"{index}\n")
                f.write(f"{timestamp_formatter(start_time)} --> {timestamp_formatter(end_time)}\n")
                f.write(f"{text}\n\n")
            else:
                # VTT format: timestamp range, text, blank line
                f.write(f"{timestamp_formatter(start_time)} --> {timestamp_formatter(end_time)}\n")
                f.write(f"{text}\n\n")
    
    print(f"Subtitle file created: {subtitle_path}")
    return subtitle_path

def create_subtitle_file_from_audio(file_pairs, output_path, pause_duration=1.0, format='srt', 
                                   offline_tts=False, lang='en', speed_factor=1.0):
    """Generate a subtitle file with more accurate timing based on actual audio durations"""
    if format not in ['srt', 'vtt']:
        raise ValueError(f"Unsupported subtitle format: {format}")
    
    # Calculate base name for subtitle file
    base_name = os.path.splitext(output_path)[0]
    subtitle_path = f"{base_name}.{format}"
    
    # Determine the timestamp formatting function
    timestamp_formatter = format_timestamp_srt if format == 'srt' else format_timestamp_vtt
    
    # Create temp directory for test audio files
    temp_dir = os.path.join(os.path.dirname(output_path) or ".", "temp_subtitle_audio")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Calculate timing for each slide based on actual audio durations
    current_time = 0
    subtitle_items = []
    
    try:
        for i, (text_file, _) in enumerate(file_pairs):
            # Read caption
            with open(text_file, 'r', encoding='utf-8') as f:
                caption = f.read().strip()
            
            # Generate audio to get accurate duration
            audio_file = os.path.join(temp_dir, f"audio_sub_{i}.mp3")
            text_to_speech(caption, audio_file, offline=offline_tts, lang=lang, speed_factor=speed_factor)
            
            # Get actual audio duration
            audio_clip = AudioFileClip(audio_file)
            audio_duration = audio_clip.duration
            audio_clip.close()
            
            # Set start and end times
            start_time = current_time
            end_time = start_time + audio_duration
            
            # Add to subtitle list with index (for SRT)
            subtitle_items.append((i + 1, start_time, end_time, caption))
            
            # Update current time for next subtitle
            current_time = end_time + pause_duration
    
        # Write the subtitle file
        with open(subtitle_path, 'w', encoding='utf-8') as f:
            # Write header for VTT
            if format == 'vtt':
                f.write("WEBVTT\n\n")
            
            # Write each subtitle entry
            for index, start_time, end_time, text in subtitle_items:
                if format == 'srt':
                    # SRT format: index, timestamp range, text, blank line
                    f.write(f"{index}\n")
                    f.write(f"{timestamp_formatter(start_time)} --> {timestamp_formatter(end_time)}\n")
                    f.write(f"{text}\n\n")
                else:
                    # VTT format: timestamp range, text, blank line
                    f.write(f"{timestamp_formatter(start_time)} --> {timestamp_formatter(end_time)}\n")
                    f.write(f"{text}\n\n")
        
        print(f"Subtitle file created with accurate timing: {subtitle_path}")
    finally:
        # Clean up temp directory
        for file in os.listdir(temp_dir):
            try:
                os.remove(os.path.join(temp_dir, file))
            except:
                pass
        try:
            os.rmdir(temp_dir)
        except:
            pass
    
    return subtitle_path

def create_video(file_pairs, output_path, transition_duration=0.5, music_file=None, music_volume=0.1, 
              offline_tts=False, pause_duration=1.0, lang='en', speed_factor=1.0, 
              resolution=(1280, 720), burn_captions=False, caption_font_size=30,
              caption_position='bottom', caption_font=None, tts_method='gtts', tts_voice=None):
    """Create a video from the image/text pairs"""
    # Start timing
    start_time = time.time()
    
    # Create temp directory for audio files
    temp_dir = os.path.join(os.path.dirname(output_path) or ".", "temp_audio")
    os.makedirs(temp_dir, exist_ok=True)
    print(f"Temp audio directory created: {temp_dir}")
    
    # Unpack resolution
    width, height = resolution
    print(f"Output video resolution: {width}x{height}")
    
    clips = []
    
    for i, (text_file, image_file) in enumerate(file_pairs):
        # Read caption
        with open(text_file, 'r', encoding='utf-8') as f:
            caption = f.read().strip()
        
        print(f"Processing slide {i+1}: {os.path.basename(text_file)}")
        
        # Create audio from caption
        audio_file = os.path.join(temp_dir, f"audio_{i}.mp3")
        text_to_speech(caption, audio_file, method=tts_method, offline=offline_tts, 
                       lang=lang, voice=tts_voice, speed_factor=speed_factor)
        
        # Get audio duration
        audio_clip = AudioFileClip(audio_file)
        audio_duration = audio_clip.duration
        print(f"  Audio duration: {audio_duration:.2f} seconds")
        
        # Create image clip with duration matching the audio + pause
        # Resize the image to the target resolution
        image_clip = (ImageClip(image_file)
                     .set_duration(audio_duration + pause_duration)
                     .resize(width=width, height=height))
        
        # If burn captions option is enabled, overlay text on the image
        if burn_captions:
            if not IMAGEMAGICK_AVAILABLE:
                print("Warning: ImageMagick is not installed or not found in PATH.")
                print("Cannot burn captions without ImageMagick. Continuing without captions.")
                print("For installation instructions, see: https://imagemagick.org/script/download.php")
            else:
                try:
                    print(f"  Creating text caption with font size {caption_font_size}")
                    
                    # Calculate the usable text width - 80% of video width for safety
                    max_text_width = int(width * 0.8)
                    
                    # Choose a font - start with user font, fallback to language-specific, then default
                    font_to_use = caption_font
                    if not font_to_use:
                        # Try to get language-specific fonts
                        font_options = LANGUAGE_FONTS.get(lang, LANGUAGE_FONTS['default'])
                        for font in font_options:
                            if font:
                                font_to_use = font
                                break
                    
                    bg_color = '#000000af'
                    # Create a simplified TextClip with background color
                    # Use method='caption' for text wrapping and alignment
                    caption_clip = TextClip(
                        caption,
                        fontsize=caption_font_size,
                        color='white',
                        bg_color=bg_color,  # RGBA with alpha for semi-transparency
                        font=font_to_use,
                        method='caption',
                        align='center',
                        size=(max_text_width, None),
                    )
                    
                    # Define vertical margin for captions
                    caption_vertical_margin = 20  # pixels from top or bottom edge
                    
                    # Position the caption on the main video based on user choice
                    if caption_position == 'top':
                        caption_clip = caption_clip.set_position(('center', caption_vertical_margin))
                    elif caption_position == 'middle':
                        caption_clip = caption_clip.set_position('center')
                    else:  # bottom
                        # For bottom position, we need to calculate the distance from the bottom
                        # Using lambda function to dynamically calculate the position based on frame size
                        caption_clip = caption_clip.set_position(lambda t: ('center', height - caption_clip.h - caption_vertical_margin))
                    
                    # Set duration to match the image clip
                    caption_clip = caption_clip.set_duration(image_clip.duration)
                    
                    # Create a black background clip with the full resolution size
                    background_clip = ColorClip(size=(width, height), 
                                              color=(0, 0, 0), 
                                              duration=image_clip.duration)
                    
                    # Center the image on the background
                    image_clip = image_clip.set_position('center')
                    
                    # Overlay both the image and caption on the background clip
                    # This ensures the caption has enough space and won't be truncated
                    image_clip = CompositeVideoClip([background_clip, image_clip, caption_clip])
                    
                    # # Save the image clip for debugging
                    # try:
                    #     debug_dir = "debug_frames"
                    #     if not os.path.exists(debug_dir):
                    #         os.makedirs(debug_dir)
                    #     debug_path = os.path.join(debug_dir, f"frame_{len(clips):03d}.png")
                    #     image_clip.save_frame(debug_path, t=0)
                    #     print(f"  Saved debug frame to: {debug_path}")
                    # except Exception as e:
                    #     print(f"  Warning: Could not save debug frame: {e}")
                    
                    print(f"  Successfully added caption using font: {font_to_use or 'default'}")
                except Exception as e:
                    print(f"Error adding captions: {e}")
                    print("Continuing without captions for this slide.")
        
        # Make sure the audio clip duration doesn't exceed its intended duration
        audio_clip = audio_clip.set_duration(audio_duration)
        
        # Position the audio at the beginning of the slide (leaving silence at the end)
        audio_clip = audio_clip.set_start(0)
        
        # Add audio to image
        video_clip = image_clip.set_audio(audio_clip)
        
        print(f"  Slide duration with pause: {audio_duration + pause_duration:.2f} seconds")
        clips.append(video_clip)
    
    print(f"Created {len(clips)} video clips")
    
    # Apply transitions if specified
    if len(clips) > 1 and transition_duration > 0:
        print(f"Applying {transition_duration}s transitions between clips")
        
        # Create a list of clips with transitions applied
        final_clips = [clips[0]]
        
        # Apply crossfadein to all clips except the first one
        for i in range(1, len(clips)):
            # Ensure audio doesn't overlap during transitions by explicitly managing it
            clip_with_transition = clips[i].crossfadein(transition_duration)
            
            # Make sure the audio from this clip starts only when the clip actually starts
            if clip_with_transition.audio is not None:
                # The audio should start after the transition begins
                clip_audio = clip_with_transition.audio.set_start(0)
                clip_with_transition = clip_with_transition.set_audio(clip_audio)
                
            final_clips.append(clip_with_transition)
        
        # Concatenate with negative padding to create the crossfade overlap effect
        final_clip = concatenate_videoclips(final_clips, method="compose", padding=-transition_duration)
        print(f"Final duration with transitions: {final_clip.duration:.2f} seconds")
    else:
        # Simple concatenation without transitions
        final_clip = concatenate_videoclips(clips, method="compose")
        print(f"Final duration without transitions: {final_clip.duration:.2f} seconds")
    
    print(f"Audio present in final clip: {final_clip.audio is not None}")
    
    # Add background music if specified
    if music_file and os.path.exists(music_file):
        background_music = AudioFileClip(music_file)
        
        # Loop the music if it's shorter than the video
        if background_music.duration < final_clip.duration:
            # Calculate how many loops we need
            loops_needed = int(final_clip.duration / background_music.duration) + 1
            # Create a list of the same audio clip multiple times
            music_clips = [background_music] * loops_needed
            # Concatenate them
            background_music = concatenate_audioclips(music_clips)
        
        # Trim the music to match the video duration
        background_music = background_music.subclip(0, final_clip.duration)
        
        # Set the volume
        background_music = background_music.volumex(music_volume)
        
        # Mix the audio
        if final_clip.audio is not None:
            final_audio = CompositeAudioClip([final_clip.audio, background_music])
            final_clip = final_clip.set_audio(final_audio)
        else:
            final_clip = final_clip.set_audio(background_music)
            print("Warning: No audio found in clips, using only background music")
    else:
        if final_clip.audio is None:
            print("Error: No audio found in the final clip")
    
    # Write the final video file
    print(f"Writing video to {output_path}")
    # Use a specific codec and bitrate for better quality
    final_clip.write_videofile(output_path, fps=24, audio_codec="aac", audio_bitrate="192k")
    
    # Clean up temp directory
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    os.rmdir(temp_dir)
    print(f"Temp directory cleaned up: {temp_dir}")
    
    # Calculate and display total processing time
    end_time = time.time()
    total_time = end_time - start_time
    
    # Format the time nicely
    hours, remainder = divmod(total_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        time_str = f"{int(hours)}h {int(minutes)}m {seconds:.2f}s"
    elif minutes > 0:
        time_str = f"{int(minutes)}m {seconds:.2f}s"
    else:
        time_str = f"{seconds:.2f}s"
    
    print(f"\nTotal processing time: {time_str}")
    print(f"Average processing time per slide: {(total_time / len(file_pairs)):.2f} seconds")
    
    return output_path

def list_supported_languages():
    """Print the list of supported languages"""
    print("\nSupported Languages:")
    print("====================")
    for code, name in SUPPORTED_LANGUAGES.items():
        print(f"{code}: {name}")
    print("\nNote: Offline TTS with pyttsx3 may have limited language support.")

def list_available_fonts():
    """Print the list of available fonts for TextClip"""
    if not IMAGEMAGICK_AVAILABLE:
        print("\nError: ImageMagick is not installed or not found in PATH.")
        print("ImageMagick is required for TextClip and font listing functionality.")
        print("For installation instructions, visit: https://imagemagick.org/script/download.php")
        print("\nAfter installing ImageMagick, make sure it's in your system PATH.")
        return
        
    try:
        from moviepy.video.VideoClip import TextClip
        print("\nQuerying available fonts from ImageMagick...")
        fonts = TextClip.list('font')
        
        if not fonts:
            print("\nNo fonts found. This might indicate an issue with your ImageMagick installation.")
            return
            
        print(f"\nFound {len(fonts)} available fonts:")
        print("============================")
        for font in sorted(fonts):
            print(font)
        print("\nUsage: Use these font names with the --caption-font option.")
        print("Note: Font availability may vary depending on your system configuration.")
    except Exception as e:
        print(f"\nError listing fonts: {e}")
        print("This could be due to issues with ImageMagick configuration or installation.")
        print("Make sure ImageMagick is properly installed and in your system PATH.")

def list_edge_voices():
    """Print available voices for Edge TTS"""
    print("Available EdgeTTS voices by language:")
    for lang, voices in EDGE_TTS_VOICES.items():
        language_name = SUPPORTED_LANGUAGES.get(lang, lang)
        print(f"\n{lang} ({language_name}):")
        for voice in voices:
            print(f"  - {voice}")
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description='Generate a video from text and image files')
    
    # Add arguments that only require input_dir for video generation
    parser.add_argument('--list-languages', action='store_true',
                        help='List all supported languages and exit')
    parser.add_argument('--list-fonts', action='store_true',
                        help='List all available fonts for captions and exit')
    parser.add_argument('--list-voices', action='store_true',
                        help='List available voices for Edge TTS and exit')
                        
    # Only parse these arguments first
    args, remaining_argv = parser.parse_known_args()
    
    # If just listing fonts or languages, we don't need input_dir
    if args.list_languages:
        list_supported_languages()
        return
        
    if args.list_fonts:
        list_available_fonts()
        return
        
    if args.list_voices:
        list_edge_voices()
        return
        
    # Add all other arguments for normal operation
    parser.add_argument('input_dir', help='Directory containing text and image files')
    parser.add_argument('--output', '-o', default='output.mp4', help='Output video file path')
    parser.add_argument('--transition', '-t', type=float, default=0.5, 
                        help='Duration of transition between slides (seconds, 0 for no transition)')
    parser.add_argument('--music', '-m', help='Background music file path')
    parser.add_argument('--music-volume', '-v', type=float, default=0.1, 
                        help='Volume of background music from 0.0 to 1.0 (default: 0.1)')
    parser.add_argument('--offline-tts', '-ol', action='store_true',
                        help='Use offline TTS (requires pyttsx3)')
    parser.add_argument('--pause', '-p', type=float, default=1.0,
                        help='Duration of pause between narrations in seconds (default: 1.0)')
    parser.add_argument('--language', '-l', default='en',
                        help='Language for text-to-speech (default: en)')
    parser.add_argument('--speed', '-s', type=float, default=1.0,
                        help='Speech rate factor (1.0 is normal speed, 1.5 is 50%% faster, 0.75 is 25%% slower)')
    parser.add_argument('--width', '-w', type=int, default=1280,
                        help='Width of the output video in pixels (default: 1280)')
    parser.add_argument('--height', '-H', type=int, default=720,
                        help='Height of the output video in pixels (default: 720)')
    parser.add_argument('--burn-captions', action='store_true',
                        help='Burn text captions on the video')
    parser.add_argument('--caption-font-size', type=int, default=30,
                        help='Font size for text captions')
    parser.add_argument('--caption-position', choices=['top', 'middle', 'bottom'], default='bottom',
                        help='Position for text captions')
    parser.add_argument('--caption-font', 
                        help='Font file path or name for captions')
    parser.add_argument('--generate-subtitles', action='store_true',
                        help='Generate a subtitle file alongside the video')
    parser.add_argument('--subtitle-format', choices=['srt', 'vtt'], default='srt',
                        help='Format for subtitle file (default: srt)')
    parser.add_argument('--tts-speed', '-ts', type=float, default=1.0,
                        help='TTS speech rate (0.5-2.0, default=1.0)')
    parser.add_argument('--tts-method', '-tm', type=str, default='edge', choices=['edge', 'gtts', 'pyttsx3'],
                        help='TTS method to use: gtts (Google), edge (Microsoft Edge), pyttsx3 (offline)')
    parser.add_argument('--tts-voice', '-tv', type=str, default=None,
                        help='TTS voice to use (available for edge TTS method)')
    
    # Parse all arguments
    args = parser.parse_args(remaining_argv, namespace=args)
    
    # Check if ImageMagick is installed when burn_captions is requested
    if args.burn_captions and not IMAGEMAGICK_AVAILABLE:
        print("WARNING: --burn-captions requires ImageMagick, but it is not installed or not found in PATH.")
        print("The video will be created without captions.")
        print("For installation instructions, visit: https://imagemagick.org/script/download.php")
        print("After installing ImageMagick, make sure it's in your system PATH.")
        print("")
        
        # Ask if user wants to continue
        if sys.stdin.isatty():  # Only prompt if running interactively
            response = input("Do you want to continue without captions? (y/n): ")
            if response.lower() != 'y':
                print("Aborting.")
                return
    
    # Validate speed factor
    if args.speed <= 0:
        print(f"Error: Speed factor must be positive. Got {args.speed}")
        return
    elif args.speed > 3.0:
        print(f"Warning: Very high speed factor ({args.speed}). Speech may be difficult to understand.")
    
    # Validate resolution
    if args.width <= 0 or args.height <= 0:
        print(f"Error: Width and height must be positive. Got {args.width}x{args.height}")
        return
    elif args.width > 3840 or args.height > 2160:
        print(f"Warning: Very high resolution ({args.width}x{args.height}). This may result in slow processing.")
    
    # Check if the specified language is supported
    if args.language not in SUPPORTED_LANGUAGES:
        print(f"Warning: Language '{args.language}' is not in the list of recognized languages.")
        print("The speech synthesis might not work properly.")
        print("Use --list-languages to see all supported languages.")
    else:
        print(f"Using language: {SUPPORTED_LANGUAGES[args.language]} ({args.language})")
    
    print(f"Speech speed factor: {args.speed}x")
    print(f"Output resolution: {args.width}x{args.height}")
    
    # Ensure input directory exists
    if not os.path.isdir(args.input_dir):
        print(f"Error: Directory '{args.input_dir}' does not exist")
        return
    
    # Get file pairs
    pairs = get_file_pairs(args.input_dir)
    if not pairs:
        print("No valid text/image pairs found")
        return
    
    print(f"Found {len(pairs)} text/image pairs")
    
    # Check if music file exists if specified
    if args.music and not os.path.exists(args.music):
        print(f"Warning: Music file '{args.music}' not found. Continuing without background music.")
        args.music = None
    
    # Create output directory if needed
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate subtitles if requested
    if args.generate_subtitles:
        print(f"Generating {args.subtitle_format.upper()} subtitle file...")
        subtitle_path = create_subtitle_file_from_audio(
            pairs, args.output, args.pause, args.subtitle_format,
            args.offline_tts, args.language, args.speed
        )
        print(f"Subtitle file created: {subtitle_path}")
    
    # Generate the video
    output_path = create_video(pairs, args.output, args.transition, args.music, 
                              args.music_volume, args.offline_tts, args.pause, 
                              args.language, args.speed, resolution=(args.width, args.height),
                              burn_captions=args.burn_captions, caption_font_size=args.caption_font_size,
                              caption_position=args.caption_position, caption_font=args.caption_font,
                              tts_method=args.tts_method, tts_voice=args.tts_voice)
    print(f"Video successfully created: {output_path}")

if __name__ == "__main__":
    main() 