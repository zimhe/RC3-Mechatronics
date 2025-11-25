# RC3-Mechatronics

A comprehensive Python-based control system for Dynamixel AX-12A servo motors with motion learning, OSC communication, and Arduino integration capabilities.

## 🎯 Overview

This project provides a complete toolkit for controlling and programming Dynamixel AX-12A servo motors. It includes motion learning capabilities with GUI monitoring, OSC (Open Sound Control) communication for remote control, and Arduino integration for expanded functionality.

## 📋 Features

- **Dynamixel AX-12A Control**: Complete servo motor control with position, speed, and torque management
- **Motion Learning & Playback**: Record and replay complex motor movements with real-time GUI monitoring
- **OSC Communication**: Remote control via Open Sound Control protocol
- **Arduino Integration**: Extend capabilities with Arduino-based control systems
- **Interactive GUI**: Real-time position monitoring during motion learning
- **Jupyter Notebook Tutorials**: Step-by-step learning materials

## 🏗️ Project Structure

```
RC3-Mechatronics/
├── 00_install_and_environment_config.ipynb    # Setup and installation guide
├── 01_simple_control.ipynb                    # Basic motor control tutorial
├── 02_motion_learning.ipynb                   # Motion recording tutorial
├── 03_run_server.ipynb                        # OSC server setup
├── requirements.txt                           # Python dependencies
├── motion_datas/                              # Saved motion files
│   └── motions-01.json
├── part_1/                                    # Core Dynamixel control
│   ├── ax12a_control_table.py                 # AX-12A register definitions
│   ├── dxl_ax12a.py                          # Main AX-12A control class
│   ├── dxl_a12_usb_control.py                # USB communication handler
│   ├── motionLearning.py                     # Motion learning with GUI
│   └── tutorial.py                           # Basic tutorials
├── part_2/                                    # OSC communication
│   ├── dxl_control_osc.py                    # OSC-enabled motor control
│   ├── dxl_osc_main.py                       # Main OSC application
│   ├── my_osc_client.py                      # OSC client implementation
│   ├── my_osc_server.py                      # OSC server implementation
│   └── osc_commond_patterns.py               # OSC command definitions
└── arduino/                                   # Arduino integration
    ├── arduino_control.py                    # Arduino communication
    └── arduino_test.py                       # Arduino testing utilities
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Dynamixel AX-12A servo motors
- USB2AX or similar USB-to-Dynamixel adapter
- Arduino (optional, for extended functionality)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/zimhe/RC3-Mechatronics.git
   cd RC3-Mechatronics
   ```

2. **Create and activate virtual environment:**

   **On Windows:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   venv\Scripts\activate
   ```

   **On Mac/Linux:**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Hardware Setup:**
   - Connect your Dynamixel servos to the USB2AX adapter
   - Connect the adapter to your computer
   - Find the COM port using the methods below:

   **Finding COM Port on Windows:**
   
   **Method 1: Device Manager (Most Reliable)**
   ```
   1. Press Win + X, select "Device Manager"
   2. Expand "Ports (COM & LPT)" section
   3. Look for entries like:
      - "USB Serial Port (COM3)"
      - "USB-SERIAL CH340 (COM4)"
      - "Arduino Uno (COM5)"
   4. Note the COM number in parentheses
   ```
   
   **Method 2: Using Python (Recommended for programmers)**
   ```python
   import serial.tools.list_ports
   
   # List all available ports
   ports = serial.tools.list_ports.comports()
   for port in ports:
       print(f"Port: {port.device}, Description: {port.description}")
   ```
   
   **Method 3: Using PowerShell (Alternative)**
   ```powershell
   # For newer Windows versions (Windows 10/11)
   Get-PnpDevice -Class Ports | Where-Object {$_.Status -eq "OK"}
   
   # Alternative command
   [System.IO.Ports.SerialPort]::getportnames()
   ```
   
   **Method 4: Command Prompt (Legacy)**
   ```cmd
   # Simple port listing
   mode
   
   # More detailed (may not work on all systems)
   wmic path win32_serialport get deviceid,name,description
   ```

   **Finding COM Port on Mac:**
   ```bash
   # List all serial devices
   ls /dev/tty.*
   
   # Look for devices like /dev/tty.usbserial-* or /dev/tty.usbmodem-*
   # Common patterns:
   # - /dev/tty.usbserial-XXXXXXXX
   # - /dev/tty.usbmodem-XXXXXXXX
   
   # Get detailed information
   system_profiler SPUSBDataType
   ```

   **Finding COM Port on Linux:**
   ```bash
   # List all serial devices
   ls /dev/tty*
   
   # Look for USB devices (common patterns):
   ls /dev/ttyUSB* /dev/ttyACM*
   
   # Get detailed device information
   dmesg | grep tty
   
   # Show USB devices
   lsusb
   
   # Get more details about serial ports
   setserial -g /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
   ```

   **Note:** Typical port names:
   - **Windows**: COM3, COM4, COM5, etc.
   - **Mac**: /dev/tty.usbserial-XXXXXXXX, /dev/tty.usbmodem-XXXXXXXX
   - **Linux**: /dev/ttyUSB0, /dev/ttyUSB1, /dev/ttyACM0, etc.

   **Auto-Detection (Recommended):**
   ```python
   # If you don't know the port name, use auto-detection
   from part_1.dxl_ax12a import auto_connect_dynamixel, find_dynamixel_port, scan_available_ports
   
   # Method 1: Full auto-connection (easiest)
   controller, port, motors = auto_connect_dynamixel()
   if controller:
       print(f"Connected to {port} with motors: {motors}")
   
   # Method 2: Just find the port and motor IDs
   port, motors = find_dynamixel_port()
   if port:
       print(f"Found motors {motors} on port {port}")
       controller = AX12a(port)
   
   # Method 3: Just list available ports
   available_ports = scan_available_ports()
   ```

5. **Configure and test:**
   - Open `00_install_and_environment_config.ipynb` in Jupyter
   - Follow the setup instructions
   - Test your hardware configuration

### Basic Usage



#### 1. Simple Motor Control

```python
from part_1.dxl_ax12a import AX12a

