#!/usr/bin/python3
"""
Author: D.C.Doedens
Date: 20220410
Goal:
    Use input from joystick to generate and plot data in matplotlib
    Both this programme and the programme on the joystick use the ibus protocol
    based on/ inspired by VJoySerialFeeder

TODO:
    - Get the serial stream of data
      - Connect to serial
      - Receive data
        - decode data
    - Plot the joydata in a 'live' plot with matplotlib
      - get matplotlib to work with live data
        - stuff..
    - Genereate live data through another source, and modify the plot settings
      using the joydata
    - change to gitlab?

DONE:
    - setup the Github thing
"""
import time
import matplotlib.pyplot as plt
import numpy as np
##
pi=np.pi
tau = 2*pi

## global variable handler, whether you like it or not
run = 0

## Communication with arduino
import serial
import serial.tools.list_ports
portlist = serial.tools.list_ports.comports()
for port in portlist:
    print(f'This should be a port: {port.name}')
ser = None
serOpen = False
channels = [0]
channel={'I':0,'J':1,'Z':2,'X':3,'Y':4,'R':5,'L':6}

def startcom():
    global ser, serOpen
    if ser == None:
        try:
            ser=serial.Serial('/dev/'+portlist[1].name,115200, timeout = 1)
            #ser=serial.Serial('COM3',115200, timeout = 1)
            time.sleep(1)
            print("Go ahead make my day (establishing communications)")
            serOpen = True
            print("Connected on: ", ser.name)
        except serial.SerialException as e:
            print("Then this happened:\n{}".format(e))
            print(ser.name)

def endcom():
    global ser, serOpen
    print("See you later alligator")
    if not ser == None:
       ser.close()
       serOpen = False
def readstick():
    global ser, serOpen
    global channels
    if serOpen:
        dataExp = (1+1+4*2+2)               #1 size + 1 key + numchannels*2 + 2 byte checksum
        key = 64
        #print("datasize should be:",dataExp)
        if ser.inWaiting()>dataExp:         # throw away old data, assuming the joystick updates
            ser.flushInput()                # faster than this script
        c=ser.read(2)                       # get size and key
        dataRecv = c[0]                     # datasize to be received
        dataPart = dataRecv -2              # size and key are not data
        check1 = dataPart -1                # Big byte
        check2 = dataPart -2                # Small byte
        buffer=bytearray(dataPart)          # data fits in buffer
        #print( "datalength {}, big bytenr {}, small bytenr {}".format(dataPart, check1, check2))
        if c[1] == key:                     # second byte sent by arduino16
            #print('datasent: {} and key: {}'.format(c[0], c[1]))
            #print('key approved')
            buffer=ser.read(dataPart)
            checksum = 0xffff - dataRecv - key ## initialise checksum
            #print('checksum' , checksum, [i for i in buffer])
            for i in range(dataPart -2):    # leave checksum out of checksum calculation
                checksum -= buffer[i]
                #print("check: ",checksum, (buffer[check1] << 8) + buffer[check2])
            if checksum == (buffer[check1] << 8) + buffer[check2]:
                #print('checksum correct') # high chance that data is correct too.
                channels=[]
                for ch in range(0,dataPart - 2,2):
                    channels.append(buffer[ch]+256*buffer[ch+1])
                #print([i for i in range(0,dataPart - 2, 2)])
                #print(f'this is the data from all channels: {channels}')
                return channels        # give new values
            #print('checksum failed')
            #print(buffer)
        print('key invalid')
        return channels #give old values

def main():
    global run, ser
    run = 1
    if (ser == None):
        startcom()
    sw=None
    while run:
        stickdata = readstick()
        #print(stickdata)
        if sw==None:
           sw=stickdata[channel['R']]
        if sw<stickdata[channel['R']]:
            print(f'Stopping now, because turn to right')
            run=False
        if sw==360 and stickdata[channel['R']]<sw:
            run=False
            print(f'stopping now, because turn to left?')
        #print(f'this is data from the stick: {stickdata}')
        print(f'I: {1023-stickdata[channel["I"]]} ',end='')
        print(f'J: {stickdata[channel["J"]]} ',end='')
        print(f'X: {1023-stickdata[channel["X"]]} ',end='')
        print(f'Y: {stickdata[channel["Y"]]} ',end='')
        print(f'Z: {stickdata[channel["Z"]]} ',end='')
        print(f'L: {stickdata[channel["L"]]}')

if __name__ == '__main__':
    main()
