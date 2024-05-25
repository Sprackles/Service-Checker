import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import socket
import time
import threading


class ServiceCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Service Checker")
        self.root.configure(bg='#2e2e2e')

        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#2e2e2e', foreground='white')
        style.configure('TEntry', fieldbackground='#3e3e3e', foreground='white')
        style.configure('TButton', background='#4e4e4e', foreground='white')
        style.configure('TCheckbutton', background='#2e2e2e', foreground='white')

        # Variables
        self.hostname_var = tk.StringVar()
        self.interval_var = tk.StringVar(value='5')
        self.custom_port_var = tk.StringVar()

        self.services = {
            "VNC": 5900,
            "HTTP": 80,
            "HTTPS": 443,
            "FTP": 21,
            "SSH": 22
        }

        self.service_vars = {service: tk.BooleanVar(value=True) for service in self.services}
        self.custom_ports = []
        self.status_labels = {}
        self.success_vars = {}
        self.fail_vars = {}

        # Layout
        ttk.Label(root, text="Hostname or IP:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.hostname_entry = ttk.Entry(root, textvariable=self.hostname_var, width=30)
        self.hostname_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(root, text="Check Interval (s):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.interval_entry = ttk.Entry(root, textvariable=self.interval_var, width=30)
        self.interval_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(root, text="Services to Check:").grid(row=2, column=0, columnspan=2, pady=5)

        row = 3
        for service, port in self.services.items():
            checkbutton = ttk.Checkbutton(root, text=f"{service} (Port {port})", variable=self.service_vars[service])
            checkbutton.grid(row=row, column=0, padx=5, pady=2, sticky='w')

            self.status_labels[service] = tk.Label(root, bg='red', width=2)
            self.status_labels[service].grid(row=row, column=1, padx=5, pady=2, sticky='w')

            self.success_vars[service] = tk.IntVar(value=0)
            self.fail_vars[service] = tk.IntVar(value=0)

            ttk.Label(root, text="Success:").grid(row=row, column=2, padx=5, pady=2, sticky='e')
            ttk.Label(root, textvariable=self.success_vars[service]).grid(row=row, column=3, padx=5, pady=2, sticky='w')

            ttk.Label(root, text="Fail:").grid(row=row, column=4, padx=5, pady=2, sticky='e')
            ttk.Label(root, textvariable=self.fail_vars[service]).grid(row=row, column=5, padx=5, pady=2, sticky='w')

            row += 1

        ttk.Label(root, text="Custom Port:").grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.custom_port_entry = ttk.Entry(root, textvariable=self.custom_port_var, width=30)
        self.custom_port_entry.grid(row=row, column=1, padx=5, pady=5)

        ttk.Button(root, text="Add Custom Port", command=self.add_custom_port).grid(row=row + 1, column=0, columnspan=2,
                                                                                    pady=5)

        ttk.Button(root, text="Start Checking", command=self.start_checking).grid(row=row + 2, column=0, columnspan=6,
                                                                                  pady=10)

        self.running = False

    def add_custom_port(self):
        try:
            custom_port = int(self.custom_port_var.get())
            if custom_port > 0 and custom_port <= 65535:
                self.custom_ports.append(custom_port)
                self.custom_port_var.set("")
                messagebox.showinfo("Success", f"Custom port {custom_port} added successfully")
            else:
                messagebox.showerror("Error", "Port must be between 1 and 65535")
        except ValueError:
            messagebox.showerror("Error", "Port must be a number")

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

        selected_services = {service: port for service, port in self.services.items() if
                             self.service_vars[service].get()}
        self.running = True
        self.thread = threading.Thread(target=self.check_servers,
                                       args=(hostname, selected_services, self.custom_ports, interval))
        self.thread.start()

    def check_servers(self, hostname, selected_services, custom_ports, interval):
        while self.running:
            all_services = {**selected_services, **{f"Custom Port {port}": port for port in custom_ports}}
            for service, port in all_services.items():
                try:
                    ip_address = socket.gethostbyname(hostname)
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2)
                    result = s.connect_ex((ip_address, port))
                    s.close()
                    if result == 0:
                        self.status_labels[service].configure(bg='green')
                        self.success_vars[service].set(self.success_vars[service].get() + 1)
                    else:
                        self.status_labels[service].configure(bg='red')
                        self.fail_vars[service].set(self.fail_vars[service].get() + 1)
                except socket.gaierror:
                    self.status_labels[service].configure(bg='red')
                    self.fail_vars[service].set(self.fail_vars[service].get() + 1)
                except Exception as e:
                    self.status_labels[service].configure(bg='red')
                    self.fail_vars[service].set(self.fail_vars[service].get() + 1)

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
    app = ServiceCheckerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()