# Method 1: Manual port specification
motor_controller = AX12a('COM3')  # Replace with your COM port

# Method 2: Auto-detection (recommended)
from part_1.dxl_ax12a import auto_connect_dynamixel
controller, port, motors = auto_connect_dynamixel()

if controller:
    print(f"Auto-connected to {port} with motors: {motors}")
    # Control a motor (use first detected motor ID)
    motor_id = motors[0] if motors else 1
    controller.set_position_ID(512, motor_id)  # Move to center position
    position = controller.get_position_ID(motor_id)  # Read current position
else:
    print("No Dynamixel motors detected. Check connections.")
```

#### 2. Motion Learning with GUI

```bash
python part_1/motionLearning.py --devicename COM3 --connected_motors 0 1 2
```

Features:
- Real-time GUI monitoring of motor positions
- Record complex movements by manually positioning motors
- Save and load motion sequences
- Configurable learning parameters

#### 3. OSC Remote Control

```python
# Start OSC server
python part_2/dxl_osc_main.py

# Send commands from OSC client
python part_2/my_osc_client.py
```

## 📖 Tutorials

The project includes comprehensive Jupyter notebook tutorials:

1. **`00_install_and_environment_config.ipynb`**: Environment setup and dependency installation
2. **`01_simple_control.ipynb`**: Basic motor control operations
3. **`02_motion_learning.ipynb`**: Recording and playing back motions
4. **`03_run_server.ipynb`**: Setting up OSC communication

## 🎮 Motion Learning GUI

The motion learning system features a real-time GUI that displays:

- **Motor Positions**: Live position values for each connected motor
- **Progress Tracking**: Step counter and progress bar
- **Interactive Controls**: Start, stop, and save functionality
- **Real-time Updates**: Smooth position monitoring during recording

To use the GUI:
1. Run the motion learning script
2. Choose "Yes" when prompted for GUI monitoring
3. Manually position the motors while the system records
4. Save your motion sequence for later playback

## 🔧 Configuration Options

### Command Line Arguments for Motion Learning

```bash
python motionLearning.py [options]

Options:
  --devicename COM3              # COM port for motor controller
  --connected_motors 0 1 2       # List of motor IDs to use
  --moving_speed 100            # Default movement speed
  --max_learning_steps 300      # Maximum recording steps
```

### Motor Configuration

- **Position Range**: 0-1023 (150° total range)
- **Speed Range**: 0-1023 (variable RPM)
- **Default Baudrate**: 1,000,000 bps
- **Protocol**: Dynamixel Protocol 1.0

## 🌐 OSC Communication

The OSC system enables remote control via network:

- **Default Port**: 8000
- **Supported Commands**: Position control, speed adjustment, torque enable/disable
- **Client-Server Architecture**: Flexible communication setup

## 🔌 Arduino Integration

Extend functionality with Arduino:

- **Serial Communication**: Bi-directional data exchange
- **Sensor Integration**: Add external sensors
- **Custom Control Logic**: Implement specialized behaviors

## 🛠️ Dependencies

- **dynamixel-sdk**: Official Dynamixel communication library
- **pyserial**: Serial communication
- **python-osc**: OSC protocol implementation
- **pyFirmata**: Arduino communication
- **easygui**: Simple GUI dialogs
- **tkinter**: GUI framework (included with Python)

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 🐛 Troubleshooting

### Common Issues

1. **COM Port Not Found**
   - Check device manager for correct COM port
   - Ensure drivers are installed for your USB adapter

2. **Motor Not Responding**
   - Verify motor ID configuration
   - Check power supply and connections
   - Ensure baudrate matches motor settings

3. **GUI Not Displaying**
   - Check tkinter installation
   - Verify Python GUI libraries are available

### Getting Help

- Check the Jupyter tutorials for step-by-step guidance
- Review the example code in each module
- Ensure all hardware connections are secure

## 📄 License

This project is part of the RC3 educational framework for mechatronics learning and research.

## 🤝 Acknowledgments

- Robotis for the Dynamixel SDK
- The Python community for excellent libraries
- RC3 team for educational framework development

---

**Note**: Make sure to configure your motor IDs and COM ports according to your specific hardware setup before running the examples.
