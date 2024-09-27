import socket
import subprocess


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        return f"Error al obtener la IP local: {str(e)}"


def get_default_gateway():
    try:
        # Usamos 'ip route' para obtener la puerta de enlace predeterminada
        result = subprocess.run(["ip", "route", "show", "default"],
                                capture_output=True, text=True)
        gateway = result.stdout.split()[2]
        return gateway
    except Exception as e:
        return f"Error al obtener la puerta de enlace: {str(e)}"


def get_wifi_networks():
    try:
        result = subprocess.run(["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "device", "wifi", "list"], capture_output=True, text=True)
        networks = []
        for line in result.stdout.strip().split('\n'):
            ssid, signal, security = line.split(':')
            networks.append({
                'ssid': ssid,
                'signal': signal,
                'security': security
            })
        return networks
    except Exception as e:
        return f"Error al obtener las redes WiFi: {str(e)}"
    
    
if __name__ == "__main__":
    # Obtener y mostrar las IPs
    print(f"Tu dirección IP local es: {get_local_ip()}")
    print(f"""La dirección IP de tu router (puerta de enlace)
          es: {get_default_gateway()}""")

    # Mostrar las redes WiFi disponibles
    print("\nRedes WiFi disponibles:")
    print(get_wifi_networks())
