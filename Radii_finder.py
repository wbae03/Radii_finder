import cv2 
import numpy as np
import time
import os
import pandas as pd
import itertools # for animated loading
import threading # for animated loading
import sys # for animated loading
import matplotlib.pyplot as plt
import numpy as np
import math
import tkinter as tk
from tkinter.filedialog import askopenfilename
import ntpath
from colorama import init

init() # related to colorama, to enable ANSI escape codes for color

# Create a single instance of Tk
root = tk.Tk()
# Set the window attributes
root.wm_attributes('-topmost', 1)
# Withdraw the window
root.withdraw()


RED = "\33[91m"
BLUE = "\33[94m"
GREEN = "\033[32m"
YELLOW = "\033[93m"
PURPLE = '\033[0;35m' 
CYAN = "\033[36m"
LBLUE = "\033[94m"
END = "\033[0m"
BOLD = "\033[1m"

# Global variables

size_ratio = 0.3

calibration_ratio = 0




def on_mouse_calibration(event, x, y, flags, param): # although flags and param are not used in this function, they must be included in the parameters as the data from mouse clicks feeds into this function and includes these parameters.

    global finished_drawing, drawing, sbox, line_coords, temp_image, calib_pixel_length, calib_real_length, calib_user_ready, calibration_ratio, close_calib_window

    x = math.floor(x * 1/size_ratio) # note: resizing the window size DOES NOT scale down the frames system / mouse coordinate system.. must convert the mouse values by applying an opposite scale (ie if the frame is scaled down by 0.5 of original size, then scale mouse coordinates by 1/0.5 aka x2 !!)
    
    y = math.floor(y * 1/size_ratio)
    

    if event == cv2.EVENT_LBUTTONDOWN and finished_drawing == False:

        print(f'\n{RED}[PROGRAM] > {END}Start Mouse Position: {YELLOW}[' + str(x) + ',' + str(y) + f']{END}')

        sbox = [x, y]

        line_coords.append(sbox)

        drawing = True

    elif event == cv2.EVENT_MOUSEMOVE and finished_drawing == False:
        
        if drawing:

            temp_image = calib_img.copy()  # Reset to the original image

            cv2.line(temp_image, tuple(sbox), (x, y), (0, 0, 255), 4)

    elif event == cv2.EVENT_LBUTTONUP and finished_drawing == False:
        
        finished_drawing = True
        
        print(f'\n{RED}[PROGRAM] > {END}End Mouse Position: {YELLOW}[' + str(x) + ',' + str(y) + f']{END}')
        ebox = [x, y]
        line_coords.append(ebox)
        drawing = False
        # Draw the final line on the main image
        cv2.line(calib_img, tuple(sbox), tuple(ebox), (0, 0, 255), 5)

        # use pythagorean theorem to find length of line
        x_length = abs(sbox[0] - ebox[0])
        y_length = abs(sbox[1] - ebox[1])
        calib_pixel_length = round(math.sqrt(x_length**2 + y_length*2), 2)
        print(f'\n{RED}[PROGRAM] > {END}Calibration pixel length: {YELLOW}[', calib_pixel_length, f']{END}')


        calibration_ratio = round(float(calib_pixel_length) / float(calib_real_length), 2) # magnification = image length / actual length
        print(f'\n{RED}[PROGRAM] > {END}Calibration successful. The calibration ratio is: {YELLOW}[', calibration_ratio, f']{END}. \n\nPlease write down this value if you will be analyzing more video data in the future, so you can enter the calibration ratio.')
        cv2.destroyWindow('Calibration Window')

