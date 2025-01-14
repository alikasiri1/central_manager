# import tkinter as tk
# from tkinter import ttk
# import threading
# import os
# import time
# import re

# LOG_FILE = "udp_alerts.log"

# class LogMonitorApp:
#     def __init__(self, master):
#         self.master = master
#         self.master.title("Log Monitor")
#         self.master.geometry("1000x600")

#         # Data storage
#         self.logs = {}
#         self.current_ip = None
#         self.terminals = {}
#         self.sorting_order = {'Type': True, 'Address': True, 'Name': True}

#         # Main layout
#         self.main_frame = tk.Frame(self.master)
#         self.main_frame.pack(fill=tk.BOTH, expand=True)

#         # Top Section: IP Table
#         self.ip_table = ttk.Treeview(
#             self.main_frame, columns=("Index", "IP", "Port"), show="headings"
#         )

#         self.ip_table.heading("Index", text="Index")
#         self.ip_table.heading("IP", text="IP")
#         self.ip_table.heading("Port", text="Port")

#         self.ip_table.column("Index", width=100)
#         self.ip_table.column("IP", width=300)
#         self.ip_table.column("Port", width=300)
#         self.ip_table.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
#         self.ip_table.bind("<<TreeviewSelect>>", self.display_logs)

#         # Bottom Section: Log/Terminal Toggle
#         self.toggle_button_frame = tk.Frame(self.main_frame)
#         self.toggle_button_frame.pack()

#         self.log_button = ttk.Button(self.toggle_button_frame, text="Log", command=self.show_log_view)
#         self.log_button.grid(row=0, column=0, padx=5)

#         self.terminal_button = ttk.Button(self.toggle_button_frame, text="Terminal", command=self.show_terminal_view)
#         self.terminal_button.grid(row=0, column=1, padx=5)

#         # Log and Terminal Frames
#         self.log_frame = tk.Frame(self.main_frame)
#         self.terminal_frame = tk.Frame(self.main_frame)

#         # Log Viewer (Table)
#         self.log_table = ttk.Treeview(
#             self.log_frame,
#             columns=("Timestamp", "Message", "CPU %"),
#             show="headings",
#             height=10
#         )

#         self.log_table.heading("Timestamp", text="Timestamp", command=lambda: self.sort_column("Timestamp"))
#         self.log_table.heading("Message", text="Message")
#         self.log_table.heading("CPU %", text="CPU %", command=lambda: self.sort_column("CPU %"))
#         self.log_table.pack(fill=tk.BOTH, expand=True)

#         # Terminal Viewer
#         self.command_entry = tk.Entry(self.terminal_frame, font=("Courier", 12))
#         self.command_entry.pack(fill=tk.X, padx=10, pady=(10, 0))
#         self.command_entry.bind("<Return>", self.send_command)

#         self.terminal_text = tk.Text(self.terminal_frame, height=20, wrap=tk.WORD, state=tk.DISABLED, font=("Courier", 12))
#         self.terminal_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

#         # Start monitoring logs in a thread
#         threading.Thread(target=self.monitor_logs, daemon=True).start()
        
#         self.show_log_view()  # Default view

#     def monitor_logs(self):
#         """Monitor the log file and update logs in real-time."""
#         last_position = 0
#         while True:
#             if os.path.exists(LOG_FILE):
#                 with open(LOG_FILE, "r") as file:
#                     file.seek(last_position)
#                     new_lines = file.readlines()
#                     last_position = file.tell()

#                     for line in new_lines:
#                         if "Alert from" in line:
#                             timestamp = line.split(" - ")[0]
#                             message = line.split(": ", 1)[-1].strip()
#                             ip = line.split("from")[1].split(":")[0].strip(" ()'").split("'")[0]
#                             port = line.split("from")[1].split(":")[0].strip(" ()'").split(',')[1]
#                             cpu_match = re.search(r"CPU usage is (\d+\.\d+)%", message)
#                             cpu_percent = float(cpu_match.group(1)) if cpu_match else None
#                             self.add_log(ip, timestamp, message, cpu_percent , port )
                            
