#!/usr/bin/env python3
"""
Automated tests for create_slideshow.py
Run with: python3 -m pytest test_slideshow.py -v
Or: python3 test_slideshow.py
"""

import sys
import subprocess
import platform
from pathlib import Path

# Import the module to test
try:
    from create_slideshow import (
        check_ffmpeg,
        get_media_files,
        find_music_file,
        get_hardware_codec,
        extract_number,
        get_audio_duration,
        get_video_duration,
        get_rotation,
    )
except ImportError as e:
    print(f"Error importing create_slideshow: {e}")
    sys.exit(1)


class TestSlideshow:
    """Test suite for slideshow generator."""

    def test_python_syntax(self):
        """Test that the Python file has valid syntax."""
        with open('create_slideshow.py', 'r') as f:
            compile(f.read(), 'create_slideshow.py', 'exec')
        assert True

    def test_imports(self):
        """Test that all required functions can be imported."""
        assert check_ffmpeg is not None
        assert get_media_files is not None
        assert find_music_file is not None
        assert get_hardware_codec is not None

    def test_ffmpeg_available(self):
        """Test that ffmpeg is available."""
        assert check_ffmpeg() is True, "ffmpeg is not installed or not in PATH"

    def test_hardware_codec_detection(self):
        """Test hardware codec detection."""
        h264_codec, h264_crf = get_hardware_codec('h264')
        h265_codec, h265_crf = get_hardware_codec('h265')

        assert h264_codec is not None
        assert h265_codec is not None
        assert h264_crf in ['23', '28']
        assert h265_crf in ['23', '28']

        # On macOS, should use VideoToolbox if available
        if platform.system() == 'Darwin':
            # Either hardware or software encoder is fine
            assert 'h264' in h264_codec.lower() or 'libx264' in h264_codec.lower()
            assert 'h265' in h265_codec.lower() or 'hevc' in h265_codec.lower() or 'libx265' in h265_codec.lower()

    def test_media_files_detection(self):
        """Test media files detection."""
        media_dir = Path('media')
        if not media_dir.exists():
            # Skip if media directory doesn't exist
            return

        media_files = get_media_files('media')
        assert len(media_files) > 0, "No media files found in media/ directory"

        # Check structure of returned tuples
        for file_path, file_type, skip_fade_in, skip_fade_out in media_files[:5]:
            assert isinstance(file_path, str)
            assert file_type in ['image', 'video']
            assert isinstance(skip_fade_in, bool)
            assert isinstance(skip_fade_out, bool)

    def test_music_file_detection(self):
        """Test music file detection (optional)."""
        music_file = find_music_file('.')
        # Music file is optional, so just check it returns None or a valid path
        if music_file:
            assert Path(music_file).exists(), f"Music file not found: {music_file}"
            assert music_file.endswith('.mp3'), "Music file should be MP3"

    def test_extract_number(self):
        """Test number extraction from filenames."""
        assert extract_number("Griffin and Faja - 1 of 38.png") == 1
        assert extract_number("Griffin and Faja - 10 of 38.mov") == 10
        assert extract_number("test.png") == 0  # No number
        assert extract_number("file - 5 of 20.png") == 5

    def test_command_line_help(self):
        """Test that command-line help works."""
        result = subprocess.run(
            ['python3', 'create_slideshow.py', '--help'],
            capture_output=True,
            text=True,
            check=True
        )
        assert '--codec' in result.stdout
        assert 'h264' in result.stdout
        assert 'h265' in result.stdout

    def test_codec_validation(self):
        """Test that invalid codecs are rejected."""
        result = subprocess.run(
            ['python3', 'create_slideshow.py', '--codec', 'invalid'],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0, "Invalid codec should be rejected"

    def test_valid_codecs(self):
        """Test that valid codecs are accepted."""
        for codec in ['h264', 'h265']:
            result = subprocess.run(
                ['python3', 'create_slideshow.py', '--codec', codec, '--help'],
                capture_output=True,
                text=True,
                check=True
            )
            assert result.returncode == 0


def run_tests():
    """Run tests without pytest."""
    print("=" * 60)
    print("Running Automated Tests")
    print("=" * 60)

    test_instance = TestSlideshow()
    tests = [
        ("Python syntax", test_instance.test_python_syntax),
        ("Imports", test_instance.test_imports),
        ("ffmpeg availability", test_instance.test_ffmpeg_available),
        ("Hardware codec detection", test_instance.test_hardware_codec_detection),
        ("Media files detection", test_instance.test_media_files_detection),
        ("Music file detection", test_instance.test_music_file_detection),
        ("Number extraction", test_instance.test_extract_number),
        ("Command-line help", test_instance.test_command_line_help),
        ("Codec validation", test_instance.test_codec_validation),
        ("Valid codecs", test_instance.test_valid_codecs),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            print(f"\n[{passed + failed + 1}/{len(tests)}] Testing {name}...")
            test_func()
            print(f"  ✓ {name}")
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ {name}: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)


