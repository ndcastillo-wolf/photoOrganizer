Photo Organizer (working title)

Organize and backup iPhone photos/videos into a clean folder structure (YYYY-MM) using EXIF metadata.
Optionally move or copy files from one or more source directories to a single destination.

Features

📸 Reads EXIF DateTimeOriginal to determine when photos/videos were taken.

🗂️ Creates a dated folder structure:

dest/iPhone_Photos/YYYY-MM/[RAW_Images|ss_and_downloads]


✅ Supports common formats (.jpg, .jpeg, .png, .heic, .dng, .mov, .mp4, .aae).

🚀 Uses concurrency (ThreadPoolExecutor) for faster handling.

🔄 Handles filename conflicts automatically (photo_1.jpg, photo_2.jpg, …).

⚡ CLI powered by Click
.

Installation

For now, clone the repo and run with Python 3.

git clone https://github.com/<your-username>/photo-organizer.git
cd photo-organizer
pip install -r requirements.txt   # (to be created)


Dependencies:

- click
- exifread

Usage

Basic example:

python photos_handler.py /path/to/DCIM --dest /path/to/backup --move


Multiple origins:

python photos_handler.py /path1 /path2 --dest /backup --copy


Show help:

python photos_handler.py --help

Roadmap

 Split into modules (cli.py, core.py, …).

 Add unit tests with pytest.

 Support --dry-run mode.

 Add progress bar for large imports.

 Package as installable CLI (pip install photo-organizer).

Contributing

This is an early-stage project. Ideas, issues, and pull requests are welcome.
