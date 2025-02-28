import subprocess
import sys

CLIENT_ARGUMENTS = 7

fh = open('config.txt', 'r')
lines = fh.read().split('\n')
fh.close()
num_clients = int(lines[0])
index = 1
# PARSING THE ARGUMENTS
for _ in range(num_clients):
    server_ip = lines[index].split()[2]
    server_port = lines[index + 1].split()[2]
    service_name = lines[index + 2].split()[2]
    total_ram = lines[index + 3].split()[2]
    total_disk = lines[index + 4].split()[2]
    delay = lines[index + 5].split()[2]
    seed = lines[index + 6].split()[2]
    subprocess.run([f'python client.py {server_ip} {server_port} {service_name} {total_ram} {total_disk} {delay} {seed}'], shell=True)
    index += CLIENT_ARGUMENTS + 1  # 1 is for the new line
