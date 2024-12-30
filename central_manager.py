# import socket
# import threading
# import psutil  # برای دسترسی به اطلاعات سیستم (برای مصرف CPU، حافظه و لیست فرآیندها)

# # TCP Server to handle agent connections
# def handle_tcp_connection(client_socket):
#     print("New connection from:", client_socket.getpeername())
    
#     try:
#         while True:
#             # دریافت دستور از کلاینت (برای استعلام وضعیت یا ارسال دستورات)
#             data = client_socket.recv(1024)
#             if not data:
#                 break
#             command = data.decode('utf-8')
            
#             print(f"Received from agent: {command}")
            
#             # پردازش دستورات مختلف
#             if command == "GET_CPU_MEMORY":
#                 # استعلام وضعیت مصرف حافظه و CPU
#                 cpu_usage = psutil.cpu_percent(interval=1)  # مصرف CPU
#                 memory_usage = psutil.virtual_memory().percent  # مصرف حافظه
#                 response = f"CPU Usage: {cpu_usage}% | Memory Usage: {memory_usage}%"
            
#             elif command == "GET_RUNNING_PROCESSES":
#                 # استعلام تعداد برنامه‌های در حال اجرا
#                 processes = len(psutil.pids())
#                 response = f"Running Processes: {processes}"
            
#             elif command == "RESTART":
#                 # ارسال دستور restart به سیستم
#                 response = "System will restart now."
#                 # در اینجا می‌توان کدی برای restart کردن سیستم اضافه کرد.
            
#             # ارسال پاسخ به کلاینت
#             client_socket.send(response.encode('utf-8'))
    
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         try:
#             # بررسی و بستن اتصال
#             if not client_socket._closed:
#                 print(f"Connection closed with {client_socket.getpeername()}")
#             client_socket.close()
#         except Exception as e:
#             print(f"Error while closing the connection: {e}")

# # UDP Server to receive event notifications (like CPU load alerts)
# def handle_udp_events():
#     udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     udp_socket.bind(('0.0.0.0', 5000))  # Listen on all interfaces, port 5000
    
#     print("Server is listening for UDP events on port 5000...")
    
#     while True:
#         data, addr = udp_socket.recvfrom(1024)
#         print(f"Received event from {addr}: {data.decode('utf-8')}")

# # Function to start the server
# def start_server():
#     tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     tcp_server.bind(('0.0.0.0', 4000))  # TCP server on port 4000
#     tcp_server.listen(5)
    
#     print("Server listening on TCP port 4000...")

#     # Start UDP event listener in a separate thread
#     udp_thread = threading.Thread(target=handle_udp_events)
#     udp_thread.daemon = True
#     udp_thread.start()

#     while True:
#         # Accept TCP connections from agents
#         client_socket, addr = tcp_server.accept()
#         tcp_thread = threading.Thread(target=handle_tcp_connection, args=(client_socket,))
#         tcp_thread.start()

# if __name__ == "__main__":
#     start_server()
#########################################################
# import socket
# import threading

# # Constants
# TCP_PORT = 5000
# UDP_PORT = 5001
# BUFFER_SIZE = 1024

# def handle_udp_alerts():
#     """Handle incoming UDP alerts from agents."""
#     udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     udp_socket.bind(("0.0.0.0", UDP_PORT))
#     print(f"Listening for UDP alerts on port {UDP_PORT}...")

#     while True:
#         message, addr = udp_socket.recvfrom(BUFFER_SIZE)
#         print(f"Alert from {addr}: {message.decode()}")

# def handle_agent_commands(agent_ip):
#     """Interact with a connected agent over TCP."""
#     tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     tcp_socket.connect((agent_ip, TCP_PORT))

#     while True:
#         print("\nCommands:")
#         print("1. Get system status")
#         print("2. Get running process count")
#         print("3. Restart system")
#         print("4. Exit")

#         choice = input("Enter your choice: ")

#         if choice == "1":
#             command = "GET_STATUS"
#         elif choice == "2":
#             command = "GET_PROCESS_COUNT"
#         elif choice == "3":
#             command = "RESTART"
#         elif choice == "4":
#             print("Exiting...")
#             break
#         else:
#             print("Invalid choice. Please try again.")
#             continue

#         # Send command to agent
#         tcp_socket.send(command.encode())

#         if choice == "3":
#             print("System restart command sent. Connection will close.")
#             break

