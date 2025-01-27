import socket
import threading
import time
import json
import logging
from datetime import datetime
import base64
from GUI import *


TCP_PORT = 5008
UDP_PORT = 50162
BUFFER_SIZE = 1024
LOG_FILE = "udp_alerts.log"


AGENT_FILE = "agents.txt"

class Client:
    def __init__(self , IP , PORT) -> None:
        self.addresse = (IP ,PORT)
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.connection.settimeout(3)
        self.connection.connect((IP , PORT))
        self.commands = {}



class Server:  
    def __init__(self, IP, UDP_PORT) -> None:  
        
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = IP
        self.udp_port = UDP_PORT
        self.udp_socket.bind(('0.0.0.0', UDP_PORT)) 
        print(f"[+] Listening for UDP alerts on 0.0.0.0:{UDP_PORT}")
        self.clients = []
        self.active_session_index = None


        logging.basicConfig(
            filename="udp_alerts.log",
            level=logging.INFO,
            format="%(asctime)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


    def connect_to_clients(self , port , IP=None):  
        
        if not IP:
            try:
                with open(AGENT_FILE, "r") as file:
                    agent_ips = [line.strip() for line in file.readlines() if line.strip()]
            except FileNotFoundError:
                print(f"Agent file '{AGENT_FILE}' not found. Please create it with agent IPs.")
                return
            except Exception as e:
                print(f"An error occurred while reading the agent file: {e}")
                return
            
            print(agent_ips)
            for ip in agent_ips:  
                try:  
                    client = Client(ip, port)
                    self.clients.append(client)
                    self.connection = client.connection
                    self.reliable_send(['inf', self.ip, self.udp_port])
                    
                    print(f"Connected to client at {ip}:{port}")  
                except Exception as e:  
                    print(f"Failed to connect to {ip}:{port} - {e}")
            self.select_session(0) 

        else:
            try:
                client = Client(IP, port)
                self.clients.append(client)
                self.reliable_send(['inf', self.ip, self.udp_port])
                print(f"Connected to client at {IP}:{port}")  
            except Exception as e:  
                print(f"Failed to connect to {IP}:{port} - {e}") 

            self.select_session(len(self.clients)-1)
        

    def select_session(self , session=1):
        try:
            i = 0
            print("\n[+] Available sessions:")
            for client in self.clients:
                print(f'{i} - {client.addresse[0]} - {client.addresse[1]}')
                i += 1
            if i>0 :
                
                if session != 0:
                    choice = int(input("[+] Choose a session to interact with (by number): "))
                else:
                    choice = 0
                self.connection = self.clients[choice].connection
                self.active_session_index = choice
                print(f"[+] You are now interacting with {self.clients[choice].addresse}")
            else:
                print('[-] there is no session')
        except:
            print('[-] there is no session')
    def reliable_send(self, data: str):  
        json_data = json.dumps(data).encode('utf-8')  
        self.connection.send(json_data)  

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
        while True:
            message, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
            decoded_message = message.decode()
            log_entry = f"Alert from  {decoded_message}" #{addr}:
            logging.info(log_entry)

            
    def remove_connection(self, index):
        del self.clients[index]
        if self.active_session_index == index:
            self.active_session_index = None
            if self.clients:
                self.select_session()
            else:
                print("[-] No active sessions available.")


    def check_connections(self):
        while True:
            for agent in self.clients:
                try:
                    agent.connection.getpeername()
                except:
                    log = f"\n[-] connection to {agent.addresse} was lost\n>> "
                    print(log)
                    
                    self.remove_connection(self.clients.index(agent))
        
            time.sleep(10)

    def handle_agent_commands(self):  
        
        while True:  
            command = input('>> ')  
            command = command.split(" ")
            
            try:
                if command[0] == "list":
                    self.select_session()
                    continue
                elif command[0]== 'reconnect':
                    if command[1] == '-a' or command[1]=='--all':
                        self.connect_to_clients(port=TCP_PORT)
                    if command[1]:
                        self.connect_to_clients(port=TCP_PORT , IP=command[1])
                    continue
                elif command[0] == "status":
                    command = ['1']

                elif command[0] == "process":
                    command = ["2"]

                elif command[0] == "restart":
                    command = ["3"]

                elif command[0] == 'upload':
                    file_content = self.read_file(command[1])
                    command.append(file_content)

                

                result = self.execute_remotely(command)
                
                if result is None:  # Connection was lost, select a new session
                    continue
                
                elif command[0] == 'close':
                    print(result)
                    self.connection.close()
                    self.remove_connection(self.active_session_index)
                    continue

                if command[0] == 'download' and "[-] Error" not in result:
                    result = self.write_file(" ".join(command[1:]), result)

                if result != '[-] Error':
                    result = '[+] ' + result
            except Exception as e:
                result = f"[-] Error: {str(e)}"

            print(result)

    def start(self):
        
        udp_connection_thread = threading.Thread(target=self.handle_udp_alerts).start()
        self.connect_to_clients(port=TCP_PORT)
        connection_thread = threading.Thread(target=self.handle_agent_commands).start()
        check_connections = threading.Thread(target=self.check_connections).start()
        


def main():
    server = Server('192.168.31.1' , UDP_PORT)
    server.start()
    
    root = tk.Tk()
    app = LogMonitorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
