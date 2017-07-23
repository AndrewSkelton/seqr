import logging
import re
import subprocess
import time

from seqr.utils.filesystem.shared import FileStats
from seqr.utils.shell_utils import run_shell_command

logger = logging.getLogger(__name__)

#def get_gs_default_service_acount():
#     "gs compute instances list --format=json"


def is_google_bucket_file_path(file_path):
    return file_path.startswith("gs://")


def does_google_bucket_file_exist(gs_path):
    return get_google_bucket_file_stats(gs_path) is not None


def get_google_bucket_file_stats(gs_path):
    _, gsutil_stat_output, _ = run_shell_command("gsutil stat %(gs_path)s" % locals(), wait_and_return_log_output=True, verbose=False)

    """
    Example gsutil stat output:

    Creation time:          Fri, 09 Jun 2017 09:36:23 GMT
    Update time:            Fri, 09 Jun 2017 09:36:23 GMT
    Storage class:          REGIONAL
    Content-Length:         363620675
    Content-Type:           text/x-vcard
    Hash (crc32c):          SWOktA==
    Hash (md5):             fEdIumyOFR7HvULeAwXCwQ==
    ETag:                   CMae+J67sNQCEAE=
    Generation:             1497000983793478
    Metageneration:         1
    """

    if not gsutil_stat_output:
        return None

    EMPTY_MATCH_OBJ = re.match("()", "")
    DATE_FORMAT = '%a, %d %b %Y %H:%M:%S %Z'

    creation_time = (re.search("Creation.time:[\s]+(.+)", gsutil_stat_output, re.IGNORECASE) or EMPTY_MATCH_OBJ).group(1)
    update_time = (re.search("Update.time:[\s]+(.+)", gsutil_stat_output, re.IGNORECASE) or EMPTY_MATCH_OBJ).group(1)
    file_size = (re.search("Content-Length:[\s]+(.+)", gsutil_stat_output, re.IGNORECASE) or EMPTY_MATCH_OBJ).group(1)
    file_md5 = (re.search("Hash (md5):[\s]+(.+)", gsutil_stat_output, re.IGNORECASE) or EMPTY_MATCH_OBJ).group(1)

    ctime = time.mktime(time.strptime(creation_time, DATE_FORMAT))
    mtime = time.mktime(time.strptime(update_time, DATE_FORMAT))
    return FileStats(ctime=ctime, mtime=mtime, size=file_size, md5=file_md5)


def google_bucket_file_iter(gs_path):
    """Iterate over lines in the given file"""
    command = "gsutil cat %(gs_path)s %(gunzip_command)s"
    if gs_path.endswith("gz"):
        command += "| gunzip -c - "

    with subprocess.Popen(command, stdout=subprocess.PIPE) as process:
        for line in process.stdout:
            yield line


def copy_google_bucket_file(source_path, destination_path):
    """Copy file to or from a google bucket"""

    returncode = run_shell_command("gsutil -m cp -P %(source_path)s %(destination_path)s" % locals(), verbose=True).wait()

    if returncode:
        raise ValueError("Failed to copy %s %s. Return code: " % (source_path, destination_path, returncode))

