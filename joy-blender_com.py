### Joyblend.blend script
"""
Author: D.C.Doedens
Date:   20210601
Goal: 
    Use input from joystick to move my 3D model.
    Both this program and the programme on the joystick use the ibus protocol
    based/inspired by on VJoySerialFeeder   

TODO:
    - Make a nice 3D model

DONE:
    - Make a proof of concept 3D model
    - Connect to serial
    - Receive data
        - Decode data
        - Assign data to model

"""
###


import bge
import serial
import time
import mathutils


## BGE control parameters ##
sceneEnd = False
gcc = bge.logic.getCurrentController()
scene = bge.logic.getCurrentScene()
own = gcc.owner
print(scene.objects)

ape=scene.objects["Suzanne"]
LUArm=scene.objects["L.UArm"]
LLArm=scene.objects["L.LArm"]
LHand=scene.objects["L.Hand"]
LUEye=scene.objects["L.UEye"]

## Communication with arduino
ser=None
serOpen = False
channels=[0]

print(time.ctime(time.time()))

def startcom():
    global ser, serOpen
    if ser==None:
        try:
            ser=serial.Serial('COM3',115200, timeout = 1)
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
                print(channels)
                return channels        # give new values
            #print('checksum failed')
            #print(buffer)
        #print('key ivalid')
        return channels #give old values
        
def gamequit():
    global sceneEnd
    endcom()
    sceneEnd = True
    print("So long, and thanks for all the fish")
    bge.logic.endGame()

def moveparts():
    channels = readstick()
    ape.position.x=-(channels[3]-512) /1000
    ape.position.y= (channels[2]-512) /1000
    ape.position.z= (channels[4]-512) /1000
    ape.localOrientation = mathutils.Matrix.Rotation(channels[5]/180*3.14, 3, 'Z')
    LUEye.localOrientation = mathutils.Matrix.Rotation(channels[6]/180*3.14, 3, 'X')
    #ape.localOrientation = mathutils.Matrix.Rotation(channels[3]/180*3.14, 3, 'X')
    #ape.localOrientation = mathutils.Euler(
    #        (channels[2]/180*3.14,0,channels[3]/180*-3.14), 'XYZ')
    LUArm.localOrientation = mathutils.Matrix.Rotation(channels[0]/180/4,3,'Y')
    LLArm.localOrientation = mathutils.Matrix.Rotation(channels[1]/180,3,'Y')
    LHand.localOrientation = mathutils.Matrix.Rotation(channels[1]/180,3,'Y')


def main():
    if not sceneEnd:
        global ser
        if (ser == None):
            startcom()
        moveparts()

    
if __name__ == '__main__':
    main()