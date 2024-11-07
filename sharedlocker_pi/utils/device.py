import subprocess

def get_device_by_bus_info(bus_info):
    result = subprocess.run(['v4l2-ctl', '--list-devices'], stdout=subprocess.PIPE, text=True)
    devices = result.stdout.split('\n\n')
    
    for device in devices:
        lines = device.split('\n')
        if len(lines) < 2:
            continue
        device_name = lines[0]
        device_path = lines[1].strip()
        device_info = subprocess.run(['v4l2-ctl', '-d', device_path, '--info'], stdout=subprocess.PIPE, text=True).stdout
        if bus_info in device_info:
            return device_path
    return None
