#!/bin/env python3

from serial.tools.list_ports import comports
import os

bold            = "\033[1m"
color_red       = "\033[31m"
color_reset     = "\033[0m"

if 'DEV_SERIAL_NUM' in os.environ.keys():
    # specify DEV_SERIAL_NUM=1234ABCD and this will print the port
    for p in comports():
            if p.serial_number == os.environ['DEV_SERIAL_NUM']:
                print(p.device)
else:
    print(bold+'device'+color_reset,bold+'serial_number'+color_reset,sep='\t\t')
    for p in comports():
        print(p.device,p.serial_number,sep='\t')