#             time.sleep(1)

#     def add_log(self, ip, timestamp, message, cpu_percent , port ):
#         """Add a log entry for the given IP."""
#         if ip not in self.logs:
#             self.logs[ip] = []
#             self.ip_table.insert("", tk.END, iid=ip, values=(len(self.ip_table.get_children()) + 1, ip, port))
#             self.terminals[ip] = ""

#         self.logs[ip].append((timestamp, message, cpu_percent))

#         if ip == self.current_ip:
#             self.update_log_display(ip)

#     def update_log_display(self, ip):
#         """Update the log table with logs for the selected IP."""
#         for row in self.log_table.get_children():
#             self.log_table.delete(row)

#         for timestamp, message, cpu_percent in self.logs[ip]:
#             self.log_table.insert("", tk.END, values=(timestamp, message, cpu_percent))

#     def display_logs(self, event):
#         """Display logs for the selected IP."""
#         selected_item = self.ip_table.selection()
#         if selected_item:
#             ip = selected_item[0]
#             self.current_ip = ip
#             self.update_log_display(ip)
#             self.show_log_view()

#     def show_log_view(self):
#         """Show the log view."""
#         self.terminal_frame.pack_forget()
#         self.log_frame.pack(fill=tk.BOTH, expand=True)

#     def show_terminal_view(self):
#         """Show the terminal view."""
#         self.log_frame.pack_forget()
#         self.terminal_frame.pack(fill=tk.BOTH, expand=True)

#     def send_command(self, event):
#         """Handle command submission."""
#         command = self.command_entry.get()
#         if command and self.current_ip:
#             self.terminals[self.current_ip] += f"> {command}\n"
#             self.terminals[self.current_ip] += f"Response from {self.current_ip}: Command executed.\n"
#             self.update_terminal_display()
#             self.command_entry.delete(0, tk.END)

#     def update_terminal_display(self):
#         """Update the terminal text area."""
#         self.terminal_text.config(state=tk.NORMAL)
#         self.terminal_text.delete(1.0, tk.END)
#         self.terminal_text.insert(tk.END, self.terminals[self.current_ip])
#         self.terminal_text.config(state=tk.DISABLED)

#     def sort_column(self, column):
#         """Sort the log table by the selected column."""
#         reverse = self.sorting_order.get(column, False)
#         self.sorting_order[column] = not reverse

#         # Sort the logs by the selected column
#         if column == "Timestamp":
#             index = 0
#         elif column == "CPU %":
#             index = 2  # CPU %

#         sorted_logs = sorted(self.logs[self.current_ip], key=lambda x: x[index], reverse=reverse)

#         # Update the log table with sorted logs
#         for row in self.log_table.get_children():
#             self.log_table.delete(row)

#         for timestamp, message, cpu_percent in sorted_logs:
#             self.log_table.insert("", tk.END, values=(timestamp, message, cpu_percent))



# if __name__ == "__main__":
#     root = tk.Tk()
#     app = LogMonitorApp(root)
#     root.mainloop()


import tkinter as tk
from tkinter import ttk
import threading
import os
import time
import re
from tkinter import Canvas

LOG_FILE = "udp_alerts.log"
CONNECTION_FILE = "connection_status.log"

class LogMonitorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Log Monitor")
        self.master.geometry("800x600")

        # Data storage
        self.logs = {}
        self.current_ip = None
        self.connection_status = {}

        # Main layout
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Top Section: IP Table
        self.ip_table = ttk.Treeview(
            self.main_frame, columns=("Index", "IP", "Port"), show="headings"
        )

        self.ip_table.heading("Index", text="Index")
        self.ip_table.heading("IP", text="IP")
        self.ip_table.heading("Port", text="Port")
        # self.ip_table.heading("Connection", text="Connection")

        self.ip_table.column("Index", width=100)
        self.ip_table.column("IP", width=100)
        self.ip_table.column("Port", width=100)
        # self.ip_table.column("Connection", width=200)
        self.ip_table.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.ip_table.bind("<<TreeviewSelect>>", self.display_logs)

        # Log Viewer (Table)
        self.log_table = ttk.Treeview(
            self.main_frame,
            columns=("Timestamp", "Message", "CPU %"),
            show="headings",
            height=10
        )

        self.log_table.heading("Timestamp", text="Timestamp", command=lambda: self.sort_logs("Timestamp"))
        self.log_table.heading("Message", text="Message")
        self.log_table.heading("CPU %", text="CPU %", command=lambda: self.sort_logs("CPU %"))

        self.log_table.column("Timestamp", width=100)
        self.log_table.column("Message", width=400)
        self.log_table.column("CPU %", width=100)

        self.log_table.pack(fill=tk.BOTH, expand=True)

        self.sorting_order = {"Timestamp": True, "CPU %": True}

        # Start monitoring logs in a thread
        threading.Thread(target=self.monitor_logs, daemon=True).start()
        # threading.Thread(target=self.update_connection_status, daemon=True).start()

    def monitor_logs(self):
        """Monitor the log file and update logs in real-time."""
        last_position = 0
        while True:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r") as file:
                    file.seek(last_position)
                    new_lines = file.readlines()
                    last_position = file.tell()

                    for line in new_lines:
                        if "Alert from" in line:
                            timestamp = line.split(" - ")[0]
                            message = line.split(": ", 1)[-1].strip()
                            ip = line.split("from")[1].split(":")[0].strip(" ()'").split("'")[0]
                            port = line.split("from")[1].split(":")[0].strip(" ()'").split(',')[1]
                            cpu_match = re.search(r"CPU usage is (\d+\.\d+)%", message)
                            cpu_percent = float(cpu_match.group(1)) if cpu_match else None
                            self.add_log(ip, timestamp, message, cpu_percent, port)
            time.sleep(1)

    def add_log(self, ip, timestamp, message, cpu_percent, port):
        """Add a log entry for the given IP."""
        if ip not in self.logs:
            self.logs[ip] = []
            # connection_state = self.connection_status.get(ip, "Unknown")
            tag = "even" if (len(self.ip_table.get_children()) + 1) % 2 == 0 else "odd"
            self.ip_table.insert("", tk.END, iid=ip, values=(len(self.ip_table.get_children()) + 1, ip, port), tags=(tag,))
            self.ip_table.tag_configure("even", background="white")
            self.ip_table.tag_configure("odd", background="#f0f0f0")
        self.logs[ip].append((timestamp, message, cpu_percent))

        # Sort logs by timestamp (newest first)
        self.logs[ip].sort(key=lambda x: x[0], reverse=True)

        # Keep only the 15 newest logs
        self.logs[ip] = self.logs[ip][:15]

        if ip == self.current_ip:
            self.update_log_display(ip)

    def update_log_display(self, ip):
        """Update the log table with logs for the selected IP."""
        for row in self.log_table.get_children():
            self.log_table.delete(row)

        for idx, (timestamp, message, cpu_percent) in enumerate(self.logs[ip]):
            tag = "even" if idx % 2 == 0 else "odd"
            self.log_table.insert("", tk.END, values=(timestamp, message, cpu_percent), tags=(tag,))

        self.log_table.tag_configure("even", background="white")
        self.log_table.tag_configure("odd", background="#f0f0f0")

        


    def display_logs(self, event):
        """Display logs for the selected IP."""
        selected_item = self.ip_table.selection()
        if selected_item:
            ip = selected_item[0]
            self.current_ip = ip
            self.update_log_display(ip)

    def sort_logs(self, column):
        """Sort the logs by the selected column."""
        reverse = self.sorting_order[column]
        self.sorting_order[column] = not reverse

        if column == "Timestamp":
            index = 0
        elif column == "CPU %":
            index = 2

        self.logs[self.current_ip].sort(key=lambda x: x[index], reverse=reverse)
        self.update_log_display(self.current_ip)

if __name__ == "__main__":
    root = tk.Tk()
    app = LogMonitorApp(root)
    root.mainloop()
