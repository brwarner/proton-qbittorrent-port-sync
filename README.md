# ProtonVPN qBittorrent Sync

This simple python script checks the active port forwarding settings of ProtonVPN and uses qBittorrent's REST API to assign that port as the current incoming connections port.

## Configuration

Ensure there is a file called `sync.ini` in the working directory of the script. 

There are three necessary settings: `ProtonBaseDir`, `ProtonRelativeLogFile` and `TorrentClientAddress`.

* `ProtonBaseDir` is the base directory where all versions of ProtonVPN installations live on your computer. It's usually `C:\Program Files\Proton\VPN`.
  * DO NOT add the version folder here. The program will automatically scan for the highest version folder available.
* `ProtonRelativeLogFile` is the relative path of the log file within a ProtonVPN version folder. It should be `ServiceData\Logs\service-logs.txt`
* `TorrentClientAddress` is the address of your qBittorrent's web interface. Usually it's `http://127.0.0.1:8080`

## Building

In order to have this program run automatically when ProtonVPN connects, you'll need to build it into an exe file.

Run `pyinstaller -F sync.py`

To set ProtonVPN to run it automatically, go to your profile settings in the app and assign the "Connect and GO" setting to run `sync.exe`.

## Compatibility Notes

Last tested with ProtonVPN version `5.1.8` and qBittorrent `5.1.0`.