#         # Receive response
#         response = tcp_socket.recv(BUFFER_SIZE).decode()
#         print(f"Response from agent: {response}")

#     tcp_socket.close()

# def main():
#     """Main function to manage agents and handle alerts."""
#     # Start the UDP alert listener in a separate thread
#     threading.Thread(target=handle_udp_alerts, daemon=True).start()

#     while True:
#         agent_ip = input("Enter the IP address of the agent to connect to (or 'exit' to quit): ")
#         if agent_ip.lower() == "exit":
#             print("Exiting central manager.")
#             break

#         try:
#             handle_agent_commands(agent_ip)
#         except Exception as e:
#             print(f"Error connecting to agent: {e}")

# if __name__ == "__main__":
#     main()

import socket
import threading
import time
import json
# Constants
TCP_PORT = 5005
UDP_PORT = 5001
BUFFER_SIZE = 1024

# Load agent IPs from a file
AGENT_FILE = "agents.txt"

def handle_udp_alerts():
    """Handle incoming UDP alerts from agents."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("0.0.0.0", UDP_PORT))
    print(f"Listening for UDP alerts on port {UDP_PORT}...")

    while True:
        message, addr = udp_socket.recvfrom(BUFFER_SIZE)
        print(f"Alert from {addr}: {message.decode()}")

def handle_agent_commands(client_socket, addr):
    """Handle commands to a connected agent over TCP."""
    print(f"Connected to agent at {addr}")
    while True:
        try:
            print("\nCommands:")
            print("1. Get system status")
            print("2. Get running process count")
            print("3. Restart system")
            print("4. Disconnect")

            choice = input("Enter your choice: ")

            if choice == "1":
                command = "GET_STATUS"
            elif choice == "2":
                command = "GET_PROCESS_COUNT"
            elif choice == "3":
                command = "RESTART"
            elif choice == "4":
                print("Disconnecting from agent...")
                break
            else:
                print("Invalid choice. Please try again.")
                continue

            # Send command to agent
            client_socket.send(command.encode())

            if choice == "3":
                print("System restart command sent. Connection will close.")
                break

            # Receive response
            response = client_socket.recv(BUFFER_SIZE).decode()
            print(f"Response from agent: {response}")

        except Exception as e:
            print(f"Error communicating with agent {addr}: {e}")
            break

    client_socket.close()

def connect_to_agents():
    """Connect to agents listed in the agents file."""
    try:
        with open(AGENT_FILE, "r") as file:
            agent_ips = [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"Agent file '{AGENT_FILE}' not found. Please create it with agent IPs.")
        return

    for agent_ip in agent_ips:
        try:
            print(f"Attempting to connect to agent at {agent_ip}:{TCP_PORT}...")
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.connect((agent_ip, TCP_PORT))
            threading.Thread(target=handle_agent_commands, args=(tcp_socket, agent_ip)).start()
        except Exception as e:
            print(f"Failed to connect to agent at {agent_ip}: {e}")



class Server:  
    def __init__(self, IP, UDP_PORT) -> None:  
        self.tdp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.tdp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
        # self.listener.bind((IP, PORT))  
        # self.listener.listen(5)  # Allow up to 5 queued connections
        # print(f'[+] Waiting for incoming connections on {IP}:{PORT}')  
        

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(("0.0.0.0", UDP_PORT))
        print(f"[+] Listening for UDP alerts on {IP}:{UDP_PORT}")

        self.connections = []  # Store connections
        self.addresses = []     # Store client addresses
        self.active_session_index = None



    def connect_to_clients(self , port):  
        try:
            with open(AGENT_FILE, "r") as file:
                agent_ips = [line.strip() for line in file.readlines() if line.strip()]
        except FileNotFoundError:
            print(f"Agent file '{AGENT_FILE}' not found. Please create it with agent IPs.")
            return
        
        for ip in agent_ips:  
            try:  
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
                client_socket.connect((ip, port))  
                self.connections.append(client_socket)  
                self.addresses.append((ip, port))
                print(f"Connected to client at {ip}:{port}")  
            except Exception as e:  
                print(f"Failed to connect to {ip}:{port} - {e}") 

        self.select_session(0)

    def select_session(self , session=1):
        print("\n[+] Available sessions:")
        for i, address in enumerate(self.addresses):
            print(f'{i} - {address}')
        if session != 0:
            choice = int(input("[+] Choose a session to interact with (by number): "))
        else:
            choice = 0
        self.connection = self.connections[choice]
        self.active_session_index = choice
        print(f"[+] You are now interacting with {self.addresses[choice]}")
        
    # def accept_connections(self):
    #     while True:
    #         connection, address = self.listener.accept()
    #         print(f'[+] Connection attempt from {address}')
            
    #         # Check if this IP address already has a connection
    #         for i, addr in enumerate(self.addresses):
    #             if addr[0] == address[0]:  # Compare IP addresses
    #                 print(f'[!] Closing existing connection from {addr}')
    #                 self.connections[i].close()
    #                 self.remove_connection(i)
    #                 break  # Exit loop after removing old connection

    #         # Accept the new connection
    #         self.connections.append(connection)
    #         self.addresses.append(address)
    #         print(f'[+] Got a new connection from {address}')  
            
    #         # Automatically select the new connection if no session is active
    #         if self.active_session_index is None:  
    #             self.select_session(len(self.connections) - 1)

    def reliable_send(self, data: str):  
        json_data = json.dumps(data).encode('utf-8')  
        self.connection.send(json_data)  

    def reliable_receive(self):  
        json_data = ""
        while True:
            try:
                part = self.connection.recv(1024).decode('utf-8')
                print(part)
                if not part:  # If the connection is lost, remove it
                    self.remove_connection(self.active_session_index)
                    return None
                json_data += part
                return json.loads(json_data)  
            except ValueError:
                continue

    def execute_remotely(self, command):  
        self.reliable_send(command)  
        return self.reliable_receive()  

    def write_file(self, path, content):
        with open(path, 'wb') as file:
            file.write(base64.b64decode(bytes(content.encode('utf-8'))))
        return "[+] Download successful."

    def read_file(self, path):
        with open(path, 'rb') as file:
            return base64.b64encode(file.read()).decode('utf-8')
    
    def handle_udp_alerts(self):
        """Handle incoming UDP alerts from agents."""
        while True:
            message, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
            print(f"Alert from {addr}: {message.decode()}")
            
    def remove_connection(self, index):
        print(f"[-] Connection to {self.addresses[index]} was lost.")
        del self.connections[index]
        del self.addresses[index]
        self.active_session_index = None
        if self.connections:
            self.select_session()
        else:
            print("[-] No active sessions available.")
    def handle_agent_commands(self):  
        # print("[+] Waiting for a new connection or active session...")
        
        while True:  
            if self.active_session_index is None:
                continue
            # if self.active_session_index is None:
            #     continue
            command = input('>> ')  
            command = command.split(" ")
            if command[0] == "list":
                self.select_session()
                continue
            
            try:
                if command[0] == "1":
                    command = ["GET_STATUS"]

                elif command[0] == "2":
                    command = ["GET_PROCESS_COUNT"]

                elif command[0] == "3":
                    command = ["RESTART"]

                elif command[0] == "4":
                    print("Disconnecting from agent...")
                    break

                elif command[0] == 'upload':
                    file_content = self.read_file(command[1])
                    command.append(file_content)
                    
                result = self.execute_remotely(command)
                
                if result is None:  # Connection was lost, select a new session
                    continue

                if command[0] == 'exit':
                    print(result)
                    self.connection.close()
                    self.remove_connection(self.active_session_index)
                    continue

                if command[0] == 'download' and "[-] Error" not in result:
                    result = self.write_file(" ".join(command[1:]), result)

            except Exception as e:
                result = f"[-] Error: {str(e)}"

            print(result)

    def start(self):
        # connection_thread = threading.Thread(target=self.accept_connections)
        udp_connection_thread = threading.Thread(target=self.handle_udp_alerts).start()
        self.connect_to_clients(port=TCP_PORT)
        

        # connection_thread.daemon = True
        # connection_thread.start()
        
        self.handle_agent_commands()



def main():
    """Main function to manage agents and handle alerts."""
    server = Server('0.0.0.0' , 4856)

    server.start()

    # Start the UDP alert listener in a separate thread
    # threading.Thread(target=handle_udp_alerts, daemon=True).start()

    # Connect to agents
    # connect_to_agents()

    # Keep the main thread alive
    # while True:
    #     try:
    #         time.sleep(1)
    #     except KeyboardInterrupt:
    #         print("Shutting down central manager.")
    #         break

if __name__ == "__main__":
    main()
