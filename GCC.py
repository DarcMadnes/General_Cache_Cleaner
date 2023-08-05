import subprocess
import os
import time
from datetime import datetime
import psutil
import shutil

def run_cmd_with_admin(cmd, close_after=True):
    delay = 5 if 'ipconfig /release' in cmd else 1
    user = os.getlogin()  # Get currently logged-in user
    subprocess.run(['runas', f'/user:{user}', '/savecred', cmd], check=True)
    print(f"Command '{cmd}' has been successfully executed!")
    
    if close_after:
        time.sleep(delay)
        os.system('exit')

def run_powershell_command(command):
    try:
        subprocess.run(['powershell', '-Command', command], check=True, input=b'Y\n')
        print(f"Command '{command}' has been successfully executed!")
    except subprocess.CalledProcessError as e:
        print(f"Error: Command '{command}' failed to execute.")
        print(f"Reason: {e}")

def create_restore_point():
    current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    description = current_datetime.replace(":", "-")
    restore_command = f'Checkpoint-Computer -Description "{description}" -RestorePointType "MODIFY_SETTINGS"'
    run_powershell_command(restore_command)

def initiate_disk_cleanup(drive):
    disk_cleanup_cmd = f'cleanmgr /sagerun:{drive}'
    run_cmd_with_admin(disk_cleanup_cmd)

def delete_temp_files(temp_folder):
    try:
        shutil.rmtree(temp_folder, ignore_errors=True)
        print(f"All files from the {temp_folder} folder have been successfully deleted!")
    except Exception as e:
        print(f"Error: Failed to delete files from the {temp_folder} folder.")
        print(f"Reason: {e}")
        
def delete_temp_files(temp_folder):
    try:
        os.chdir(temp_folder)  # Change working directory to temp folder
        for root, dirs, files in os.walk(temp_folder):
            for file in files:
                os.remove(os.path.join(root, file))
        print(f"All files from {temp_folder} have been successfully deleted!")
    except Exception as e:
        print(f"Error: Failed to delete files from {temp_folder}.")
        print(f"Reason: {e}")
        # Further error handling here if needed        
        
def change_console_color(color_code):
    subprocess.run(['cmd', '/c', f'color {color_code}'], shell=True)   
         

def main():
    
    start_time = time.time()
    change_console_color('2')
    create_restore_point()
    delete_temp_files('C:\Windows\Temp') # Delete files from the TEMP folder
    delete_temp_files(os.path.join(os.environ['LOCALAPPDATA'], 'Temp'))  # Delete files from the Local TEMP folder

    run_powershell_command('vssadmin delete shadows /all /quiet')  # Delete shadow copies

    run_cmd_with_admin('REG ADD "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\SystemRestore" /V "SystemRestorePointCreationFrequency" /T REG_DWORD /D 0 /F')
    
    run_powershell_command("Start-Process -FilePath 'wsreset.exe' -Verb RunAs")
    time.sleep(5)
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == 'WinStore.App.exe':
            print("Terminating WinStore.App.exe process...")
            psutil.Process(process.info['pid']).terminate()
            print("WinStore.App.exe process terminated.")
            break
    
    commands = [
        ('ipconfig /release', False),
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

    partitions = psutil.disk_partitions(all=True)
    for partition in partitions:
        drive_letter = partition.device[:2] 
        # Extract the drive letter (e.g., 'C:')
        print(f"Initiating disk cleanup on drive {drive_letter}")
        initiate_disk_cleanup(drive_letter)
        
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\n\033[1;92mTotal time taken: {elapsed_time:.2f} seconds\033[0m")    

    os.system('pause')

if __name__ == "__main__":
    main()
