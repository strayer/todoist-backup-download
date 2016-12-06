import logging
import os

import humanize
import requests
from typing import List

import settings
import todoist_api
from todoist_api import TodoistBackup


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


def main():
    logging.info("Starting backup download")

    backup_list = todoist_api.get_backup_list()

    dump_backup_list(backup_list)

    if not backup_list:
        logging.info("No backups found, exiting.")

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

    logging.info("All done")

if __name__ == "__main__":
    main()
