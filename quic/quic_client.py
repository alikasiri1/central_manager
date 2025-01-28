# import asyncio as asc
# from connector import *
# import aioquic.asyncio
# # from aioquic.asyncio.protocol import connect, serve
# # from aioquic.quic.configuration import QuicConfiguration
# from aioquic.asyncio.client import connect
# from aioquic.quic.configuration import QuicConfiguration
# import ssl

# class QUIC_client(client):
#     def __init__(self, host, port, use_json):
#         super().__init__(host, port, use_json)
#         self.traffic_type = "quic"
#         self.payload = b"p" * (self.quic_payload_size - 1) + b"\n"

#         self.config = QuicConfiguration(
#             is_client=True,
#             verify_mode=ssl.CERT_NONE,  # Disable certificate verification for testing
#         )

#     async def _maintask(self):
#         self._infomessage(f'Connecting to server {self.host}:{self.port}')
        
#         async with aioquic.asyncio.client.connect(
#             host=self.host, port=self.port, configuration=self.config
#         ) as client:
#             await client.wait_connected()
#             self._infomessage('Connection successful')
            
#             reader, writer = await client.create_stream()
#             self._infomessage('Stream created, now transmitting')

#             while True:
#                 # Prompt the user for input
#                 writer.write("127.0.0.1:5555\n".encode())
#                 user_input = input("Enter 'status' or 'process' or 'restart' (or 'exit' to quit): ").strip().lower()

#                 if user_input == "exit" or user_input == 'quit':
#                     self._infomessage('Exiting client...')
#                     break
#                 elif user_input in ("status", "process" , "restart"):
#                     # Send the user input to the server
#                     writer.write(f"{user_input}\n".encode())
#                     client.transmit()
#                     self._infomessage(f"Sent: {user_input}")

#                     # Wait for the server's response
#                     response = await reader.readline()
#                     self._infomessage(f"Received: {response.decode().strip()}")
#                 else:

#                     print("Invalid input. Please enter 'hello', 'goodbye', or 'exit'.")

#             # Close the connection
#             writer.write(b'STOP\n')
#             client.transmit()
#             client.close()
#             await client.wait_closed()
#             self._infomessage('Client finished')


#     def run_test(self):
#         # super().run_test()
#         loop = asc.get_event_loop()
#         loop.run_until_complete(self._maintask())



# if __name__ == "__main__":
#     # Set the server host, port, and JSON usage flag
#     client = QUIC_client(host="127.0.0.1", port=4433, use_json=False)
#     # Set the duration of the test in seconds
#     client.run_test()

#######################################################################
# import asyncio as asc
# from connector import *
# import aioquic.asyncio
# from aioquic.asyncio.client import connect
# from aioquic.quic.configuration import QuicConfiguration
# import ssl

# class QUIC_client(client):
#     def __init__(self, host, port, use_json):
#         super().__init__(host, port, use_json)
#         self.traffic_type = "quic"
#         self.payload = b"p" * (self.quic_payload_size - 1) + b"\n"

#         self.config = QuicConfiguration(
#             is_client=True,
#             verify_mode=ssl.CERT_NONE,  # Disable certificate verification for testing
#         )

#     async def _maintask(self):
#         self._infomessage(f'Connecting to server {self.host}:{self.port}')
        
#         async with aioquic.asyncio.client.connect(
#             host=self.host, port=self.port, configuration=self.config
#         ) as client:
#             await client.wait_connected()
#             self._infomessage('Connection successful')
            
#             reader, writer = await client.create_stream()
#             self._infomessage('Stream created, now transmitting')
#             writer.write("192.168.1.108:5555\n".encode())
#             self._infomessage('Send: 127.0.0.1:5555\n')
#             while True:
#                 # Prompt the user for input
                
#                 user_input = input("Enter 'status' or 'process' or 'restart' (or 'exit' to quit): ").strip().lower()

#                 if user_input == "exit" or user_input == 'quit':
#                     self._infomessage('Exiting client...')
#                     break
#                 elif user_input in ("status", "process" , "restart"):
#                     # Send the user input to the server
#                     writer.write(f"{user_input}\n".encode())
#                     client.transmit()
#                     self._infomessage(f"Sent: {user_input}")

#                     # Wait for the server's response
#                     response = await reader.readline()
#                     self._infomessage(f"Received: {response.decode().strip()}")
#                 else:
#                     print("Invalid input. Please enter 'hello', 'goodbye', or 'exit'.")

#             # Close the connection
#             writer.write(b'STOP\n')
#             client.transmit()
#             client.close()
#             await client.wait_closed()
#             self._infomessage('Client finished')

