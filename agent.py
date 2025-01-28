# import socket
# import threading
import socket
import threading
import psutil
import os
import time
import platform
import json
import sys
import subprocess
import base64
import signal


TCP_PORT = 5010
BUFFER_SIZE = 1024

# Shared flag to signal threads to stop
stop_event = threading.Event()
def get_ip_address():
    system = platform.system().lower()
    
    if system == "linux":
        # Use the 'hostname' command to get the IP address on Linux
        try:
            result = subprocess.run(["hostname", "-I"], capture_output=True, text=True, check=True)
            ip_address = result.stdout.strip().split()[0]
            return ip_address , system
        except Exception as e:
            print(f"Unable to get IP address on Linux: {e}")
    
    elif system == "windows":
        # Use the 'ipconfig' command to get the IP address on Windows
        try:
            result = subprocess.run(["ipconfig"], capture_output=True, text=True, check=True)
            output = result.stdout
            # Find the IPv4 address in the output
            for line in output.splitlines():
                if "IPv4 Address" in line:
                    ip_address = line.split(":")[1].strip()
                    return ip_address , system
            print("No IPv4 address found in ipconfig output.")
        except Exception as e:
            print(f"Unable to get IP address on Windows: {e}")
    else:
        print(f"Unsupported operating system: {system}")

def get_system_status():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    return {
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage
    }

def get_running_process_count():
    return len(psutil.pids())

def restart_system(password , system):
    if system == 'linux':
        os.system(f"echo {password} | sudo -S init 6")
    else:
        command = 'shutdown /r /t 0'
        os.system( command , shell=True)

class Agent:
    def __init__(self, IP, tcp_port):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((IP, tcp_port))
        self.tcp_socket.listen(1)
        self.actuall_ip , self.system = get_ip_address()
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
                json_data += part
                return json.loads(json_data)
            except ValueError:
                continue

    def udp_event_sender(self):
        while not stop_event.is_set():
            if self.udp_port:
                cpu_usage = psutil.cpu_percent(interval=1)
                if cpu_usage > 0.5:  # Example threshold for high CPU usage
                    # address = self.udp_socket.getsockname()
                    message = f"{(self.actuall_ip,self.udp_port)} : CRITICAL: CPU usage is {cpu_usage}%"
                    print(f'sending : CRITICAL: CPU usage is {cpu_usage}%')
                    self.udp_socket.sendto(message.encode(), (self.server_ip, self.udp_port))
            time.sleep(5)  

    def excute_command(self , command):
        return subprocess.check_output(command , shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    

    def read_file(self , path):
        with open(path , 'rb') as file:
            return base64.b64encode(file.read())

    def write_file(self , path , content):
        with open(path , 'wb') as file:
            file.write(base64.b64decode(bytes(content.encode('utf-8'))))
        return "[+] Upload succesful.".encode('utf-8')
    
    def change_working_directory(self , path):
        os.chdir(path)
        return "[+] changing working directory to " + path
    
    def tcp_handler(self):
        client_socket, addr = self.tcp_socket.accept()
        print(f'[+] Connection attempt from {addr}')
        self.connection = client_socket

        while not stop_event.is_set():
            try:
                command = self.reliable_receive()
                print(f'>> {command} ', end='')

                if command[0] == 'inf':
                    self.server_ip = command[1]
                    self.udp_port = command[2]
                    continue

                elif command[0] == 'close':
                    self.reliable_send('closed')
                    stop_event.set()  # Signal all threads to stop
                    self.tcp_socket.close()
                    sys.exit(0)  

                elif command[0] == "1":
                    status = get_system_status()
                    output = f"CPU: {status['cpu_usage']}%, Memory: {status['memory_usage']}%"

                elif command[0] == "2":
                    count = get_running_process_count()
                    output = f"Running processes: {count}"

                elif command[0] == "3":
                    output = "Restarting system..."
                    self.reliable_send(output)
                    self.tcp_socket.close()
                    restart_system(command[1] , system= self.system)
                    return
                
                elif command[0] == 'cd' and len(command)>1:
                    self.change_working_directory(" ".join(command[1:]))
                    output = self.excute_command("cd")
                    output = output.decode(errors='ignore')

                elif command[0] == 'download':
                    output = self.read_file(" ".join(command[1:]))
                    output = output.decode(errors='ignore')

                elif command[0] == 'upload':
                    output = self.write_file(command[1] , command[2])
                    output = output.decode(errors='ignore')

                else:
                    output = self.excute_command(command)
                    output = output.decode(errors='ignore')
                # else:
                #     output = "[-] Error"

                print(output)
                self.reliable_send(output)

            except Exception as e:
                print(f"Error: {e}")
                output = "[-] Error"
                self.reliable_send(output)


    def start(self):
        tcp_connection_thread = threading.Thread(target=self.tcp_handler)
        udp_connection_thread = threading.Thread(target=self.udp_event_sender)

        udp_connection_thread.start()
        tcp_connection_thread.start()

        udp_connection_thread.join()
        tcp_connection_thread.join()

        # Clean up resources
        self.tcp_socket.close()
        self.udp_socket.close()


if __name__ == "__main__":
    agent = Agent("0.0.0.0", TCP_PORT)
    agent.start()
