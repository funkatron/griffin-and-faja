# Griffin and Faja Slideshow Generator

A minimalist Python script to create beautiful slideshow videos from images and videos with background music.

## Overview

This project creates slideshow videos from a collection of images and videos, with smooth fade transitions, auto-rotation correction, and optional background music. The slideshow is designed to match the duration of the background music automatically.

## Features

- **Memory-efficient**: Processes media files sequentially (one at a time)
- **Smart transitions**: 
  - PNG images fade in/out smoothly
  - When a PNG and MOV share the same number, MOV plays first with fade-in only, then PNG appears instantly (no fade-in)
- **Auto-rotation**: Automatically corrects orientation based on metadata
- **Music integration**: 
  - Trims first 20 seconds from MP3
  - Fades in over 2 seconds at the start
  - Fades out over 6 seconds at the end
  - Slideshow duration matches trimmed music length
- **Minimalist design**: Clean, centered images with black padding

## Requirements

- Python 3.x
- ffmpeg (installed and in PATH)
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt-get install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Usage

1. Place your media files (PNG images, MOV/MP4 videos) in the `media/` folder
2. Optionally add an MP3 file for background music (in `media/` or root directory)
3. Run the script:

```bash
python3 create_slideshow.py
```

4. The script will:
   - Process all images and videos sequentially
   - Scale and center them at 1920x1080 resolution
   - Create smooth fade transitions
   - Add background music if provided
   - Generate `slideshow.mp4` in the root directory

5. You'll be prompted to play the video in your default media player

## File Organization

```
.
├── create_slideshow.py  # Main slideshow generator
├── strip_metadata.py    # Utility to strip metadata from media files
├── media/               # Place your images and videos here
│   ├── *.png
│   ├── *.mov
│   └── *.mp3 (optional)
└── slideshow.mp4        # Output video (created after running)
```

## Configuration

You can modify these settings in `create_slideshow.py`:

- `slide_duration`: Duration for each image slide (default: 4.0 seconds)
- `fade_duration`: Duration of fade transitions (default: 0.5 seconds)
- `music_trim_start`: Seconds to trim from start of music (default: 20.0)
- `music_fade_in`: Fade-in duration for music (default: 2.0 seconds)
- `music_fade_out`: Fade-out duration for music (default: 6.0 seconds)
- `resolution`: Output resolution (default: '1920x1080')

## Metadata Stripping

Before committing media files, run `strip_metadata.py` to remove metadata:
- Strips all metadata from PNG images
- Removes location/GPS data from MOV videos
- Preserves MP3 metadata (not stripped)

```bash
python3 strip_metadata.py
```

## Special Behavior

- **PNG + MOV pairs**: When files share the same number (e.g., "2 of 38.png" and "2 of 38.mov"):
  - MOV plays first with fade-in only (no fade-out)
  - PNG appears immediately after with no fade-in (only fade-out)
  - Creates a seamless transition

## License

This is a personal project - feel free to use and modify as needed.

---

I made this for my son, who is the best thing I have ever done and will ever do.

Mea maxuma culpa to Mr. Evans and Ms. O'Connor, the latter of whom is assuredly leading the choir of Heaven as we speak, finally embraced.

