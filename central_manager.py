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

            choice = input("Enter your choice: ").lower()
            
            if choice == 'help':
                print("\nCommands:")
                print("1. Get system status")
                print("2. Get running process count")
                print("3. Restart system")
                print("4. Disconnect")
                continue

            elif choice == "status":
                command = "1"
            elif choice == "process_count":
                command = "2"
            elif choice == "restart":
                command = "3"
            elif choice == "disconnect":
                print("4")
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
        
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((IP, UDP_PORT))
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
                    command = ['1']#["GET_STATUS"]

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
        
        udp_connection_thread = threading.Thread(target=self.handle_udp_alerts).start()
        self.connect_to_clients(port=TCP_PORT)
        connection_thread = threading.Thread(target=self.handle_agent_commands).start()

        # connection_thread.daemon = True
        # connection_thread.start()
        
        # self.handle_agent_commands()



def main():
    """Main function to manage agents and handle alerts."""
    server = Server('127.0.0.1' , UDP_PORT)

    server.start()

if __name__ == "__main__":
    main()
