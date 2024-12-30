# import socket
# import time
# import random
# import psutil  # برای دسترسی به اطلاعات سیستم (برای مصرف CPU و حافظه)
# import os
# import threading

# # Function to send events like high CPU load
# def generate_events(udp_socket, server_ip, server_port):
#     while True:
#         time.sleep(random.randint(5, 10))  # Simulate event at random intervals
#         cpu_usage = psutil.cpu_percent(interval=1)
#         if cpu_usage > 80:  # For example, if CPU usage is higher than 80%
#             event_message = f"High CPU Load: {cpu_usage}%"
#             udp_socket.sendto(event_message.encode('utf-8'), (server_ip, server_port))
#             print(f"Sent UDP event to server: {event_message}")

# # Function to send system status to the central server
# def send_system_status(tcp_socket):
#     while True:
#         # ارسال اطلاعات وضعیت مصرف CPU و حافظه
#         tcp_socket.send("GET_CPU_MEMORY".encode('utf-8'))
#         data = tcp_socket.recv(1024)
#         print(f"System Status: {data.decode('utf-8')}")
        
#         # ارسال تعداد برنامه‌های در حال اجرا
#         tcp_socket.send("GET_RUNNING_PROCESSES".encode('utf-8'))
#         data = tcp_socket.recv(1024)
#         print(f"Running Processes: {data.decode('utf-8')}")
        
#         time.sleep(5)  # ارسال وضعیت به صورت دوره‌ای

# # Function to restart the system when requested
# def restart_system(tcp_socket):
#     while True:
#         tcp_socket.send("RESTART".encode('utf-8'))
#         data = tcp_socket.recv(1024)
#         print(f"Response: {data.decode('utf-8')}")
#         if "System will restart now" in data.decode('utf-8'):
#             print("Restarting the system...")
#             os.system("shutdown /r /t 1")  # Restart Windows system
#             break

# # Function to handle TCP connection and communication with server
# def handle_tcp_connection():
#     tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     tcp_socket.connect(('127.0.0.1', 4000))  # Connect to the server's TCP port

#     try:
#         # ارسال وضعیت سیستم به سرور
#         system_status_thread = threading.Thread(target=send_system_status, args=(tcp_socket,))
#         system_status_thread.daemon = True
#         system_status_thread.start()
        
#         # مدیریت دستور restart
#         restart_thread = threading.Thread(target=restart_system, args=(tcp_socket,))
#         restart_thread.daemon = True
#         restart_thread.start()

#         # با سرور در ارتباط باشید و منتظر دریافت دستورات باشید
#         while True:
#             time.sleep(1)
    
#     finally:
#         tcp_socket.close()

# # Function to start the agent
# def start_agent():
#     # UDP socket for sending event notifications
#     udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     server_ip = '127.0.0.1'  # Server IP address
#     server_udp_port = 5000  # Server's UDP port
    
#     # Start event generation in a separate thread
#     udp_thread = threading.Thread(target=generate_events, args=(udp_socket, server_ip, server_udp_port))
#     udp_thread.daemon = True
#     udp_thread.start()

#     # Handle TCP communication with the server
#     handle_tcp_connection()

# if __name__ == "__main__":
#     start_agent()
import socket
import threading
import psutil
import os
import time
import json
import sys 
# Constants
TCP_PORT = 5005
UDP_PORT = 5001
BUFFER_SIZE = 1024

def get_system_status():
    """Get the system's CPU and memory usage."""
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    return {
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage
    }

def get_running_process_count():
    """Get the number of running processes."""
    return len(psutil.pids())

def restart_system():
    """Restart the system."""
    os.system("shutdown /r /t 1")

