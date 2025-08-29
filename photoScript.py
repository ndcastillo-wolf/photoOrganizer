import os
import shutil
import logging
from datetime import datetime
import exifread
from concurrent.futures import ThreadPoolExecutor
import time
import click

# Define basic logging information 

logging.basicConfig(
    format="%(asctime)s: %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

### Valid extensions for both photo and video 

VALID_EXTS = {'.jpg', '.jpeg', '.png', '.heic', '.dng', '.mov', '.mp4', '.aae'}

def get_creation_date(file_path: str) -> datetime:
    try:
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f, details=False)
            if 'EXIF DateTimeOriginal' in tags:
                date_str = str(tags['EXIF DateTimeOriginal'])
                return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        logger.debug(f"EXIF error for {file_path}: {e}")

    return datetime.fromtimestamp(os.path.getmtime(file_path))

def process_file(file_info, move_files: bool = True):
    src_path, dest_dir = file_info
    filename = os.path.basename(src_path)
    ext = os.path.splitext(filename)[1].lower()

    # quick exits
    if filename.startswith('.') or ext not in VALID_EXTS:
        return False

    try:
        date_taken = get_creation_date(src_path)
        month_year = date_taken.strftime("%Y-%m")

        base_folder = os.path.join(dest_dir, "iPhone_Photos", month_year)
        raw_dir = os.path.join(base_folder, "RAW_Images")
        png_dir = os.path.join(base_folder, "ss_and_downloads")

        final_dir = raw_dir if ext == '.dng' else png_dir if ext == '.png' else base_folder
        os.makedirs(final_dir, exist_ok=True)

        # name conflict handling
        dest_path = os.path.join(final_dir, filename)
        counter = 1
        name, orig_ext = os.path.splitext(filename)
        while os.path.exists(dest_path):
            dest_path = os.path.join(final_dir, f"{name}_{counter}{orig_ext}")
            counter += 1

        if move_files:
            shutil.move(src_path, dest_path)
            logger.info(f"Moved: {filename} → {os.path.basename(final_dir)}")
        else:
            shutil.copy2(src_path, dest_path)
            logger.info(f"Copied: {filename} → {os.path.basename(final_dir)}")

        return True

    except Exception as e:
        logger.error(f"Error processing {filename}: {e}")
        return False

def process_directory(origin: str, dest: str, move_files: bool = True) -> int:
    file_list = []
    for root, _, files in os.walk(origin):
        for file in files:
            file_list.append((os.path.join(root, file), dest))

    with ThreadPoolExecutor(max_workers=min(32, (os.cpu_count() or 1) * 4)) as executor:
        results = list(executor.map(lambda f: process_file(f, move_files), file_list))

    return sum(1 for r in results if r)

# Setting CLI functionality through the cli function through the click library 


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "--origin", "origins",
    multiple=True,
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, path_type=str),
    help="Source directory (repeat to add more, e.g., --origin A --origin B)."
)
@click.option(
    "--dest", required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True, path_type=str),
    help="Destination root directory."
)
@click.option("--move/--copy", default=False, show_default=True)
@click.option("--recursive/--no-recursive", default=True, show_default=True)
def cli(origins, dest, move, recursive):
    start = time.perf_counter()
    click.echo("=== Photo Organization Script with Concurrency ===")
    click.echo(f"Mode: {'MOVE' if move else 'COPY'}")

    # Optional: dedupe and keep stable order
    seen = set()
    unique_origins = [o for o in origins if not (o in seen or seen.add(o))]

    total_processed = 0
    for origin in unique_origins:
        if recursive:
            directories = [origin] + [os.path.join(root, d) for root, dirs, _ in os.walk(origin) for d in dirs]
        else:
            directories = [origin]

        for directory in directories:
            click.echo(f"\nProcessing: {directory}")
            count = process_directory(directory, dest, move_files=move)
            total_processed += count
            click.echo(f"Processed {count} files in this folder")

    elapsed = time.perf_counter() - start
    click.echo("\n=== Organization Complete ===")
    click.echo(f"Total files processed: {total_processed}")
    click.echo(f"Destination structure: {dest}/iPhone_Photos/YYYY-MM/[RAW_Images|ss_and_downloads]")
    click.echo(f"Total time: {elapsed:.2f}s")

if __name__ == "__main__":
    cli()
