#!/usr/bin/env python3
"""
Port Management Utility for OSC Server
Helps find and manage ports for the OSC server
"""

import socket
import subprocess
import sys
import os

def check_port(host, port):
    """Check if a port is available"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result != 0  # True if port is available
    except:
        return False

def find_available_ports(start_port=8080, count=10):
    """Find available ports starting from start_port"""
    available_ports = []
    for port in range(start_port, start_port + 100):
        if check_port("127.0.0.1", port):
            available_ports.append(port)
            if len(available_ports) >= count:
                break
    return available_ports

def find_process_using_port(port):
    """Find which process is using a specific port (Windows)"""
    try:
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            processes = []
            for line in lines:
                if f':{port}' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        try:
                            # Get process name
                            proc_result = subprocess.run(
                                f'tasklist /FI "PID eq {pid}" /FO CSV',
                                shell=True,
                                capture_output=True,
                                text=True
                            )
                            if proc_result.stdout:
                                proc_lines = proc_result.stdout.strip().split('\n')
                                if len(proc_lines) > 1:
                                    proc_name = proc_lines[1].split(',')[0].strip('"')
                                    processes.append(f"PID: {pid}, Process: {proc_name}")
                        except:
                            processes.append(f"PID: {pid}")
            return processes
        return []
    except:
        return []

def kill_process_on_port(port):
    """Kill process using specified port"""
    processes = find_process_using_port(port)
    if not processes:
        print(f"No processes found using port {port}")
        return False
    
    print(f"Processes using port {port}:")
    for proc in processes:
        print(f"  {proc}")
    
    confirm = input(f"Do you want to kill these processes? (y/N): ")
    if confirm.lower() == 'y':
        try:
            # Extract PIDs and kill them
            for proc in processes:
                if "PID:" in proc:
                    pid = proc.split("PID:")[1].split(",")[0].strip()
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True)
                    print(f"Killed process {pid}")
            return True
        except Exception as e:
            print(f"Error killing processes: {e}")
            return False
    return False

def main():
    print("=== OSC Server Port Manager ===\n")
    
    # Check default port
    default_port = 8080
    print(f"Checking default port {default_port}...")
    
    if check_port("127.0.0.1", default_port):
        print(f"✓ Port {default_port} is available")
    else:
        print(f"✗ Port {default_port} is in use")
        processes = find_process_using_port(default_port)
        if processes:
            print("Processes using this port:")
            for proc in processes:
                print(f"  {proc}")
            
            print("\nOptions:")
            print("1. Kill the process(es)")
            print("2. Use a different port")
            print("3. Exit")
            
            choice = input("Enter your choice (1-3): ")
            
            if choice == "1":
                if kill_process_on_port(default_port):
                    print(f"Port {default_port} should now be available")
                else:
                    print("Failed to kill processes")
            elif choice == "2":
                print("\nFinding alternative ports...")
            else:
                sys.exit(0)
    
    # Show available ports
    print(f"\nAvailable ports near {default_port}:")
    available = find_available_ports(default_port, 10)
    for i, port in enumerate(available[:5], 1):
        print(f"  {i}. {port}")
    
    if available:
        print(f"\nRecommended port: {available[0]}")
        
        # Offer to update the server configuration
        update = input("Update server configuration to use recommended port? (y/N): ")
        if update.lower() == 'y':
            try:
                # Update my_osc_server.py
                server_file = "my_osc_server.py"
                if os.path.exists(server_file):
                    with open(server_file, 'r') as f:
                        content = f.read()
                    
                    # Replace the address line
                    new_content = content.replace(
                        f'address=("0.0.0.0",{default_port})',
                        f'address=("0.0.0.0",{available[0]})'
                    )
                    
                    with open(server_file, 'w') as f:
                        f.write(new_content)
                    
                    print(f"Updated {server_file} to use port {available[0]}")
                else:
                    print(f"Could not find {server_file}")
                    
            except Exception as e:
                print(f"Error updating configuration: {e}")
    else:
        print("No available ports found!")

if __name__ == "__main__":
    main()