#     def run_test(self):
#         loop = asc.get_event_loop()
#         loop.run_until_complete(self._maintask())

# async def udp_listener(port):
#     """Listen on a UDP port and print whatever is received."""
#     loop = asc.get_event_loop()
#     transport, protocol = await loop.create_datagram_endpoint(
#         lambda: UDPProtocol(),
#         local_addr=('0.0.0.0', 5555)
#     )
#     print(f"Listening on UDP port {port}...")

#     try:
#         while True:
#             await asc.sleep(3600)  # Keep the listener running
#     except asc.CancelledError:
#         transport.close()

# class UDPProtocol:
#     def __init__(self):
#         self.transport = None

#     def connection_made(self, transport):
#         self.transport = transport

#     def datagram_received(self, data, addr):
#         print(f"Received from {addr}: {data.decode()}")

#     def error_received(self, exc):
#         print(f"Error received: {exc}")

#     def connection_lost(self, exc):
#         print("Connection closed")

# if __name__ == "__main__":
#     # Set the server host, port, and JSON usage flag
#     client = QUIC_client(host="127.0.0.1", port=4433, use_json=False)
    
#     # Start the UDP listener on port 5555
#     loop = asc.get_event_loop()
#     udp_listener_task = loop.create_task(udp_listener(5555))
    
#     # Set the duration of the test in seconds
#     client.run_test()
    
#     # Cancel the UDP listener task when the QUIC client finishes
#     udp_listener_task.cancel()
#     loop.run_until_complete(udp_listener_task)



import asyncio
import threading
from connector import *
import aioquic.asyncio
from aioquic.asyncio.client import connect
from aioquic.quic.configuration import QuicConfiguration
from GUI import *
import logging
import ssl
import socket

class QUIC_client(client):
    def __init__(self, host, port, use_json):
        super().__init__(host, port, use_json)
        self.traffic_type = "quic"
        self.payload = b"p" * (self.quic_payload_size - 1) + b"\n"

        self.config = QuicConfiguration(
            is_client=True,
            verify_mode=ssl.CERT_NONE,  # Disable certificate verification for testing
        )

    def _maintask(self):
        self._infomessage(f'Connecting to server {self.host}:{self.port}')
        
        # Run the QUIC client in a separate thread
        def run_quic_client():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._quic_client_task())

        quic_thread = threading.Thread(target=run_quic_client)
        quic_thread.start()
        quic_thread.join()

    async def _quic_client_task(self):
        async with aioquic.asyncio.client.connect(
            host=self.host, port=self.port, configuration=self.config
        ) as client:
            await client.wait_connected()
            self._infomessage('Connection successful')
            
            reader, writer = await client.create_stream()
            self._infomessage('Stream created, now transmitting')
            writer.write("127.0.0.1:5555\n".encode())
            client.transmit()
            self._infomessage(f"Sent: 127.0.0.1:5555\n")
            while True:
                # Prompt the user for input
                
                user_input = input("Enter 'status' or 'process' or 'restart' (or 'exit' to quit): ").strip().lower()

                if user_input == "exit" or user_input == 'quit':
                    self._infomessage('Exiting client...')
                    break
                elif user_input in ("status", "process" , "restart"):
                    # Send the user input to the server
                    writer.write(f"{user_input}\n".encode())
                    client.transmit()
                    self._infomessage(f"Sent: {user_input}")

                    # Wait for the server's response
                    response = await reader.readline()
                    self._infomessage(f"Received: {response.decode().strip()}")
                else:
                    print("Invalid input. Please enter 'status', 'process', 'restart', or 'exit'.")

            # Close the connection
            writer.write(b'STOP\n')
            client.transmit()
            client.close()
            await client.wait_closed()
            self._infomessage('Client finished')

    def run_test(self):
        self._maintask()

logging.basicConfig(
        filename="udp_alerts.log",
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
def udp_listener(port):
    """Listen on a UDP port and print whatever is received."""

    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 5555))
    print(f"Listening on UDP port {port}...")

    try:
        while True:
            data, addr = sock.recvfrom(4096)  # Buffer size is 4096 bytes
            log_entry = f"Received from : {data.decode()}"
            # print(log_entry)
            logging.info(log_entry)
    except KeyboardInterrupt:
        print("UDP listener stopped.")
    finally:
        sock.close()


if __name__ == "__main__":
    # Set the server host, port, and JSON usage flag
    client = QUIC_client(host="127.0.0.1", port=4433, use_json=False)
    
    # Start the UDP listener in a separate thread
    udp_thread = threading.Thread(target=udp_listener, args=(5555,))
    udp_thread.daemon = True  # Daemonize thread to exit when the main program exits
    udp_thread.start()

    client.run_test()


    
    