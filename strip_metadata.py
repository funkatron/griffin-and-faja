#!/usr/bin/env python3
"""
Strip metadata from media files in the media/ folder using mpv/ffmpeg.
Removes EXIF data from images and metadata from videos.
"""

import subprocess
from pathlib import Path


def strip_image_metadata(image_path: Path, temp_path: Path) -> bool:
    """Strip metadata from image using ffmpeg."""
    try:
        ext = image_path.suffix.lower()
        if ext == '.png':
            cmd = [
                'ffmpeg',
                '-y',
                '-i', str(image_path),
                '-map_metadata', '-1',
                '-pix_fmt', 'rgba',
                '-update', '1',
                '-frames:v', '1',
                str(temp_path)
            ]
        else:
            cmd = [
                'ffmpeg',
                '-y',
                '-i', str(image_path),
                '-map_metadata', '-1',
                '-update', '1',
                '-frames:v', '1',
                '-codec', 'copy',
                str(temp_path)
            ]
        subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if temp_path.exists() and temp_path.stat().st_size > 0:
            temp_path.replace(image_path)
            return True
        return False
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        return False


def strip_video_metadata(video_path: Path, temp_path: Path) -> bool:
    """Strip location metadata from video using ffmpeg."""
    try:
        cmd = [
            'ffmpeg',
            '-y',
            '-i', str(video_path),
            '-map_metadata', '-1',  # Remove all metadata first
            '-metadata', 'location=',  # Explicitly clear location
            '-metadata', 'com.apple.quicktime.location=',  # Clear QuickTime location
            '-metadata', 'com.apple.quicktime.location.ISO6709=',  # Clear ISO location
            '-codec', 'copy',
            str(temp_path)
        ]
        subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if temp_path.exists() and temp_path.stat().st_size > 0:
            temp_path.replace(video_path)
            return True
        return False
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        return False


def strip_audio_metadata(audio_path: Path, temp_path: Path) -> bool:
    """Skip audio metadata stripping - keep MP3 data."""
    # Don't strip audio metadata
    return False


def main():
    media_dir = Path('media')

    if not media_dir.exists():
        print("Error: media/ directory not found")
        return

    image_extensions = {'.png', '.jpg', '.jpeg'}
    video_extensions = {'.mov', '.mp4', '.avi', '.mkv'}
    audio_extensions = {'.mp3', '.m4a', '.aac', '.wav'}

    files_to_process = []
    for ext in image_extensions | video_extensions | audio_extensions:
        files_to_process.extend(media_dir.glob(f'*{ext}'))

    if not files_to_process:
        print("No media files found in media/ directory")
        return

    print(f"Found {len(files_to_process)} files to process")
    print("Stripping metadata...\n")

    success_count = 0
    fail_count = 0

    for file_path in sorted(files_to_process):
        print(f"Processing: {file_path.name}...", end=' ')
        # Use same extension for temp file - prepend dot to filename
        temp_path = file_path.parent / f'.tmp_{file_path.name}'

        success = False
        if file_path.suffix.lower() in image_extensions:
            success = strip_image_metadata(file_path, temp_path)
        elif file_path.suffix.lower() in video_extensions:
            success = strip_video_metadata(file_path, temp_path)
        elif file_path.suffix.lower() in audio_extensions:
            # Skip audio files - keep their metadata
            print("(skipped - keeping metadata)")
            success = True  # Count as success since we're intentionally skipping
            continue

        if success:
            print("✓")
            success_count += 1
        else:
            print("✗")
            fail_count += 1
            if temp_path.exists():
                temp_path.unlink()

    print(f"\nDone! Success: {success_count}, Failed: {fail_count}")


if __name__ == '__main__':
    main()

