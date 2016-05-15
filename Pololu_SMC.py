
import sys
from time import sleep
import RPi.GPIO as GPIO
import wiringpi2

#import logging
#import logging.config






class Pololu_SMC:
    '''
        Motorcontroller for Pololu SimpleMotorController
        like 18v7, 18v15, 24v12, 18v25, 24v23
        
        Use Serial/USB Pololu-Protocol
        
        Preconditions for SMC-Boards
        1)    fixed baud rate of 57600 configured on all connected boards
        2)    used for binary mode
        3)    CRC mode disabled
       
       Author: LunaX 
       
       History    
       APRIL 2015    initial
       
    '''
    __SPEED_MAX = 3200
    __SPEED_MIN = 500
    __SPEED_STOP = 0
    
    CMD_POLOLU_PROTOCOL = 0xAA
    CMD_FORWARD     = 0x05
    CMD_BACKWARD    = 0x06
    CMD_FORWARD7    = 0x09
    CMD_BACKWARD7   = 0x0A
    CMD_BRAKE       = 0x12
    CMD_GETVAR      = 0x21
    CMD_SETLIMIT    = 0x22
    CMD_GETVERSION  = 0x42
    CMD_STOP        = 0x60
    CMD_EXITSTART   = 0x03

    VAR_TEMP        = 0x18
    VAR_VIN         = 0x23

    
    buffer = [0]*10
    
    def __init__(self, serialPort, baud, resetGPIO, errorGPIO, errorCallback):
        self.resetGPIO = resetGPIO
        self.errorGPIO = errorGPIO
        self.errorCallback = errorCallback
        self.Open(serialPort, baud)
        # simple motor controller must be running for at least 1ms
        # before we try to send serial data. Let us wait 100ms
        print ("{0} serial {1}".format(self.__class__.__name__,self.serial))
        
        sleep(0.1)
        pass
    
    def getMaxSpeed():
        return __SPEED_MAX
        
    def getMinSpeed():
        return __SPEED_MIN
        
    
    def SetDefaults(self, MAXSPEED=3200, MINSPEED=500):
        self.__SPEED_MAX = MAXSPEED
        self.__SPEED_MIN = MINSPEED
        pass
    
    def Close(self):
        '''
            close serial conneciton to SMC board
        '''
        wiringpi2.serialClose(self.serial)
        pass
    
    def Open(self, serialPort, baud):
        '''
            open serial connection to SMC board
        '''
        self.serial = wiringpi2.serialOpen(serialPort,baud)
        if (self.serial) <= 0:
            self.errorCallback(self.serial, "can't open serial port")
            return None
        pass
        
    def Stop(self, driverId):
        '''
            Stop motor(s)
            
            4 bytes buffer is send
            0 = protocoll
            1 = driver id
            2 = STOP command
            
        '''
        self.buffer = [0] * 3
        self.buffer[0] = self.CMD_POLOLU_PROTOCOL
        self.buffer[1] = driverId
        self.buffer[2] = self.CMD_STOP
        if self.__sendBuffer(self.buffer, len(self.buffer)) < 0:
            self.errorCallback(-2, "Stop send buffer smaller than number of send bytes")
            pass
        pass
        
        
    def Reverse(self, driverId):
        pass
    
    def ExitSafeStart(self, driverId):
        '''
        SMC-Board goes after restart into a motor save mode to avoid 
        motor starts. To clear the safe-start violation,  this method must be
        called one-time before we want to use systems.
        Must be called after every restart/reboot and any error
        '''
        wiringpi2.serialPutchar(self.serial, self.CMD_POLOLU_PROTOCOL)
        wiringpi2.serialPutchar(self.serial, driverId)
        wiringpi2.serialPutchar(self.serial, self.CMD_EXITSTART)
        pass
        
       
    def Forward(self, driverId, speed, inverse=False):
        '''
            forward command for driverID with speed
            
            5 bytes buffer
            0 = protocoll
            1 = driver id
            2 = forward/backward
            3 = 5 low bits from speed
            4 = 7 high bits from speed
        '''
        speed = int(speed)
        if (speed < 0):
            speed = abs(speed)
        if (speed > self.__SPEED_MAX):
            speed = self.__SPEED_MAX
        if (speed < self.__SPEED_MIN and speed != 0):
            speed = self.__SPEED_MIN
            
        self.buffer = [0]*5
        self.buffer[0] = self.CMD_POLOLU_PROTOCOL
        self.buffer[1] = driverId
        if inverse == False:
            self.buffer[2] = self.CMD_FORWARD
        else:
            self.buffer[2] = self.CMD_BACKWARD
            
        # separate into two bytes
        # speed[0] = 5 low bits from speed
        # speed[1] = 7 high bits from speed
        speed = [(speed & 0x1F), (speed >> 5)] 
        self.buffer[3] = speed[0]
        self.buffer[4] = speed[1] 
        #print "Forward ", self.buffer
        if self.__sendBuffer(self.buffer, len(self.buffer)) < 0:
            self.errorCallback(-2, "Forward send buffer smaller than number of send bytes")
            pass
        pass
    
    def Backward(self, driverId, speed, inverse=False):
        '''
            backward command for driverID with speed
            
            5 bytes buffer
            0 = protocoll
            1 = driver id
            2 = forward/backward
            3 = 5 low bits from speed
            4 = 7 high bits from speed
        '''
        speed = int(speed)
        if (speed < 0):
            speed = abs(speed)
        if (speed > self.__SPEED_MAX):
            speed = self.__SPEED_MAX
        if (speed < self.__SPEED_MIN and speed != 0):
            speed = self.__SPEED_MIN
        self.buffer = [0]*5
        self.buffer[0] = self.CMD_POLOLU_PROTOCOL
        self.buffer[1] = driverId
        if inverse == False:
            self.buffer[2] = self.CMD_BACKWARD
        else:
            self.buffer[2] = self.CMD_FORWARD
        # separate into two bytes
        # speed[0] = 5 low bits from speed
        # speed[1] = 7 high bits from speed
        speed = [(speed & 0x1F), (speed >> 5)] 
        self.buffer[3] = speed[0]
        self.buffer[4] = speed[1] 
        #print "Backward", self.buffer
        if self.__sendBuffer(self.buffer, len(self.buffer)) < 0:
            self.errorCallback(-2, "Backward send buffer smaller than number of send bytes")
            pass
        pass
    
    def Brake(self, driverId, brakeAmount):
        '''
        send brake command to SMC. brakeAmount indicate value of braking
        0    = maximum coasting
        32   = full braking
        '''
        # prevent a serial error if brakeAmount is not in rang
        
        if (brakeAmount > 32):
            brakeAmount = 32
        if (brakeAmount < 0):
            brakeAmount = 0
        self.buffer = [0]*4
        self.buffer[0] = self.CMD_POLOLU_PROTOCOL
        self.buffer[1] = driverId
        self.buffer[2] = self.CMD_BRAKE
        self.buffer[3] = (brakeAmount >> 0) & 0xFF 
        self.__sendBuffer(self.buffer, len(self.buffer))
        pass
    
    def getTemperatur(self, driverId):
        # temp in 0.1 steps => 286 = 28.6degree
        return self.__readVariable(driverId, self.VAR_TEMP)    
        pass
    
    def getVINVoltage(self, driverId):            
        # VIN in 0.1 steps 253 = 25.3Volt
        return self.__readVariable(driverId, self.VAR_VIN)      
        pass
    
    def __readSMCByte(self):
        '''
        read one byte from SMC-Controller if available
        otherwise return -1
        '''
        if wiringpi2.serialDataAvail(self.serial) < 1:
            return -1
        return wiringpi2.serialGetChar()
     
    def __sendBuffer(self, buf, size):
        '''
        send number of size bytes from buffer to SMC-controller
        if size > than buffer, method return -1
        if error occured method return -1
        otherwise return number of sent bytes (size)
        '''
        if len(buf) < size:
            return -1
        for b in range (0,size):
            #print buf[b]
            wiringpi2.serialPutchar(self.serial, buf[b])
            
        return 0
        
    def __readVariable(self, driverId, variableID):
        '''
        read variableID from SMC. Send 4Bytes and receive 2 Byte
        return integer value in 0.1 units
        '''
        self.buffer = [0]*4
        self.buffer[0] = self.CMD_POLOLU_PROTOCOL
        self.buffer[1] = driverId
        self.buffer[2] = self.CMD_GETVAR
        self.buffer[3] = variableID 
        self.__sendBuffer(self.buffer, len(self.buffer))
        # reading data from SMC
        b = [0,0]
        b[0] = self.__readSMCByte();
        b[1] = self.__readSMCByte();
            
        # temp in 0.1 steps => 286 = 28.6degree
        return (b[0] + 256 * b[1])      
        
        

