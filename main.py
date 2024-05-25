import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import socket
import time
import threading

class ServerCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Server Checker")
        self.root.configure(bg='#2e2e2e')

        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#2e2e2e', foreground='white')
        style.configure('TEntry', fieldbackground='#3e3e3e', foreground='white')
        style.configure('TButton', background='#4e4e4e', foreground='white')
        style.configure('TCombobox', fieldbackground='#3e3e3e', foreground='white')

        # Variables
        self.hostname_var = tk.StringVar()
        self.interval_var = tk.StringVar(value='5')
        self.status_var = tk.StringVar(value='Unknown')
        self.success_var = tk.IntVar(value=0)
        self.fail_var = tk.IntVar(value=0)
        self.service_var = tk.StringVar()

        self.services = {
            "VNC": 5900,
            "HTTP": 80,
            "HTTPS": 443,
            "FTP": 21,
            "SSH": 22
        }

        # Layout
        ttk.Label(root, text="Hostname or IP:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.hostname_entry = ttk.Entry(root, textvariable=self.hostname_var, width=30)
        self.hostname_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(root, text="Service:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.service_combobox = ttk.Combobox(root, textvariable=self.service_var, values=list(self.services.keys()), state='readonly')
        self.service_combobox.grid(row=1, column=1, padx=5, pady=5)
        self.service_combobox.set("VNC")

        ttk.Label(root, text="Check Interval (s):").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.interval_entry = ttk.Entry(root, textvariable=self.interval_var, width=30)
        self.interval_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(root, text="Start Checking", command=self.start_checking).grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Label(root, text="Current Status:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(root, textvariable=self.status_var).grid(row=4, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(root, text="Successful Attempts:").grid(row=5, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(root, textvariable=self.success_var).grid(row=5, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(root, text="Unsuccessful Attempts:").grid(row=6, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(root, textvariable=self.fail_var).grid(row=6, column=1, padx=5, pady=5, sticky='w')

        self.running = False

    def start_checking(self):
        hostname = self.hostname_var.get()
        if not hostname:
            messagebox.showerror("Error", "Hostname or IP address is required")
            return
        try:
            interval = float(self.interval_var.get())
        except ValueError:
            messagebox.showerror("Error", "Interval must be a number")
            return

        service = self.service_var.get()
        if service not in self.services:
            messagebox.showerror("Error", "Please select a valid service")
            return

        self.running = True
        self.thread = threading.Thread(target=self.check_server, args=(hostname, self.services[service], interval))
        self.thread.start()

    def check_server(self, hostname, port, interval):
        while self.running:
            try:
                ip_address = socket.gethostbyname(hostname)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                result = s.connect_ex((ip_address, port))
                s.close()
                if result == 0:
                    self.status_var.set(f"Running (Host: {hostname}, IP: {ip_address}, Port: {port})")
                    self.success_var.set(self.success_var.get() + 1)
                else:
                    self.status_var.set(f"Not Running (Host: {hostname}, IP: {ip_address}, Port: {port})")
                    self.fail_var.set(self.fail_var.get() + 1)
            except socket.gaierror:
                self.status_var.set(f"Hostname resolution failed")
                self.fail_var.set(self.fail_var.get() + 1)
            except Exception as e:
                self.status_var.set(f"Error: {str(e)}")
                self.fail_var.set(self.fail_var.get() + 1)

            time.sleep(interval)

    def stop_checking(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()

    def on_closing(self):
        self.stop_checking()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerCheckerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()