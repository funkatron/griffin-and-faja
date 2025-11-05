# Agent Documentation

This file provides context and guidance for AI agents working on this codebase.

## Project Overview

This is a Python-based slideshow video generator that creates minimalist videos from images and videos with background music. The project prioritizes memory efficiency by processing media files sequentially rather than loading everything into memory.

## Key Files

- **`create_slideshow.py`** - Main script that generates slideshow videos
- **`strip_metadata.py`** - Utility to remove metadata from media files before committing
- **`test_slideshow.py`** - Automated test suite (10 tests)
- **`README.md`** - User-facing documentation
- **`media/`** - Directory containing source images (PNG), videos (MOV/MP4), and optional music (MP3)

## Core Functions

### Media Processing

- **`get_media_files(directory, exclude_output)`** - Discovers and sorts media files by number
  - Returns tuples: `(filepath, type, skip_fade_in, skip_fade_out)`
  - Groups files by number (e.g., "1 of 38")
  - Special handling: When PNG and MOV share same number, MOV plays first with no fade-out, PNG follows with no fade-in

- **`extract_number(filename)`** - Extracts number from filenames like "Griffin and Faja - 1 of 38.png"

- **`get_rotation(file_path)`** - Uses ffprobe to detect rotation metadata from EXIF/QuickTime

### Video Segment Creation

- **`create_image_segment(...)`** - Processes a single PNG image into a video segment
  - Scales and centers with black padding
  - Applies rotation correction via transpose filters
  - Adds fade transitions (conditional based on `skip_fade_in`)
  - Uses hardware acceleration when available

- **`create_video_segment(...)`** - Processes a single MOV/MP4 into a video segment
  - Similar to image segment but preserves original duration
  - Removes audio track for consistency
  - Conditional fade-out based on `skip_fade_out`

### Audio Processing

- **`find_music_file(directory)`** - Locates MP3 file in directory or media subdirectory

- **`get_audio_duration(audio_file)`** - Gets duration using ffprobe

- **`get_video_duration(video_file)`** - Gets duration using ffprobe (with fallback)

### Codec & Hardware

- **`get_hardware_codec(codec)`** - Detects best available codec
  - On macOS: Checks for VideoToolbox hardware encoders (h264_videotoolbox, hevc_videotoolbox)
  - Falls back to software encoders (libx264, libx265) if hardware unavailable
  - Returns tuple: `(codec_name, crf_value)`
  - CRF: 23 for H.264, 28 for H.265

### Main Workflow

- **`create_slideshow(...)`** - Orchestrates the entire slideshow generation
  1. Discovers media files
  2. Calculates target duration from trimmed music
  3. Processes each file sequentially into individual segments
  4. Creates concat file listing all segments
  5. Combines segments with FFmpeg concat demuxer
  6. Adds trimmed and faded background music
  7. Outputs final video with web optimization (`-movflags +faststart`)

## Design Decisions

### Memory Efficiency
- **Sequential Processing**: Each media file is processed individually into a segment file
- **Concat Demuxer**: Uses FFmpeg's concat demuxer (not complex filtergraph) to combine segments
- **Temporary Files**: Segment files stored in `.slideshow_temp/` directory (cleaned up after)

### Transition Logic
- PNG images: Fade in at start, fade out at end
- Videos: Fade in at start, fade out at end
- Special case: When PNG and MOV share same number:
  - MOV plays first with fade-in only (no fade-out)
  - PNG follows immediately (no fade-in, fade-out only)

### Codec Strategy
- Default: H.264 (libx264 or h264_videotoolbox)
- Option: H.265 (libx265 or hevc_videotoolbox)
- Hardware acceleration automatically detected and used on macOS
- CRF values: 23 (H.264), 28 (H.265) - balance quality vs file size

### Audio Handling
- MP3 trimmed: First 20 seconds removed (configurable via `--music-trim-start`)
- Fade in: 2 seconds at start (configurable)
- Fade out: 6 seconds at end (configurable)
- Slideshow duration automatically scales to match trimmed music length

## Command-Line Arguments

All options are configurable via argparse:
- `--slide-duration`: Duration for each image slide (default: 4.0s)
- `--fade-duration`: Duration of fade transitions (default: 1.0s)
- `--fps`: Output frame rate (default: 30)
- `--resolution`: Output resolution in WxH format (default: "1920x1080")
- `--music-trim-start`: Seconds to trim from start of MP3 (default: 20.0)
- `--music-fade-in`: Music fade-in duration (default: 2.0)
- `--music-fade-out`: Music fade-out duration (default: 6.0)
- `--output`: Output filename (default: "slideshow.mp4")
- `--no-play`: Skip prompt to play video after creation
- `--codec`: Video codec: "h264" (default) or "h265"

## Testing

Run tests with:
```bash
python3 test_slideshow.py
```

The test suite verifies:
- Python syntax and imports
- FFmpeg availability
- Hardware codec detection
- Media file detection
- Music file detection
- Number extraction logic
- Command-line interface validation

## Common Tasks

### Adding a New Feature

1. Follow OODA process: Observe, Orient, Decide, Act
2. Update relevant function(s) in `create_slideshow.py`
3. Add command-line argument if needed
4. Write tests in `test_slideshow.py`
5. Update README.md documentation
6. Test thoroughly before committing

### Debugging FFmpeg Issues

- FFmpeg commands use verbose output (no `-hide_banner`)
- Check temp files in `.slideshow_temp/` if issues occur
- Common issues:
  - Rotation: Use `get_rotation()` and apply transpose filters manually
  - Codec errors: Ensure hardware codec is available or fallback to software
  - Duration mismatches: Check `get_audio_duration()` and `get_video_duration()` return values

### Metadata Stripping

Before committing media files, run:
```bash
python3 strip_metadata.py
```

This removes:
- All metadata from PNG images
- Location metadata from MOV/MP4 videos
- Keeps MP3 metadata intact (as requested)

## Important Notes

- **Working Directory**: Script looks for media files in `media/` subdirectory
- **Output Files**: Generated videos are in project root (gitignored except `slideshow_web_loop.mp4`)
- **Temporary Files**: `.slideshow_temp/` directory created during processing (gitignored)
- **Platform Support**: macOS hardware acceleration works; Linux/Windows use software encoders
- **FFmpeg Dependency**: Must be installed and in PATH (checked by `check_ffmpeg()`)

## Git Workflow

- Media files in `media/` are tracked in git (open-source project)
- Output videos (`slideshow.mp4`) are gitignored
- Preview video (`slideshow_web_loop.mp4`) is tracked for README embedding
- Always strip metadata before committing media files

## Version History

- **v0.2**: H.265 codec support, hardware acceleration, automated tests
- **v0.1**: Initial release with basic slideshow generation

