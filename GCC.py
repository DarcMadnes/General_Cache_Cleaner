import subprocess
import os
import psutil
import shutil
import time
from datetime import datetime

def run_cmd_with_admin(cmd, close_after=True):
    delay = 5 if 'ipconfig /release' in cmd else 2  
    # Set delay to 5 seconds for ipconfig /release, 2 seconds for others
    try:
        user = os.getlogin()  # Get currently logged-in user
        subprocess.run(['runas', f'/user:{user}', '/savecred', cmd], check=True)
        print(f"Command '{cmd}' has been successfully executed!")

        time.sleep(delay)  # Delay before closing the Command Prompt window

        if close_after:
            os.system('exit')  # Close the Command Prompt window
    except subprocess.CalledProcessError as e:
        print(f"Error: Command '{cmd}' failed to execute.")
        print(f"Reason: {e}")
        # You can add further error handling here if needed
            
def change_console_color(color_code):
    subprocess.run(['cmd', '/c', f'color {color_code}'], shell=True)

# Change console color to gray background with green text (8A)
change_console_color('8A')            

def initiate_disk_cleanup(drive):
    # Command to initiate disk cleanup with administrator privileges
    disk_cleanup_cmd = f'cleanmgr /sagerun:{drive}'

    run_cmd_with_admin(disk_cleanup_cmd)

def delete_temp_files():
    try:
        temp_folder = os.environ['TEMP']
        shutil.rmtree(temp_folder, ignore_errors=True)
        print("All files from the TEMP folder have been successfully deleted!")
    except Exception as e:
        print("Error: Failed to delete files from the TEMP folder.")
        print(f"Reason: {e}")
        # You can add further error handling here if needed

def delete_temp_files_local():
    try:
        temp_folder = os.path.join(os.environ['LOCALAPPDATA'], 'Temp')
        shutil.rmtree(temp_folder, ignore_errors=True)
        print("All files from the TEMP folder have been successfully deleted!")
    except Exception as e:
        print("Error: Failed to delete files from the TEMP folder.")
        print(f"Reason: {e}")
        # You can add further error handling here if needed        

def run_powershell_command(command):
    try:
        subprocess.run(['powershell', '-Command', command], check=True, input=b'Y\n')  # Automatically answer Yes
        print(f"Command '{command}' has been successfully executed!")
    except subprocess.CalledProcessError as e:
        print(f"Error: Command '{command}' failed to execute.")
        print(f"Reason: {e}")
        # You can add further error handling here if needed

def reset_microsoft_store():
    reset_command = "Start-Process -FilePath 'wsreset.exe' -Verb RunAs"
    run_powershell_command(reset_command)

    # Wait for 5 seconds after the cleanmgr command finishes
    time.sleep(5)

    # Terminate the WinStore.App.exe process
    try:
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name'] == 'WinStore.App.exe':
                print("Terminating WinStore.App.exe process...")
                psutil.Process(process.info['pid']).terminate()
                print("WinStore.App.exe process terminated.")
                break
    except Exception as e:
        print("Error: Failed to terminate WinStore.App.exe process.")
        print(f"Reason: {e}")

def create_restore_point():
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    description = current_datetime.replace(" ", "_").replace(":", "-")
    restore_command = f'Checkpoint-Computer -Description "{description}" -RestorePointType "MODIFY_SETTINGS"'
    run_powershell_command(restore_command)

def main():
    # Run PowerShell command to delete shadow copies
    delete_shadow_copies_cmd = 'vssadmin delete shadows /all /quiet'
    run_powershell_command(delete_shadow_copies_cmd)

    # Run the command to modify System RestorePointCreationFrequency
    system_restore_command = 'REG ADD "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore" /V "SystemRestorePointCreationFrequency" /T REG_DWORD /D 0 /F'
    run_cmd_with_admin(system_restore_command)

    # Reset Microsoft Store
    reset_microsoft_store()

    # Create a restore point
    create_restore_point()

    # Commands to be executed with administrator privileges
    commands = [
        ('ipconfig /release', False),  # Do not close Command Prompt window
        'ipconfig /flushdns',
        'ipconfig /registerdns',
        'ipconfig /renew',
        'netsh winsock reset'
    ]
    
    for cmd in commands:
        if isinstance(cmd, tuple):
            run_cmd_with_admin(cmd[0], close_after=cmd[1])
        else:
            run_cmd_with_admin(cmd)

    print("All commands have been successfully executed!")

    # Get a list of all disk partitions
    partitions = psutil.disk_partitions(all=True)

    # Initiate disk cleanup on each drive
    for partition in partitions:
        drive_letter = partition.device[:2]  # Extract the drive letter (e.g., 'C:')
        print(f"Initiating disk cleanup on drive {drive_letter}")
        initiate_disk_cleanup(drive_letter)

    # Delete all files from the Win TEMP folder
    delete_temp_files()

    # Delete all files from the Local TEMP folder
    delete_temp_files_local()

    # Close the Command Prompt window
    os.system('exit')

if __name__ == "__main__":
    main()
 