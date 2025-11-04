#!/usr/bin/env python3
"""
Create a minimalist slideshow video from images and videos.
Memory-efficient: processes files sequentially.
"""

import os
import subprocess
import re
import tempfile
import platform
from pathlib import Path


def extract_number(filename: str) -> int:
    """Extract the number from filename like 'Griffin and Faja - 1 of 38.png'"""
    match = re.search(r'(\d+) of \d+', filename)
    if match:
        return int(match.group(1))
    return 0


def get_media_files(directory: str, exclude_output: str = None) -> list[tuple[str, str, bool, bool]]:
    """
    Get all PNG, MP4, and MOV files sorted by their number.
    Returns list of (filepath, type, skip_fade_in, skip_fade_out) tuples.
    When PNG and MOV share the same number:
    - MOV comes first with skip_fade_out=True (fade-in only)
    - PNG follows with skip_fade_in=True (no fade-in)
    Excludes the output file if specified.
    """
    directory_path = Path(directory)

    # Get all media files
    png_files = [(f, 'image') for f in directory_path.glob('*.png')]
    mp4_files = [(f, 'video') for f in directory_path.glob('*.mp4')]
    mov_files = [(f, 'video') for f in directory_path.glob('*.mov')]

    all_files = png_files + mp4_files + mov_files

    # Exclude output file if it exists
    if exclude_output:
        exclude_name = Path(exclude_output).name
        all_files = [(f, t) for f, t in all_files if f.name != exclude_name]

    # Group files by number
    files_by_number = {}
    for file_path, file_type in all_files:
        num = extract_number(file_path.name)
        if num not in files_by_number:
            files_by_number[num] = []
        files_by_number[num].append((file_path, file_type))

    # Sort and process groups
    result = []
    for num in sorted(files_by_number.keys()):
        group = files_by_number[num]

        # Separate MOV and PNG files in this group
        movs = [(f, t) for f, t in group if f.suffix.lower() == '.mov']
        pngs = [(f, t) for f, t in group if f.suffix.lower() == '.png']
        others = [(f, t) for f, t in group if f.suffix.lower() not in ['.mov', '.png']]

        # If there's a MOV and PNG with same number, MOV first (no fade-out), then PNG (no fade-in)
        if movs and pngs:
            # Add MOV first with skip_fade_out=True
            for f, t in movs:
                result.append((str(f), t, False, True))
            # Add PNG(s) with skip_fade_in=True
            for f, t in pngs:
                result.append((str(f), t, True, False))
        else:
            # No matching pair, add normally
            for f, t in movs + pngs + others:
                result.append((str(f), t, False, False))

    return result


def find_music_file(directory: str) -> str | None:
    """Find MP3 file in directory or media subdirectory."""
    directory_path = Path(directory)
    # Check main directory first, then media folder
    for search_dir in [directory_path, directory_path / 'media']:
        mp3_files = list(search_dir.glob('*.mp3'))
        if mp3_files:
            return str(mp3_files[0])
    return None


