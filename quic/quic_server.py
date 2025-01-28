from connector import *  # Base classes: `client` and `server`
import asyncio as asc
from connector import *
import os , psutil
import aioquic.asyncio
from aioquic.asyncio.client import connect
# from aioquic.asyncio.server import serve
# from aioquic.quic.configuration import QuicConfiguration
from aioquic.asyncio.server import serve
from aioquic.quic.configuration import QuicConfiguration
import ssl
import socket
import platform
import subprocess
import threading

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

def get_ip_address():
    system = platform.system().lower()
    
    if system == "linux":
        try:
            result = subprocess.run(["hostname", "-I"], capture_output=True, text=True, check=True)
            ip_address = result.stdout.strip().split()[0]
            return ip_address , system
        except Exception as e:
            print(f"Unable to get IP address on Linux: {e}")
    
    elif system == "windows":
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


class QUIC_server(server):
    def __init__(self, port, interval, use_json):
        super().__init__(port, interval, use_json)
        self.traffic_type = "quic"
        self.actuall_ip , self.system = get_ip_address()
        self.config = QuicConfiguration(is_client=False)
        self.config.load_cert_chain("server_cert.pem", "server_key.pem")  # Provide certificate files
        self.loop = asc.get_event_loop()
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_port = None
        self.central_ip = None
        
    def _streamhandler(self, reader, writer):
        self._infomessage(message="Stream created")
        self.currentstreamtask = self.loop.create_task(
            self._currentstreamhandler(reader, writer)
        )

    async def _currentstreamhandler(self, reader, writer):
        self._infomessage('Stream handler started')
        line = await reader.readline()
        # print(line.decode())
        line = line.decode().strip()
        self._infomessage(f'Received: {line}')
        self.central_ip = line.split(':')[0]
        self.udp_port = int(line.split(':')[1])
        print(self.central_ip,self.udp_port)
        while True:
            # Read message from the client
            line = await reader.readline()
            
            if line == b'':
                continue
                # self._infomessage('Connection interrupted! Exiting', is_error=True)
                # return
            elif line == b'STOP\n':
                self._infomessage(f'Received: {line}')
                self._infomessage('Received STOP, finishing server...')
                return
            elif line == b'status\n':
                self._infomessage(f'Received: {line}')
                status = get_system_status()
                output = f"CPU: {status['cpu_usage']}%, Memory: {status['memory_usage']}%\n"
                writer.write(output.encode())
                # await writer.drain()

            elif line == b'process\n':
                self._infomessage(f'Received: {line}')
                count = get_running_process_count()
                output = f"Running processes: {count}\n"
                writer.write(output.encode())
                # await writer.drain()


            elif line == b'restart\n':
                self._infomessage(f'Received: {line}')
                output = "Restarting system...\n"
                self._infomessage(f'Sent: {output}')
                writer.write(output.encode())
                restart_system('123225' , system= self.system)
                return

            else:
                writer.write(b'Unknown message received\n')
                self._infomessage(f'Unknown message received: {line.decode().strip()}')
                continue

            self._infomessage(f'Sent: {output}')
            # Send any pending data
            # writer.drain()

    def udp_event_sender(self):
            print('haha')
            while True:
                if self.udp_port:
                    cpu_usage = psutil.cpu_percent(interval=1)
                    if cpu_usage > 1:  # Example threshold for high CPU usage
                        # address = self.udp_socket.getsockname()
                        message = f"{(self.actuall_ip,self.udp_port)} : CRITICAL: CPU usage is {cpu_usage}%"
                        # print(f'sending : CRITICAL: CPU usage is {cpu_usage}%')
                        self._infomessage(f'sending : CRITICAL: CPU usage is {cpu_usage}%')
                        self.udp_socket.sendto(message.encode(), (self.central_ip, self.udp_port))
                time.sleep(5)

    def listen(self):
        super().listen()
        try:
            self.server_task = self.loop.create_task(
                serve(
                    host="0.0.0.0",
                    port=self.port,
                    configuration=self.config,
                    stream_handler=self._streamhandler,
                )
            )
            self.loop.run_forever()
        except asc.CancelledError:
            print("Cancelled error")


if __name__ == "__main__":
    # Set the port, interval, and JSON usage flag
    server = QUIC_server(port=4433, interval=1, use_json=False)

    udp_thread = threading.Thread(target=server.udp_event_sender)
    udp_thread.daemon = True  # Daemonize thread to exit when the main program exits
    udp_thread.start()

    server.listen()