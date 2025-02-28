import socket
import sys
import time
from time import sleep
import random

# Arguments parsing and server constants
if len(sys.argv) != 8:
    print('[ERROR] Server arguments sent is wrong (should sent 7)')
    exit(-1)
# Server settings
SERVER_IP = sys.argv[1]
SERVER_PORT = int(sys.argv[2])

# Client setting (total ram and disk are in GB, and they must be powers of two)
SERVICE_NAME = sys.argv[3]
TOTAL_RAM = int(sys.argv[4])
TOTAL_DISK = int(sys.argv[5])
DELAY = float(int(sys.argv[6])/1000)
random.seed(int(sys.argv[7]))  # Random seed for generation


# Hardcoded message function
def get_message_format(cpu, free_ram, free_disk):
    return '{\n' \
           f' "serviceName": "{SERVICE_NAME}",\n' \
           f' "Timestamp": {time.time_ns()},\n' \
           f' "CPU": {cpu},\n' \
           ' "RAM": {\n' \
           f' "Total": {TOTAL_RAM},\n' \
           f' "Free": {free_ram}\n' \
           ' },\n' \
           ' "Disk": {\n' \
           f' "Total": {TOTAL_DISK},\n' \
           f' "Free": {free_disk}\n' \
           ' },\n' \
           '}\n'


# Extra function to control the message (can be removed)
def generate_message():
    return get_message_format(
        cpu=random.random(),
        free_ram=random.random() * TOTAL_RAM,
        free_disk=random.random() * TOTAL_DISK
    )


# Connecting to the server and entering the loop
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
while True:
    msg = generate_message()
    UDPClientSocket.sendto(str.encode(msg), (SERVER_IP, SERVER_PORT))
    sleep(DELAY)
