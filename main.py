import logging
import os

import humanize
import requests
from typing import List

import settings
import todoist_api
from todoist_api import TodoistBackup

# Use the built-in version of scandir/walk if possible, otherwise
# use the scandir module version
try:
    from os import scandir
except ImportError:
    from scandir import scandir


def build_full_backup_path(backup: TodoistBackup):
    return os.path.join(
        settings.BACKUP_PATH,
        backup.safe_filename()
    )


def dump_backup_list(backups: List[TodoistBackup]):
    with open(os.path.join(settings.BACKUP_PATH, "backup-list.txt"), "w") as f:
        f.write("Current backup list:\n\n")

        if backups:
            f.writelines([backup.safe_filename() + "\n" for backup in backups])
        else:
            f.write("no backups found via Todoist API")


def move_to_archive(filepath_to_move: str):
    if not os.path.exists(settings.BACKUP_ARCHIVE_PATH):
        os.mkdir(settings.BACKUP_ARCHIVE_PATH)

    dst_path = os.path.join(
        settings.BACKUP_ARCHIVE_PATH,
        os.path.basename(filepath_to_move)
    )

    os.rename(filepath_to_move, dst_path)


def move_old_backups_to_archive(backups: List[TodoistBackup]):
    backup_filenames = [backup.safe_filename() for backup in backups]

    for entry in scandir(settings.BACKUP_PATH):
        if entry.is_file() and entry.name[-4:] == ".zip":
            if entry.name in backup_filenames:
                continue

            logging.info("Moving backup %s to archive" % entry.name)
            move_to_archive(entry.path)


def main():
    logging.info("Starting backup download")

    backup_list = todoist_api.get_backup_list()

    dump_backup_list(backup_list)

    if not backup_list:
        logging.info("No backups found via Todoist API")

    session = requests.session()

    for backup in backup_list:
        backup_path = build_full_backup_path(backup)

        if os.path.exists(backup_path):
            logging.debug(
                "[backup:%s] Skipping, already downloaded." % backup.version
            )
            continue

        logging.info("[backup:%s] Downloading backup" % backup.version)

        backup_size = session.head(backup.url).headers["content-length"]
        if backup_size:
            logging.info("[backup:%s] %s" % (
                backup.version, humanize.naturalsize(backup_size)
            ))

        r = session.get(backup.url, stream=True, timeout=1)

        if not r.ok:
            logging.error("[backup:%s] Download failed! (%s)" % (
                backup.version, r.status_code
            ))
            continue

        with open(backup_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=256):
                f.write(chunk)

        logging.info("[backup:%s] Download finished" % backup.version)

    move_old_backups_to_archive(backup_list)

    logging.info("All done")


if __name__ == "__main__":
    main()
