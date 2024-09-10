import subprocess

def get_ip_address():
    try:
        result = subprocess.run(['ip', '-4', 'addr', 'show', 'wlan0'], capture_output=True, text=True)
        output = result.stdout
        
        for line in output.split('\n'):
            if 'inet' in line:
                ip = line.split()[1].split('/')[0]
                return ip
    except Exception as e:
        print(f"Error getting IP address: {e}")
    return "IP not found"