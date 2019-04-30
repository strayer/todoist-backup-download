import os
import sys

import logging
import requests
from typing import List, Dict
from urllib.parse import urlparse

import settings

TODOIST_BACKUPS_API_URL = "https://todoist.com/API/v8/backups/get"
TODOIST_REQUESTS_SESSION = requests.session()


class TodoistBackup(object):
    URL_JSON_KEY = "url"
    VERSION_JSON_KEY = "version"

    def __init__(self, json_data: Dict[str, str]):
        self.url = json_data[self.URL_JSON_KEY]  # type: str
        self.version = json_data[self.VERSION_JSON_KEY]  # type: str

    def __repr__(self):
        return "%s(%s)" % (
            type(self).__name__,
            {self.URL_JSON_KEY: self.url, self.VERSION_JSON_KEY: self.version}
        )

    def __str__(self):
        return "Todoist backup for version %s" % self.version

    def safe_filename(self) -> str:
        date, time = self.version.split(" ")
        filename = os.path.basename(urlparse(self.url).path)

        return "%s_%s_%s" % (
            date,
            time.replace(":", "-"),
            filename
        )


def get_requests_session():
    return TODOIST_REQUESTS_SESSION

def get_backup_list() -> List[TodoistBackup]:
    r = TODOIST_REQUESTS_SESSION.post(TODOIST_BACKUPS_API_URL, {
        "token": settings.TODOIST_TOKEN
    })

    if r.status_code != 200:
        logging.error(
            "Todoist API request unsuccessful, status code %s" % r.status_code
        )
        logging.error(r.text)
        sys.exit(1)

    backups_json = r.json()

    todoist_backup_list = []

    for backup in backups_json:
        if "url" not in backup or "version" not in backup:
            logging.error("Malformed backup entry: %s" % backup)
            continue

        todoist_backup_list.append(TodoistBackup(backup))

    return todoist_backup_list
