import datetime    
import webbrowser
import interface
import tkinter      #for Linux you must install tkinter and scrot
import socket
import time
import os
import struct
import win32api

import pyautogui
import cv2

import numpy as np  #pip install numpy
import cv2 as cv    #pip install opencv-python
import pyautogui    #pip install PyAutoGUI

from os import walk

status = ""


# Find the time for name
def find_time():
    x = datetime.datetime.now()
    date_for_name = (x.strftime("%d") + "-" + x.strftime("%m") + "-" + x.strftime("%Y") + "-" + x.strftime("%H") + "-" +
                     x.strftime("%M") + "-" + x.strftime("%S"))
    return date_for_name
def get_input():
    global hostname
    global username
    hostname = interface.hostname.get()
    username = interface.username.get()
    
def edit_checks(clicked):
    if clicked == "mp4":
        if interface.mp4_format.get() == False:
            interface.avi_format.set(True)
        else:
            interface.avi_format.set(False)
    elif clicked == "avi":
        if interface.avi_format.get() == False:
            interface.mp4_format.set(True)
        else:
            interface.mp4_format.set(False)


def result_format():
    if interface.mp4_format.get() == True:
        return ".mp4"
    else:
        return ".avi"

def result_format2():
    if result_format() == ".mp4":
        return "MP4V"
    else:
        return "XVID"


interface.video_format.add_checkbutton(label=".mp4", onvalue=1, offvalue=0, variable=interface.mp4_format,
                                       command=lambda: edit_checks("mp4"))
interface.video_format.add_checkbutton(label=".avi", onvalue=1, offvalue=0, variable=interface.avi_format,
                                       command=lambda: edit_checks("avi"))

# interface.about.add_command(label="Mehmet Mert Altuntas",
                            # command=lambda: webbrowser.open("https://github.com/mehmet-mert"))
def is_another_process_running():
    global singleton_socket
    singleton_socket = socket.socket()
    try:
        singleton_socket.bind(('127.0.0.1', 56231))
        singleton_socket.listen()
    except:
        return True
    return False

def send(screen, currtime, idletime, filename, username):
    sock = socket.socket()
    sock.settimeout(60)
    try:
        sock.connect((interface.hostname.get(), 56230))
        sock.sendall(struct.pack('<QQ64s64sI', 111, 222, filename.encode('utf-8'), interface.username.get().encode('utf-8'), len(screen)))
        sock.sendall(screen)
        sock.close()
        os.remove("Outputs/"+filename)
    except:
        print("coonect failed")
    
    # logfp.write('Sent {}\n'.format(time.strftime("%y:%m:%d %H:%M:%S", time.localtime())))

# Start button command
def create_vid():
    global out
    screen_size = pyautogui.size()
    fourcc = cv.VideoWriter_fourcc(*result_format2())
    out = cv.VideoWriter("Outputs/"+ interface.username.get()+ " " + find_time() + result_format(), fourcc, interface.switch.get(),
                         (screen_size))

def record():
    img = pyautogui.screenshot()
    frame = np.array(img)
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    out.write(frame)


def start_record():
    if status in ("end"):
        create_vid()
    status_playing("playing")

def stop_record():
    out.release()
    f = []
    # time.sleep(60)
    for (dirpath, dirnames, filenames) in walk("Outputs"):
        for file in filenames:
            print (file)
            imgfp = open("Outputs/"+file, 'rb')
            imgdata = imgfp.read()
            imgfp.close()
            send(imgdata, find_time(), find_time(), file, interface.username.get())
            time.sleep(1)

# Report what's happening
def status_playing(yeter):
    global status
    status = yeter
    if status == "stopped":
        interface.pause["state"] = "disabled"
        interface.start["state"] = "normal"
        interface.canvas.itemconfig(interface.info, text="Paused. Continue Recording with Play")
    elif status == "playing":
        interface.pause["state"] = "normal"
        interface.end["state"] = "normal"
        interface.start["state"] = "disabled"
        interface.canvas.itemconfig(interface.info, text="Recording...")
    elif status == "end":
        interface.canvas.itemconfig(interface.info, text="Video Saved At Outputs Folder. Let's Create Another One!")
        interface.pause["state"] = "disabled"
        interface.end["state"] = "disabled"
        interface.start["state"] = "normal"


interface.start.config(command=lambda: start_record())
interface.end.config(command=lambda: status_playing("end"))
interface.pause.config(command=lambda: status_playing("stopped"))

#interface.root.protocol("WM_DELETE_WINDOW", on_closing)
interface.running = True
while interface.running:
    interface.root.update()
    interface.switch.place(x=400, y=176, anchor=tkinter.CENTER)
    interface.start.place(x=318, y=230, width=172, height=58)
    interface.pause.place(x=118, y=230, width=172, height=58)
    interface.end.place(x=518, y=230, width=172, height=58)
    interface.root.config(menu=interface.menubar)
    if status == "playing":
        record()
    elif status == "stopped":
        pass
    elif status == "end":
        stop_record()
