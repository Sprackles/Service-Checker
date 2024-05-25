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
        self.ip_hostname_var = tk.StringVar(value='')

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

        self.ip_hostname_label = ttk.Label(root, textvariable=self.ip_hostname_var)
        self.ip_hostname_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='w')

        ttk.Label(root, text="Check Interval (s):").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.interval_entry = ttk.Entry(root, textvariable=self.interval_var, width=30)
        self.interval_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(root, text="Services to Check:").grid(row=3, column=0, columnspan=2, pady=5)

        self.service_row_start = 4
        self.display_services()

        ttk.Label(root, text="Custom Port:").grid(row=self.service_row_start + len(self.services), column=0, padx=5,
                                                  pady=5, sticky='w')
        self.custom_port_entry = ttk.Entry(root, textvariable=self.custom_port_var, width=30)
        self.custom_port_entry.grid(row=self.service_row_start + len(self.services), column=1, padx=5, pady=5)

        ttk.Button(root, text="Add Custom Port", command=self.add_custom_port).grid(
            row=self.service_row_start + len(self.services) + 1, column=0, columnspan=2, pady=5)

        self.start_button = ttk.Button(root, text="Start Checking", command=self.toggle_checking)
        self.start_button.grid(row=self.service_row_start + len(self.services) + 2, column=0, columnspan=6, pady=10)

        self.running = False

    def display_services(self):
        row = self.service_row_start
        for service, port in self.services.items():
            checkbutton = ttk.Checkbutton(self.root, text=f"{service} (Port {port})",
                                          variable=self.service_vars[service])
            checkbutton.grid(row=row, column=0, padx=5, pady=2, sticky='w')

            self.status_labels[service] = tk.Label(self.root, bg='red', width=2)
            self.status_labels[service].grid(row=row, column=1, padx=5, pady=2, sticky='w')

            self.success_vars[service] = tk.IntVar(value=0)
            self.fail_vars[service] = tk.IntVar(value=0)

            ttk.Label(self.root, text="Success:").grid(row=row, column=2, padx=5, pady=2, sticky='e')
            ttk.Label(self.root, textvariable=self.success_vars[service]).grid(row=row, column=3, padx=5, pady=2,
                                                                               sticky='w')

            ttk.Label(self.root, text="Fail:").grid(row=row, column=4, padx=5, pady=2, sticky='e')
            ttk.Label(self.root, textvariable=self.fail_vars[service]).grid(row=row, column=5, padx=5, pady=2,
                                                                            sticky='w')

            row += 1

    def add_custom_port(self):
        try:
            custom_port = int(self.custom_port_var.get())
            if custom_port > 0 and custom_port <= 65535:
                port_label = f"Custom Port {custom_port}"
                self.services[port_label] = custom_port
                self.service_vars[port_label] = tk.BooleanVar(value=True)

                row = self.service_row_start + len(self.services) - 1

                checkbutton = ttk.Checkbutton(self.root, text=port_label, variable=self.service_vars[port_label])
                checkbutton.grid(row=row, column=0, padx=5, pady=2, sticky='w')

                self.status_labels[port_label] = tk.Label(self.root, bg='red', width=2)
                self.status_labels[port_label].grid(row=row, column=1, padx=5, pady=2, sticky='w')

                self.success_vars[port_label] = tk.IntVar(value=0)
                self.fail_vars[port_label] = tk.IntVar(value=0)

                ttk.Label(self.root, text="Success:").grid(row=row, column=2, padx=5, pady=2, sticky='e')
                ttk.Label(self.root, textvariable=self.success_vars[port_label]).grid(row=row, column=3, padx=5, pady=2,
                                                                                      sticky='w')

                ttk.Label(self.root, text="Fail:").grid(row=row, column=4, padx=5, pady=2, sticky='e')
                ttk.Label(self.root, textvariable=self.fail_vars[port_label]).grid(row=row, column=5, padx=5, pady=2,
                                                                                   sticky='w')

                self.custom_port_var.set("")
                messagebox.showinfo("Success", f"Custom port {custom_port} added successfully")
            else:
                messagebox.showerror("Error", "Port must be between 1 and 65535")
        except ValueError:
            messagebox.showerror("Error", "Port must be a number")

    def toggle_checking(self):
        if self.running:
            self.stop_checking()
            self.start_button.configure(text="Start Checking")
        else:
            self.start_checking()
            self.start_button.configure(text="Stop Checking")

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

        try:
            ip_address = socket.gethostbyname(hostname)
            self.ip_hostname_var.set(f"Hostname: {hostname}, IP: {ip_address}")
        except socket.gaierror:
            messagebox.showerror("Error", "Invalid hostname or IP address")
            return

        selected_services = {service: port for service, port in self.services.items() if
                             self.service_vars[service].get()}
        self.running = True
        self.thread = threading.Thread(target=self.check_servers,
                                       args=(hostname, ip_address, selected_services, interval))
        self.thread.start()

    def check_servers(self, hostname, ip_address, selected_services, interval):
        while self.running:
            for service, port in selected_services.items():
                try:
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