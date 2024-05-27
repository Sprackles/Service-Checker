# Service Checker

## Overview
The Service Checker is a tool designed to help you monitor various types of servers on a remote machine. It allows you to check the status of predefined services like VNC, HTTP, HTTPS, FTP, and SSH, as well as custom ports you can add. The application provides real-time status updates with visual indicators and keeps track of successful and unsuccessful attempts.

## Features
- **Service Monitoring**: Check the status of predefined services and custom ports.
- **Visual Indicators**: Green indicator for active services and red indicator for inactive services.
- **Customizable Check Interval**: Set the frequency of checks in seconds.
- **Hostname and IP Display**: Shows both hostname and IP address of the remote machine.
- **Real-Time Status**: Provides real-time updates with counts of successful and unsuccessful checks.
- **User-Friendly Interface**: Dark mode interface for ease of use.

## How to Use

### 1. Configure the Application:
   - Open the application.
   - Enter the hostname or IP address of the remote machine.
   - The hostname and IP address will be displayed after entering a hostname.
   - Enter the check interval in seconds (e.g., 5 for 5 seconds).

### 2. Add Custom Ports:
   - Enter a custom port number in the "Custom Port" field.
   - Click "Add Custom Port" to add the port to the list of services to be checked.
   - The custom port will be added to the list with its own visual indicator and success/fail counters.

### 3. Select Services to Check:
   - Use the checkboxes to select which predefined services and custom ports to monitor. All predefined services are selected by default.

### 4. Start Checking:
   - Click the "Start Checking" button to begin monitoring the selected services.
   - The button will toggle to "Stop Checking" to allow you to stop the monitoring process.

### 5. Monitor Status:
   - The application will display real-time status updates with visual indicators (green for active, red for inactive) and counts of successful and unsuccessful attempts.

## Future Improvements
I'm planning to make improvements and add more features.

## Installation

### Prerequisites
- Python 3.x
- Tkinter

### Running the Tool
1. **Clone the repository**:
   ```sh
   git clone https://github.com/Sprackles/Service-Checker.git
2. **Navigate to the project directory**:
   ```sh
   cd service-checker
3. **Run the script**:
   ```sh
   python service_checker.py

### Compiling to an Executable
   To compile the script into a single executable file using Pyinstaller:
1. **Install pyinstaller**:
   ```sh
   pip install pyinstaller
2. **Compile the script**:
   ```sh
   pyinstaller --onefile --windowed service_checker.py
