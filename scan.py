import socket
import csv
from concurrent.futures import ThreadPoolExecutor

# Define the IP range and ports to scan
ip_range_start = "192.168.1.1"
ip_range_end = "192.168.1.254"
ports_to_scan = [5555, 22, 80, 443]  # Example ports to scan

# Convert IP range to integers for easy iteration
def ip_to_int(ip):
    return sum(int(octet) << (8 * i) for i, octet in enumerate(reversed(ip.split('.'))))

def int_to_ip(int_ip):
    return '.'.join(str((int_ip >> (8 * i)) & 0xFF) for i in reversed(range(4)))

start_int = ip_to_int(ip_range_start)
end_int = ip_to_int(ip_range_end)

# Function to scan a single port on a single IP
def scan_port(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)  # Set timeout to 1 second
            if s.connect_ex((ip, port)) == 0:
                return port
    except Exception:
        pass
    return None

# Function to scan all specified ports on a single IP
def scan_ip(ip):
    open_ports = []
    for port in ports_to_scan:
        if scan_port(ip, port):
            open_ports.append(port)
    return ip, open_ports

# Scan the IP range
def scan_ip_range(start, end):
    results = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        future_to_ip = {executor.submit(scan_ip, int_to_ip(ip)): ip for ip in range(start, end + 1)}
        for future in future_to_ip:
            ip, open_ports = future.result()
            if open_ports:
                results.append((ip, open_ports))
    return results

# Scan and save results to CSV
scan_results = scan_ip_range(start_int, end_int)

with open('open_ports_multiple.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["IP Address", "Open Ports"])
    for ip, open_ports in scan_results:
        writer.writerow([ip, ', '.join(map(str, open_ports))])

print(f"Scan complete. Results saved to 'open_ports_multiple.csv'.")
