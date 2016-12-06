Todoist backup downloader
=========================

A simple python3 script to be used to automate the download of Todoist backup
files. Can be used as a cronjob with logging to syslog.

## Requirements

- Python 3.3+ (tested with Python 3.4)
- various Python libs (see [`requirements.txt`](requirements.txt))
- (optional) Python `lzma` module to recompress archived backup files

## Setup

- create a virtualenv (optional) and install the Python requirements with
`pip install -r requirements.txt`
- create a `settings_local.py` file to override settings in
[settings.py](settings.py)

## Usage

Run `main.py` to start the backup process and `recompress_archive.py` to
recompress archived backup files.

The main script will download all not yet downloaded backups to the
configured backup folder.

The recompress utility will recompress all archived zip files as
`.tar.xz` archives to save space. This doesn't make a huge difference in
my case (2kb instead of 10kb per file), but may end up worthwhile for
bigger Todoist profiles.

## Cron example

These are example files to let cron automatically run the backup process
every 6 hours.

```python
# settings_local.py
BACKUP_PATH = "/var/lib/syncthing/backup_todoist/"
TODOIST_TOKEN = "1234567"
DEBUG = False
SYSLOG_ENABLED = True
```

```
# crontab -e
13 */6 * * * /path/todoist-backup-download/run.sh
```

```bash
# run.sh
#!/bin/sh
cd /path/todoist-backup-download

./.venv/bin/python main.py
./.venv/bin/python recompress_archive.py

exit 0
```
