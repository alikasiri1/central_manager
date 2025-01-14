import socket
import threading
import psutil
import os
import time
import json
import sys 
# Constants
TCP_PORT = 5007
# UDP_PORT = 5001
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

class Agent:
    def __init__(self , IP , tcp_port ) -> None:
        # Create a socket object
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((IP, tcp_port))
        self.tcp_socket.listen(1)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 
        self.udp_port = None
        self.server_ip = None

        print(f'[+] Waiting for incoming connections on {IP}:{tcp_port}')

    def reliable_send(self, data: str):  
        json_data = json.dumps(data).encode('utf-8') 
        self.connection.send(json_data)  


    def reliable_receive(self):  
        json_data = ""
        while True:
            try:
                part = self.connection.recv(1024).decode('utf-8')
                # if not part:  # If the connection is lost, remove it
                #     self.remove_connection(self.active_session_index)
                #     return None
                json_data += part
                return json.loads(json_data)  
            except ValueError:
                continue
    
    def udp_event_sender(self):
        """Send critical events to the central manager via UDP."""
        # udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            if self.udp_port:
                cpu_usage = psutil.cpu_percent(interval=1)
                if cpu_usage > 1:  # Example threshold for high CPU usage
                    message = f"CRITICAL: CPU usage is {cpu_usage}%"
                    print(f'sending {message}')
                    self.udp_socket.sendto(message.encode(), (self.server_ip, self.udp_port))
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
                print(f'>> {command} ',end='')
                if command[0] == 'inf':
                    self.server_ip = command[1]
                    self.udp_port = command[2]
                    continue
                
                elif command[0] == 'exit':
                    self.reliable_send('exited')
                    self.tcp_socket.close()
                    sys.exit()

                elif command[0] == "1":
                    status = get_system_status()
                    output = f"CPU: {status['cpu_usage']}%, Memory: {status['memory_usage']}%"


                elif command[0] == "2":
                    count = get_running_process_count()
                    output = f"Running processes: {count}"
                elif command[0] == "3":
                    output = "Restarting system..."
                    self.reliable_send(output.decode(errors='ignore'))
                    self.tcp_socket.close()
                    restart_system()
                    return
                
                else:
                    output = "[-] Error".encode()

                
                print(output)
                self.reliable_send(output)

            except Exception:
                output = "[-] Error"
                self.reliable_send(output)


    def start(self):
        tcp_connection_thread = threading.Thread(target=self.tcp_handler)
        udp_connection_thread = threading.Thread(target=self.udp_event_sender)
        udp_connection_thread.start()
        

        tcp_connection_thread.start()
        udp_connection_thread.join()

        tcp_connection_thread.join()
        


if __name__ == "__main__":
    agent = Agent("0.0.0.0" , TCP_PORT)
    agent.start()