def on_mouse_radius(event, x1, y1, flags, param): # although flags and param are not used in this function, they must be included in the parameters as the data from mouse clicks feeds into this function and includes these parameters.

    global finished_drawing, drawing, sbox, line_coords, temp_image, calib_pixel_length, calib_real_length, calib_user_ready, actual_radius, close_calib_window

    x1 = math.floor(x1 * 1/size_ratio) # note: resizing the window size DOES NOT scale down the frames system / mouse coordinate system.. must convert the mouse values by applying an opposite scale (ie if the frame is scaled down by 0.5 of original size, then scale mouse coordinates by 1/0.5 aka x2 !!)
    
    y1 = math.floor(y1 * 1/size_ratio)
    

    if event == cv2.EVENT_LBUTTONDOWN and finished_drawing == False:

        print(f'\n{RED}[PROGRAM] > {END}Start Mouse Position: {YELLOW}[' + str(x1) + ',' + str(y1) + f']{END}')

        sbox = [x1, y1]

        sx, sy = [x1], [y1]

        line_coords.append(sbox)

        drawing = True

    elif event == cv2.EVENT_MOUSEMOVE and finished_drawing == False:
        
        if drawing:

            temp_image = radius_img.copy()  # Reset to the original image

            midpoint = ((sbox[0] + x1) // 2, (sbox[1] + y1) // 2)

            dx = x1 - sbox[0]
            dy = y1 - sbox[1]

            line_length = math.sqrt(dx ** 2 + dy ** 2)

            perp_dx = -dy
            perp_dy = dx

            perp_length = math.sqrt(perp_dx ** 2 + perp_dy ** 2)

            perp_dx = (perp_dx / perp_length) * (line_length / 2)
            perp_dy = (perp_dy / perp_length) * (line_length / 2)

            perp_start = (int(midpoint[0] + perp_dx), int(midpoint[1] + perp_dy))
            perp_end = (int(midpoint[0] - perp_dx), int(midpoint[1] - perp_dy))

            # Draw the original cursor line
            cv2.line(temp_image, tuple(sbox), (x1, y1), (0, 0, 255), 4)

            # Draw the perpendicular line
            cv2.line(temp_image, perp_start, perp_end, (0, 0, 255), 4)
         

    elif event == cv2.EVENT_LBUTTONUP and finished_drawing == False:
        
        finished_drawing = True
        
        print(f'\n{RED}[PROGRAM] > {END}End Mouse Position: {YELLOW}[' + str(x) + ',' + str(y) + f']{END}')
        ebox = [x, y]
        line_coords.append(ebox)
        drawing = False
        # Draw the final line on the main image
        cv2.line(radius_img, tuple(sbox), tuple(ebox), (0, 0, 255), 5)

        # use pythagorean theorem to find length of line
        x_length = abs(sbox[0] - ebox[0])
        y_length = abs(sbox[1] - ebox[1])
        calib_pixel_length = round(math.sqrt(x_length**2 + y_length*2), 2)
        print(f'\n{RED}[PROGRAM] > {END}Calibration pixel length: {YELLOW}[', calib_pixel_length, f']{END}')

        actual_radius = round(float(calib_pixel_length) / float(calibration_ratio), 2)
        print(f'\n{GREEN}-------------------------------------------------------------------------------------{END}')
        print(f'\n{RED}[PROGRAM] > {END}{GREEN}Radius is: [', actual_radius, f']{END}.')
        cv2.destroyWindow('Radius Window')


calib_user_ready = False

while calib_user_ready == False:
    
    calib_real_length = input(f'\n\n\n\n{RED}[PROGRAM] > {END}Please enter the actual length {YELLOW}[MICROMETERS]{END} of the calibration tool.\n\n{GREEN}[USER INPUT] > {END}')

    if calib_real_length.isnumeric():

        calib_user_ready = True

    else:
        print(f'\n{RED}[PROGRAM] > {END}Invalid input. Please enter the actual length {YELLOW}[MICROMETERS]{END} of the calibration tool')



while True:

    calib_user_ready = False

    ask_user_calib_ready = False

    close_calib_window = False

    drawing = False 

    finished_drawing = False

    line_coords = []

    actual_radius = 0

    print(f'{GREEN}-------------------------------------------------------------------------------------{END}\n')
    print(f'\nCurrent calibraiton ratio stored in memory is: {calibration_ratio}')

    while not ask_user_calib_ready: # While loop ensures the user prompts are repeated if the user input is invalid (ie not 'y' or 'n')

        ask_user_calib = input(f'\n{RED}[PROGRAM] >{END} Do you require calibration using an image with a known measurement (ie. using a ruler)? \nAlternatively, enter a calibration ratio {YELLOW}(pixel length / micrometer length){END} obtained from previous calibrations.\n\nPress {YELLOW}\'Y\'{END} to load a calibration scale image.\nPress {YELLOW}\'N\'{END} to determine the radii of droplet images.\n\n{GREEN}[USER INPUT] > {END}')

        if ask_user_calib.lower() == 'y':

            use_calib_image = True

            ask_user_calib_ready = True


        elif ask_user_calib.lower() == 'n':

            use_calib_image = False

            ask_user_calib_ready = True

        else:

            print(f'\n{RED}[PROGRAM] >{END} Invalid input. Please press {YELLOW}\'Y\'{END} or {YELLOW}\'N\'{END}.\n (Tip: if you do not require a calibration, you can just put in an arbitrary calibration value after press \'N\'){END}')


    if use_calib_image == True:

        calib_file = askopenfilename()

        print(f"\n{RED}[SYSTEM] >{END} Does the calibration file exist: ", os.path.exists(calib_file))

        calib_img = cv2.imread(calib_file)

        temp_image = calib_img.copy()

        cv2.namedWindow('Calibration Window')

        if finished_drawing == False:

            cv2.setMouseCallback('Calibration Window', on_mouse_calibration)
            
        print(f'\n{RED}[PROGRAM] > {END}In the calibration window, please draw a line parallel to the calibration tool / ruler by holding the left mouse button.\n\n{GREEN}[USER INPUT] > {END}')

        while close_calib_window == False:

            try:
                resized_temp_image = cv2.resize(temp_image, (0,0), fx = size_ratio, fy = size_ratio)
                cv2.setWindowProperty('Calibration Window', cv2.WND_PROP_TOPMOST, 1)
                cv2.moveWindow('Calibration Window',10,50)
                cv2.imshow('Calibration Window', resized_temp_image)
                cv2.startWindowThread()

            except:

                dummy = 1

            if calibration_ratio != 0:

                close_calib_window = True

            if cv2.waitKey(1) & 0xFF == 27:  # Exit on pressing 'ESC'
             
             break




    elif use_calib_image == False:

        if calibration_ratio == 0:

            while calib_user_ready == False:
                calibration_ratio = input(f'\n{RED}[PROGRAM] > {END}Please enter a {YELLOW}calibration ratio{END} value. \nThis value may be obtained from previous calibrations or analysis of videos with the same dimensions.\n\n{GREEN}[USER INPUT] > {END}')

                try:
                    if isinstance(float(calibration_ratio), float): # checks if the instance is a number

                        calib_user_ready = True
                        print(f'\n{RED}[PROGRAM] > {END}Calibration successful. The calibration ratio value is: {YELLOW}[', calibration_ratio, f']{END}.\n Please write down this value if you will be analyzing more video data in the future, so you can enter the calibration ratio.')

                except:
                    print(f'\n{RED}[PROGRAM] > {END}Invalid input. Please enter the calibration ratio. If unknown, please restart the program and use a calibration image.')

        else:
            print('')

        radius_file = askopenfilename()

        print(f"\n{RED}[SYSTEM] >{END} Does the radius file exist: ", os.path.exists(radius_file))

        print(f'\n{RED}[PROGRAM] > {END} Calibration ratio stored in memory is: {calibration_ratio}')

        radius_img = cv2.imread(radius_file)

        temp_image = radius_img.copy()

        cv2.namedWindow('Radius Window')

        if finished_drawing == False:

            cv2.setMouseCallback('Radius Window', on_mouse_radius)

        print(f'\n{RED}[PROGRAM] > {END}In the radius window, please draw a line spanning the diameter of the circl of interest. \n\n{GREEN}[USER INPUT] > {END}')

        while close_calib_window == False:

            try:
                resized_temp_image = cv2.resize(temp_image, (0,0), fx = size_ratio, fy = size_ratio)
                cv2.setWindowProperty('Radius Window', cv2.WND_PROP_TOPMOST, 1)
                cv2.moveWindow('Radius Window',10,50)
                cv2.imshow('Radius Window', resized_temp_image)
                cv2.startWindowThread()
            except:
                dummy = 1

            if actual_radius != 0:
                close_calib_window = True

            if cv2.waitKey(1) & 0xFF == 27:  # Exit on pressing 'ESC'
                break
