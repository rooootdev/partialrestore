from tempfile import TemporaryDirectory
from pathlib import Path

from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.services.mobilebackup2 import Mobilebackup2Service
from pymobiledevice3.services.diagnostics import DiagnosticsService
from pymobiledevice3.exceptions import PyMobileDevice3Exception

from . import backup
from .backup import _FileMode as FileMode

def restore(backup: backup.Backup, reboot: bool = False):
    try:
        with TemporaryDirectory() as backup_dir:
            backup.write_to_directory(Path(backup_dir))

            lockdown = create_using_usbmux()
            with Mobilebackup2Service(lockdown) as mb:
                mb.restore(backup_dir, system=True, reboot=reboot, copy=False, source=".")
            if reboot:
                with DiagnosticsService(lockdown) as diagnostics_service:
                    diagnostics_service.restart()
    except PyMobileDevice3Exception as e:
        if "Find My" in str(e):
            print("disable find my iphone.")
            raise e
        elif "crash_on_purpose" not in str(e):
            raise e