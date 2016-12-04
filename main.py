import logging
import os

import humanize
import requests

import settings
import todoist_api


def build_full_backup_path(backup: todoist_api.TodoistBackup):
    return os.path.join(
        settings.BACKUP_PATH,
        backup.safe_filename()
    )


def main():
    logging.info("Starting backup download")

    backup_list = todoist_api.get_backup_list()

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
