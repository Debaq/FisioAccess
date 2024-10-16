import subprocess
import socket
import os

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        return f"Error al obtener la IP local: {str(e)}"

def get_display_server():
    if 'DISPLAY' in os.environ:
        return 'Xo'  # Xorg is running
    elif os.path.exists('/dev/fb0'):
        return 'B'  # Framebuffer is available
    else:
        return '?'  # Unknown or no graphical environment
    
    
def get_cpu_temperature():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = float(f.read().strip()) / 1000
        return f"{temp:.1f}°C"
    except Exception as e:
        return f"Error: {str(e)}"