def udp_event_sender():
    """Send critical events to the central manager via UDP."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        cpu_usage = psutil.cpu_percent(interval=1)
        if cpu_usage > 80:  # Example threshold for high CPU usage
            message = f"CRITICAL: CPU usage is {cpu_usage}%"
            udp_socket.sendto(message.encode(), ("<broadcast>", UDP_PORT))
        time.sleep(5)  # Check every 5 seconds

# def tcp_handler(client_socket):
#     """Handle commands from the central manager."""
#     while True:
#         try:
#             data = client_socket.recv(BUFFER_SIZE).decode()
#             if not data:
#                 break

#             print(f"Received command: {data}")
#             if data == "GET_STATUS":
#                 status = get_system_status()
#                 response = f"CPU: {status['cpu_usage']}%, Memory: {status['memory_usage']}%"
#             elif data == "GET_PROCESS_COUNT":
#                 count = get_running_process_count()
#                 response = f"Running processes: {count}"
#             elif data == "RESTART":
#                 response = "Restarting system..."
#                 client_socket.send(response.encode())
#                 client_socket.close()
#                 restart_system()
#                 return
#             else:
#                 response = "Unknown command."

#             client_socket.send(response.encode())
#         except Exception as e:
#             print(f"Error: {e}")
#             break

#     client_socket.close()

# def start_tcp_server():
#     """Start the TCP server for the agent."""
#     tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     tcp_socket.bind(("0.0.0.0", TCP_PORT))
#     tcp_socket.listen(1)
#     print(f"Agent listening for central manager connection on port {TCP_PORT}...")

#     while True:
#         client_socket, addr = tcp_socket.accept()
#         print(f"Connected by central manager from {addr}")
#         tcp_handler(client_socket)


class Agent:
    def __init__(self , IP , tcp_port , udp_port) -> None:
        # Create a socket object
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((IP, tcp_port))
        self.tcp_socket.listen(1)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_port = udp_port

        print(f'[+] Waiting for incoming connections on {IP}:{tcp_port}')
        
        # while True:
        #     client_socket, addr = self.tcp_socket.accept()
        #     print(f'[+] Connection attempt from {addr}')
        #     self.run()
        # Connect to the attacker's machine
        # self.connection.connect((ip, port))
        # print('connected')


    def reliable_send(self, data: str):  
        json_data = json.dumps(data).encode('utf-8') 
        print(json_data) 
        self.connection.send(json_data)  

    # def reliable_receive(self):  
    #     json_data = ""
    #     while True:
    #         try:
    #             json_data = json_data + self.tcp_socket.recv(1024).decode('utf-8')  # Decode from bytes  
    #             return json.loads(json_data)  # Fixed to use json.loads instead of json.load  
    #         except ValueError:
    #             continue

    def reliable_receive(self):  
        json_data = ""
        while True:
            try:
                part = self.connection.recv(1024).decode('utf-8')
                if not part:  # If the connection is lost, remove it
                    self.remove_connection(self.active_session_index)
                    return None
                json_data += part
                return json.loads(json_data)  
            except ValueError:
                continue
    
    def udp_event_sender(self):
        """Send critical events to the central manager via UDP."""
        # udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            cpu_usage = psutil.cpu_percent(interval=1)
            if cpu_usage > 80:  # Example threshold for high CPU usage
                message = f"CRITICAL: CPU usage is {cpu_usage}%"
                self.udp_socket.sendto(message.encode(), ("<broadcast>", self.udp_port))
            time.sleep(5)  # Check every 5 seconds

    def tcp_handler(self):
        # prersian = subprocess.call('chcp 65001', shell=True)
        # print(prersian)
        # print("[+] Waiting for a new connection or active session...")
        client_socket, addr = self.tcp_socket.accept()
        print(f'[+] Connection attempt from {addr}')
        self.connection = client_socket
        while True:
            
            command = self.reliable_receive()
            try:
                print(command)
                if command[0] == 'exit':
                    self.reliable_send('exited')
                    self.tcp_socket.close()
                    sys.exit()
                elif command[0] == "GET_STATUS":
                    status = get_system_status()
                    output = f"CPU: {status['cpu_usage']}%, Memory: {status['memory_usage']}%"


                elif command[0] == "GET_PROCESS_COUNT":
                    count = get_running_process_count()
                    output = f"Running processes: {count}"
                elif command[0] == "RESTART":
                    output = "Restarting system..."
                    self.reliable_send(output.decode(errors='ignore'))
                    self.tcp_socket.close()
                    restart_system()
                    return
                
                else:
                    output = "[-] Error".encode()

                
                print(output)
                # print(output.decode(errors='ignore'))
                # output =output.encode()
                self.reliable_send(output)

            except Exception:
                output = "[-] Error"
                self.reliable_send(output)


    def start(self):
        tcp_connection_thread = threading.Thread(target=self.tcp_handler)
        udp_connection_thread = threading.Thread(target=self.udp_event_sender)

        tcp_connection_thread.start()
        udp_connection_thread.start()

        tcp_connection_thread.join()
        udp_connection_thread.join()


if __name__ == "__main__":
    # Start UDP sender in a separate thread
    # threading.Thread(target=udp_event_sender, daemon=True).start()
    agent = Agent("172.17.35.70" , TCP_PORT , UDP_PORT)
    agent.start()
    # Start the TCP server
    # start_tcp_server()


