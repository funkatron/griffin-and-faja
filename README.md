# Griffin and Faja Slideshow Generator

I made this for my son, who is the best thing I have ever done and will ever do.

Mea maxuma culpa to Mr. Evans and Ms. O'Connor, the latter of whom is assuredly leading the choir of Heaven as we speak, finally embraced.

---

A minimalist Python script to create beautiful slideshow videos from images and videos with background music.

## Quick Start

1. Clone the repository
2. Make sure you have ffmpeg installed and in your PATH.
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt-get install ffmpeg` or whatever your package manager is
   - Windows: Use a package manager like Chocolatey or Scoop to install ffmpeg. example: `choco install ffmpeg` or `scoop install ffmpeg`. Alternatively, download from [ffmpeg.org](https://ffmpeg.org/download.html)
3. Run the script:
```bash
python3 create_slideshow.py
```

## Overview

This project creates a slideshow video from a collection of images and videos, with smooth fade transitions, auto-rotation correction, and optional background music. The slideshow is designed to match the duration of the background music automatically. The output video will be saved in the root directory as `slideshow.mp4`. The user will be prompted to play the video in their default media player.

The script supports a number of options beyond the default behavior and media.
For example, the user can specify the duration of each slide, the duration of the fade transitions, the resolution of the output video, the background music, and the duration of the fade in and fade out of the background music.

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

## Configuration

All configuration options can be passed as command-line arguments. Run `python3 create_slideshow.py --help` to see all available options.

### Command-Line Arguments

- `--slide-duration`: Duration for each image slide in seconds (default: 4.0)
- `--fade-duration`: Duration of fade transitions in seconds (default: 0.5)
- `--fps`: Frames per second for output video (default: 30)
- `--resolution`: Output video resolution as WIDTHxHEIGHT (default: 1920x1080)
- `--music-trim-start`: Seconds to trim from start of music (default: 20.0)
- `--music-fade-in`: Music fade-in duration in seconds (default: 2.0)
- `--music-fade-out`: Music fade-out duration in seconds (default: 6.0)
- `--output`: Custom output filename (default: slideshow.mp4)
- `--no-play`: Skip prompt to play video after creation

### Examples

```bash
# Use default settings
python3 create_slideshow.py

# Custom slide duration and fade
python3 create_slideshow.py --slide-duration 5.0 --fade-duration 1.0

# 4K resolution output
python3 create_slideshow.py --resolution 3840x2160

# Custom output filename, skip play prompt
python3 create_slideshow.py --output my_slideshow.mp4 --no-play
```

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

- The code in this repository is licensed under the [AGPL3](https://www.gnu.org/licenses/agpl-3.0.en.html).
- The media in the `media/` folder is licensed under the [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

## Credits

- [ffmpeg](https://ffmpeg.org/)
- [Python](https://www.python.org/)
