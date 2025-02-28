import datetime
import socket
import threading
import sys
import subprocess
from datetime import date

# Arguments parsing and server constants
if len(sys.argv) != 5:
    print('[ERROR] Server arguments sent is wrong (should sent 4)')
    exit(-1)
SERVER = sys.argv[1]
PORT = int(sys.argv[2])
BUFFER_SIZE = int(sys.argv[3])
MESSAGES_TO_SENT = int(sys.argv[4])
# Local server variables
messages = ['' for _ in range(MESSAGES_TO_SENT)]
current_message = 0


# This function writes the 1024 to a file and calls the hdfs to store it
def send_to_hdfs():
    today_date = str(date.today()).split('-')
    filename = f'{today_date[2]}_{today_date[1]}_{today_date[0]}.log'
    fw = open(filename, 'w', buffering=(MESSAGES_TO_SENT * BUFFER_SIZE))
    for i in range(MESSAGES_TO_SENT):
        fw.write(messages[i])
    fw.flush()
    fw.close()
    subprocess.run([f'hadoop fs -appendToFile {filename} /{filename}'],shell = True)
    print(f'[INFO] Server sent to hdfs at {datetime.datetime.now()}')


# Handle client function (msg is the message received from client, address is the client address)
def handle_client(msg, address):
    global lock, messages, current_message
    # Critical area
    lock.acquire()
    messages[current_message] = msg.decode("utf-8")
    current_message += 1
    if current_message == MESSAGES_TO_SENT:
        send_to_hdfs()
        current_message = 0
    lock.release()


lock = threading.Lock()
# Server setup and entering the for loop
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((SERVER, PORT))
print(f'[STARTING] server is starting...')
while True:
    packet = UDPServerSocket.recvfrom(BUFFER_SIZE)
    thread = threading.Thread(target=handle_client, args=(packet[0], packet[1]))
    thread.start()
