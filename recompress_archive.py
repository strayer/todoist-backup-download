import glob
import logging
import os
import sys
import tarfile
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import humanize

import settings
import utils

# Use the built-in version of scandir if possible, otherwise
# use the scandir module version
try:
    from os import scandir
except ImportError:
    from scandir import scandir

if not utils.python_module_exists("lzma"):
    print("ERROR: lzma module is required!", file=sys.stderr)
    sys.exit(1)


def compress_path_as_tar(path: str, tar_path: str):
    with tarfile.open(tar_path, "w|xz") as f_tar:
        # Not simply doing f_tar.add(path, arcname='') because it causes an
        # empty / folder to appear in the tar file
        for entry in scandir(path):
            f_tar.add(entry.path, arcname=entry.name)


def extract_zip(zipfile_path: str, target_dir: str):
    with ZipFile(zipfile_path) as f_zip:
        f_zip.extractall(target_dir)


def build_tar_path(zipfile_path):
    ext = zipfile_path[-4:]

    if ext == ".zip":
        return zipfile_path[:-4] + ".tar.xz"
    else:
        return zipfile_path + ".tar.xz"


def main():
    archived_zips = glob.glob(
        os.path.join(settings.BACKUP_ARCHIVE_PATH, "*.zip")
    )

    if not archived_zips:
        logging.info("No archived backups to recompress")
        sys.exit(0)

    logging.info("Recompressing %s archived backups" % len(archived_zips))

    for archived_zip_path in archived_zips:
        tar_path = build_tar_path(archived_zip_path)

        with TemporaryDirectory() as tmpdirname:
            extract_zip(archived_zip_path, tmpdirname)
            compress_path_as_tar(tmpdirname, tar_path)

        zip_size = os.path.getsize(archived_zip_path)
        tar_size = os.path.getsize(tar_path)

        os.remove(archived_zip_path)

        logging.info(
            "Recompressed archive %s, saved %s" % (
                os.path.basename(archived_zip_path),
                humanize.naturalsize(zip_size - tar_size)
            )
        )

    logging.info("All done")


if __name__ == '__main__':
    main()
