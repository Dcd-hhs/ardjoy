#!/usr/bin/python3
"""
    inspired by
    https://stackoverflow.com/questions/54557530/matplotlib-real-time-plotting-in-python
    user: clockelliptic

"""

from time import sleep
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
print(f"rcparams says: {mpl.rcParams['backend']}")
mpl.use("TkAgg") #interactive mode can be on now. plt.ion()
#import serial
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

# specify how many points to show on the x-axis
xwidth = 10

# use real-time plotting
plt.ion()

# setup each of the subplots
ax = []
fig, ax[0:7] = plt.subplots(7, 1, sharex=False, sharey=False)

# set up each of the lines/curves to be plotted on their respective subplots
lines = {index: Axes_object.plot([],[])[0] for index, Axes_object in enumerate(ax)}

# cache background of each plot for fast re-drawing, AKA Blit
ax_bgs = {index: fig.canvas.copy_from_bbox(Axes_object.bbox)
          for index, Axes_object in enumerate(ax)}

# initial drawing of the canvas
fig.canvas.draw()
plt.show()
# setup variable to contain incoming serial port data
y_data = {index:[0] for index in range(len(ax))}
x_data = [-1]

def startcom():
    global ser, serOpen
    if ser == None:
        try:
            ser=serial.Serial('/dev/'+portlist[1].name,115200, timeout = 1)
            #ser=serial.Serial('COM3',115200, timeout = 1)
            sleep(1)
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
def printstick(stickdata):
    #print(f'this is data from the stick: {stickdata}')
    print(f'I: {1023-stickdata[channel["I"]]} ',end='')
    print(f'J: {stickdata[channel["J"]]} ',end='')
    print(f'X: {1023-stickdata[channel["X"]]} ',end='')
    print(f'Y: {stickdata[channel["Y"]]} ',end='')
    print(f'Z: {stickdata[channel["Z"]]} ',end='')
    print(f'L: {stickdata[channel["L"]]} ',end='')
    print(f'R: {stickdata[channel["R"]]}')
    print(f'\033[A\033[A')


def update_data(new_byte, ):
    print(new_byte)
    x_data.append(x_data[-1] + 1)
    for i, val in enumerate(new_byte):
        y_data[i].append(val)

def update_graph():
    for i in y_data.keys():
        # update each line object
        lines[i].set_data(x_data, y_data[i])

        # try to set new axes limits
        try:
            #print('I do!')
            ax[i].set_xlim([x_data[-1] - xwidth, x_data[-1]])
            if max(y_data[i][-xwidth:]) > ax[i].get_ylim()[1]:
                new_min = min(y_data[i][-xwidth:])
                new_max = max(y_data[i][-xwidth:])
                ax[i].set_ylim([new_min-abs(new_min)*0.2, new_max+abs(new_max)*0.2])
        except:
            continue

    fig.canvas.draw()


#ser = serial.Serial('COM3', 115200) # Establish the connection on a specific port
#byte=ser.readline() #first line not to be plotted
if (ser == None):
    startcom()
sw=None
run = 1
while run:
    # ser.write(b'9') # send a command to the arduino
    # byte=ser.read(7) #read 7 bytes back
    stickdata = readstick()
    if sw==None:
           sw=stickdata[channel['R']]
    if sw<stickdata[channel['R']]-350:
        #print(f'Stopping now, because turn to right')
        run=False
    if sw==360 and stickdata[channel['R']]<sw-350:
        run=False
    byte = np.random.rand(7)
    printstick(stickdata)
    update_data(stickdata)
    update_graph()
    #print(x_data,y_data)
