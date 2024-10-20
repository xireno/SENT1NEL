import psutil
import time

def get_current_drives():
    """Get a list of all currently mounted drives."""
    partitions = psutil.disk_partitions()
    return [p.device for p in partitions if 'removable' in p.opts]

def detect_usb_changes(previous_drives):
    """Detect if a USB drive was connected or removed."""
    current_drives = get_current_drives()

    # Check for new drives (connected)
    new_drives = [drive for drive in current_drives if drive not in previous_drives]
    if new_drives:
        print(f"USB Drive Connected: {', '.join(new_drives)}")

    # Check for removed drives (disconnected)
    removed_drives = [drive for drive in previous_drives if drive not in current_drives]
    if removed_drives:
        print(f"USB Drive Removed: {', '.join(removed_drives)}")

    return current_drives

def monitor_usb():
    """Continuously monitor for USB changes."""
    print("Monitoring USB devices...")

    # Get the initial list of drives
    previous_drives = get_current_drives()
    print(f"Current Drives: {', '.join(previous_drives) if previous_drives else 'None'}")

    # Monitor for changes continuously
    try:
        while True:
            previous_drives = detect_usb_changes(previous_drives)
            time.sleep(2)  # Check every 2 seconds
    except KeyboardInterrupt:
        print("\nStopping USB monitoring.")

def get_drives_info():
    """Fetch information about all connected drives."""
    drives = []
    partitions = psutil.disk_partitions()
    for partition in partitions:
        usage = psutil.disk_usage(partition.mountpoint)
        drive_info = {
            "device": partition.device,
            "mountpoint": partition.mountpoint,
            "fstype": partition.fstype,
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.percent
        }
        drives.append(drive_info)
    return drives
