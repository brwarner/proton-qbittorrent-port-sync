import configparser
import logging
import os
import re
import sys
from pathlib import Path
from urllib import request, parse
from packaging.version import Version

# HACK: ProtonVPN for some reason sets the working directory to System32 instead of the exe directory. Correct.
if "system32" in os.getcwd():
    os.chdir(os.path.dirname(sys.executable))

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='sync.log',
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

# Read config file
config = configparser.ConfigParser()
config.read('sync.ini')

def find_best_version_folder(directory):
    best_version_dir = None
    best_version = None
    for path in Path(directory).glob("v*"):
        version = Version(path.name[1:])
        logger.info(f"Found version folder {version}.")
        if best_version_dir is None or version > best_version:
            best_version_dir = path.name
            best_version = version
    return best_version_dir

def find_log_file(base_dir, relative_log_dir):
    version_dir = find_best_version_folder(base_dir)
    logger.info(f"Latest version is in folder {version_dir}.")
    return os.path.join(base_dir, version_dir, relative_log_dir)

def find_port(filename):
    logger.info(f"Searching for VPN port forwarding settings in {filename}")
    try:
        with open(filename) as logs:
            lines = logs.readlines()
            lines.reverse()
            for line in lines:
                match = re.search(r"Port pair (\d+)->(\d+)", line)
                if match:
                    logger.info(f"Found forwarding port: {match.group(1)}")
                    return match.group(1)
        logger.critical(f"Couldn't find Port pair line in log file {filename}")
        return -1
    except Exception as err:
        logger.critical(err)
        return -1

def set_port(address, port_number):
    # Send request to change port to torrent client
    logger.info(f"Configuring incoming connections port {port_number} for qBittorrent running at {address}")

    data = parse.urlencode(dict(json=f'{{"listen_port": {port_number}}}')).encode()
    req = request.Request(f'{address}/api/v2/app/setPreferences', data=data)
    try:
        with request.urlopen(req) as resp:
            if resp.status == 200:
                logger.info("Received status 200. Success.")
                return True
            else:
                logger.error(f"Failed to set port. Received status {resp.status}. Reason: {resp.reason}.")
                return False
    except Exception as err:
        logger.critical(err)
        return False

# Find the log file
log_file = find_log_file(config["DEFAULT"]["ProtonBaseDir"], config["DEFAULT"]["ProtonRelativeLogFile"])
if not os.path.exists(log_file):
    logger.error(f"Log file {log_file} does not exist.")
    exit(-1)

# Find the current port number from ProtonVPN
port = find_port(log_file)
if port == -1:
    exit(-1)

# Set the port in qBittorrent
success = set_port(config["DEFAULT"]["TorrentClientAddress"], port)
if not success:
    exit(-1)
