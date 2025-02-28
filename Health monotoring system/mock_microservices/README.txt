Running the driver:

-> python driver.py
* driver.py, client.py and config.txt MUST ALL BE IN THE SAME DIRECTORY
* The driver will only run the clients and the server should run manually
* You must put the number of clients in the first line then you should specify the clients arguments
and put new line between each client.
* YOU MUST STICK TO THIS FORMAT IN THE CONFIGURATION FILE FOR EACH CLIENT:

SERVER_IP = <ip>
SERVER_PORT_NUMBER = <port_number>
SERVICE_NAME = <service_name>
TOTAL_RAM = <ram>
TOTAL_DISK = <disk>
DELAY = <delay>
SEED = <seed>
<NEW LINE>

* Refer to the last section for more notes on the clients arguments


Running the server:

-> python server.py <SERVER_IP> <SERVER_PORT_NUMBER> <BUFFER_SIZE> <MESSAGES_TO_SENT>
* BUFFER_SIZE : This is the size of the buffer in Bytes where the server will store the
clients message in (MAXIMUM HEAlTH MESSAGE LENGTH in bytes).
* MESSAGES_TO_SENT : This is the number of messages that the server stores before it sends them to hdfs.
* The default size for <BUFFER_SIZE> is 256
* The default size for <MESSAGES_TO_SENT> is 1024

Running the client [MANUALLY]:

-> python client.py <SERVER_IP> <SERVER_PORT_NUMBER> <SERVICE_NAME> <TOTAL_RAM> <TOTAL_DISK> <DELAY_ms> <RANDOM_SEED>
* DELAY_ms : The delay is the time in (ms) that the clients sleeps before it sends another message to the server.
BE CAREFUL : If the time is below 50 ms THIS FUNCTION WON'T BEHAVE AS PREDICTED.
NOTE : If you want the client not to wait just put 0
* RANDOM_SEED : It is the seed for generating random numbers for used ram and disk