def check_ffmpeg() -> bool:
    """Check if ffmpeg is available."""
    try:
        subprocess.run(['ffmpeg', '-version'],
                      capture_output=True,
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_audio_duration(audio_file: str) -> float:
    """Get duration of audio file in seconds."""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        audio_file
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        return duration if duration > 0 else 0.0
    except (subprocess.CalledProcessError, ValueError):
        return 0.0


def get_rotation(file_path: str) -> int:
    """Get rotation angle from video/image metadata."""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream_side_data_list=rotation',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        file_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        rotation = result.stdout.strip()
        if rotation:
            return int(float(rotation))
    except:
        pass

    # Check for display matrix rotation
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'side_data=rotation',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        file_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        rotation = result.stdout.strip()
        if rotation:
            return int(float(rotation))
    except:
        pass

    return 0


def get_video_duration(video_file: str) -> float:
    """Get duration of video file in seconds."""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_file
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        return duration if duration > 0 else 5.0  # Default to 5s if invalid
    except (subprocess.CalledProcessError, ValueError):
        # If we can't get duration, default to 5 seconds
        return 5.0


def create_image_segment(
    img_file: str,
    output_segment: str,
    width: int,
    height: int,
    slide_duration: float,
    fade_duration: float,
    fps: int,
    skip_fade_in: bool = False
) -> None:
    """Create a single image slide video segment with fade and auto-rotation."""
    fade_start = slide_duration - fade_duration

    # Build fade filter
    fade_parts = []
    if not skip_fade_in:
        fade_parts.append(f'fade=t=in:st=0:d={fade_duration}')
    fade_parts.append(f'fade=t=out:st={fade_start}:d={fade_duration}')
    fade_filter = ','.join(fade_parts)

    # Get rotation and apply transpose if needed
    rotation = get_rotation(img_file)
    rotation_filter = ''
    if rotation == 90:
        rotation_filter = 'transpose=1,'
    elif rotation == 180:
        rotation_filter = 'transpose=1,transpose=1,'
    elif rotation == 270:
        rotation_filter = 'transpose=2,'

    cmd = [
        'ffmpeg',
        '-y',
        '-loop', '1',
        '-t', str(slide_duration),
        '-i', img_file,
        '-vf', (
            f'{rotation_filter}'
            f'scale={width}:{height}:force_original_aspect_ratio=decrease,'
            f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,'
            f'setsar=1,fps={fps},'
            f'{fade_filter}'
        ),
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',
        output_segment
    ]

    subprocess.run(cmd, check=True, capture_output=True, text=True)


def create_video_segment(
    video_file: str,
    output_segment: str,
    width: int,
    height: int,
    fade_duration: float,
    fps: int,
    skip_fade_out: bool = False
) -> None:
    """Process a video file: scale, center, add fade transitions, auto-rotate."""
    duration = get_video_duration(video_file)
    fade_start = max(0, duration - fade_duration)

    # Build fade filter
    fade_parts = []
    fade_parts.append(f'fade=t=in:st=0:d={fade_duration}')
    if not skip_fade_out:
        fade_parts.append(f'fade=t=out:st={fade_start}:d={fade_duration}')
    fade_filter = ','.join(fade_parts)

    # Get rotation and apply transpose if needed
    rotation = get_rotation(video_file)
    rotation_filter = ''
    if rotation == 90:
        rotation_filter = 'transpose=1,'
    elif rotation == 180:
        rotation_filter = 'transpose=1,transpose=1,'
    elif rotation == 270:
        rotation_filter = 'transpose=2,'

    cmd = [
        'ffmpeg',
        '-y',
        '-i', video_file,
        '-vf', (
            f'{rotation_filter}'
            f'scale={width}:{height}:force_original_aspect_ratio=decrease,'
            f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,'
            f'setsar=1,fps={fps},'
            f'{fade_filter}'
        ),
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',
        '-an',  # Remove audio for consistency
        output_segment
    ]

    subprocess.run(cmd, check=True, capture_output=True, text=True)


def create_slideshow(
    media_files: list[tuple[str, str, bool, bool]],
    output_file: str = 'slideshow.mp4',
    slide_duration: float = 4.0,
    fade_duration: float = 0.5,
    fps: int = 30,
    resolution: str = '1920x1080',
    music_file: str | None = None,
    music_trim_start: float = 20.0,
    music_fade_in: float = 2.0,
    music_fade_out: float = 6.0
) -> None:
    """
    Create a minimalist slideshow video with smooth fade transitions.
    Memory-efficient: processes files one at a time.
    Handles both images and videos.
    Optionally adds background music with fade in/out.
    """
    if not media_files:
        print("No media files found!")
        return

    image_count = sum(1 for _, t, _, _ in media_files if t == 'image')
    video_count = sum(1 for _, t, _, _ in media_files if t == 'video')

    print(f"Found {len(media_files)} files ({image_count} images, {video_count} videos)")
    if music_file:
        print(f"Music: {Path(music_file).name} (trim first {music_trim_start}s, fade in {music_fade_in}s, fade out {music_fade_out}s at end)")
    print(f"Creating minimalist slideshow: {output_file}")
    print(f"Image duration: {slide_duration}s, Fade: {fade_duration}s")

    width, height = resolution.split('x')
    width, height = int(width), int(height)

    script_dir = Path(output_file).parent
    temp_dir = script_dir / '.slideshow_temp'
    temp_dir.mkdir(exist_ok=True)

    segment_files = []
    video_without_audio = None

    # Calculate target duration from music if provided
    target_duration = None
    if music_file and Path(music_file).exists():
        audio_duration = get_audio_duration(music_file)
        target_duration = audio_duration - music_trim_start
        print(f"Target slideshow duration: {target_duration:.2f}s (from trimmed audio)")

    # Calculate total duration needed for all slides/videos
    total_duration_needed = 0.0
    for file_path, file_type, _, _ in media_files:
        if file_type == 'image':
            total_duration_needed += slide_duration
        else:  # video
            vid_duration = get_video_duration(file_path)
            total_duration_needed += vid_duration

    # Adjust durations if we have a target duration
    duration_scale = 1.0
    if target_duration and total_duration_needed > 0:
        duration_scale = target_duration / total_duration_needed
        print(f"Duration scale factor: {duration_scale:.3f}")

    try:
        # Process each file sequentially
        print("\nProcessing files...")
        for i, (file_path, file_type, skip_fade_in, skip_fade_out) in enumerate(media_files, 1):
            segment_file = str(temp_dir / f'segment_{i:03d}.mp4')
            notes = []
            if skip_fade_in:
                notes.append("no fade-in")
            if skip_fade_out:
                notes.append("no fade-out")
            note_str = f" [{', '.join(notes)}]" if notes else ""
            print(f"  [{i}/{len(media_files)}] {Path(file_path).name} ({file_type}){note_str}")

            if file_type == 'image':
                adjusted_slide_duration = slide_duration * duration_scale
                create_image_segment(
                    file_path, segment_file, width, height,
                    adjusted_slide_duration, fade_duration, fps, skip_fade_in
                )
            else:  # video
                create_video_segment(
                    file_path, segment_file, width, height,
                    fade_duration, fps, skip_fade_out
                )

            segment_files.append(segment_file)

        # Create concat file list
        concat_file = str(temp_dir / 'concat_list.txt')
        with open(concat_file, 'w') as f:
            for seg in segment_files:
                f.write(f"file '{seg}'\n")

        # Concatenate all segments (video only, no audio)
        print("\nConcatenating segments...")
        video_without_audio = str(temp_dir / 'video_no_audio.mp4')
        cmd = [
            'ffmpeg',
            '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c:v', 'copy',
            '-an',  # No audio
            video_without_audio
        ]

        subprocess.run(cmd, check=True, capture_output=False, text=True)

        # Get video duration
        video_duration = get_video_duration(video_without_audio)

        # Add music if provided
        if music_file and Path(music_file).exists():
            print("\nAdding background music...")
            # Get full audio duration
            audio_duration = get_audio_duration(music_file)
            # Trim: remove first N seconds only, keep the rest (will fade out at end)
            trimmed_duration = audio_duration - music_trim_start
            # Calculate fade out timing - fade out at end of slideshow
            music_fade_out_start = video_duration - music_fade_out

            print(f"Video duration: {video_duration:.2f}s, Trimmed audio: {trimmed_duration:.2f}s")

            # Create silent audio track for video, then mix with trimmed music
            cmd = [
                'ffmpeg',
                '-y',
                '-i', video_without_audio,
                '-i', music_file,
                '-filter_complex', (
                    f'[0:v]copy[v];'
                    f'anullsrc=channel_layout=stereo:sample_rate=44100:duration={video_duration}[a0];'
                    f'[1:a]atrim={music_trim_start}:{audio_duration},'
                    f'asetpts=PTS-STARTPTS,'
                    f'afade=t=in:st=0:d={music_fade_in},'
                    f'afade=t=out:st={music_fade_out_start}:d={music_fade_out}[a1];'
                    f'[a0][a1]amix=inputs=2:duration=first:dropout_transition=2[outa]'
                ),
                '-map', '[v]',
                '-map', '[outa]',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-shortest',
                output_file
            ]
        else:
            # No music, just copy video
            cmd = [
                'ffmpeg',
                '-y',
                '-i', video_without_audio,
                '-c', 'copy',
                output_file
            ]

        subprocess.run(cmd, check=True, capture_output=False, text=True)
        print(f"\n✓ Slideshow created: {output_file}")

    finally:
        # Clean up temporary segments
        print("\nCleaning up temporary files...")
        for seg in segment_files:
            try:
                Path(seg).unlink()
            except:
                pass
        try:
            if video_without_audio and Path(video_without_audio).exists():
                Path(video_without_audio).unlink()
            Path(concat_file).unlink()
            temp_dir.rmdir()
        except:
            pass


def open_video(video_file: str) -> None:
    """Open video file in default media player."""
    video_path = Path(video_file)

    if not video_path.exists():
        print(f"Video file not found: {video_file}")
        return

    system = platform.system()
    try:
        if system == 'Darwin':  # macOS
            subprocess.run(['open', str(video_path)], check=True)
        elif system == 'Linux':
            subprocess.run(['xdg-open', str(video_path)], check=True)
        elif system == 'Windows':
            subprocess.run(['start', str(video_path)], check=True, shell=True)
        else:
            print(f"Unsupported platform: {system}")
    except subprocess.CalledProcessError as e:
        print(f"Error opening video: {e}")
    except FileNotFoundError:
        print("Could not find default media player")


def main():
    """Main function."""
    script_dir = Path(__file__).parent
    media_dir = script_dir / 'media'

    # Check if media directory exists
    if not media_dir.exists():
        print(f"Error: Media directory not found: {media_dir}")
        print("Please create a 'media' folder and add your images/videos there.")
        return

    if not check_ffmpeg():
        print("Error: ffmpeg is not installed or not in PATH")
        print("Please install ffmpeg:")
        print("  macOS: brew install ffmpeg")
        return

    output_file = str(script_dir / 'slideshow.mp4')
    media_files = get_media_files(str(media_dir), exclude_output=output_file)

    if not media_files:
        print(f"No media files found in {media_dir}!")
        return

    print(f"Looking for media files in: {media_dir}")
    print("Files to include:")
    for file_path, file_type, skip_fade_in, skip_fade_out in media_files[:5]:
        notes = []
        if skip_fade_in:
            notes.append("no fade-in")
        if skip_fade_out:
            notes.append("no fade-out")
        note_str = f" [{', '.join(notes)}]" if notes else ""
        print(f"  - {Path(file_path).name} ({file_type}){note_str}")
    if len(media_files) > 5:
        print(f"  ... and {len(media_files) - 5} more")

    output_file = str(script_dir / 'slideshow.mp4')
    # Check for music in both main directory and media folder
    music_file = find_music_file(str(script_dir))

    create_slideshow(
        media_files=media_files,
        output_file=output_file,
        slide_duration=4.0,
        fade_duration=0.5,
        fps=30,
        resolution='1920x1080',
        music_file=music_file,
        music_trim_start=20.0,
        music_fade_in=2.0,
        music_fade_out=6.0
    )

    # Prompt to play video
    if Path(output_file).exists():
        print(f"\n{'='*60}")
        response = input(f"\nPlay slideshow in default media player? [Y/n]: ").strip().lower()
        if response in ('', 'y', 'yes'):
            print("Opening video...")
            open_video(output_file)


if __name__ == '__main__':
    main()
