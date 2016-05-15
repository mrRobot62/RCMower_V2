# -*- coding: utf-8 -*-

from time import sleep


class Pololu_SMC:
    '''
        MOCK - simulate a pololu motor driver class
        
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
    serial = None
    
    def __init__(self, serialPort, baud, resetGPIO, errorGPIO, errorCallback):
        self.serial = serialPort
        print ("{0} - SerialPort:{1}".format(self.__class__.__name__, serialPort))
        
        sleep(0.1)
        pass
    
    def getMaxSpeed(self):
        return self.__SPEED_MAX
        
    def getMinSpeed(self):
        return self.__SPEED_MIN
        
    
    def SetDefaults(self, MAXSPEED=3200, MINSPEED=500):
        self.__SPEED_MAX = MAXSPEED
        self.__SPEED_MIN = MINSPEED
        pass
    
    def Close(self):
        print ("{0} Close ({1})".format(self.__class__.__name__, None ))
        pass
    
    def Open(self, serialPort, baud):
        print ("{0} Open ({1}, {2})".format(self.__class__.__name__, serialPort, baud ))
        if (self.serial) <= 0:
            self.errorCallback(self.serial, "can't open serial port")
            return None
        pass
        
    def Stop(self, driverId):
        print ("{0} Stop (ID: {1})".format(self.__class__.__name__, driverId ))
        pass
        
        
    def Reverse(self, driverId):
        print ("{0} Reverse (ID: {1})".format(self.__class__.__name__, driverId ))
        pass
    
    def ExitSafeStart(self, driverId):
        print ("{0} ExitSafeStart (ID: {1})".format(self.__class__.__name__, driverId ))
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
        print ("{0} Forward ({1})".format(self.__class__.__name__, self.buffer ))
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
        print ("{0} Backward ({1})".format(self.__class__.__name__, self.buffer ))
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
        print ("{0} Break ({1})".format(self.__class__.__name__, self.buffer ))
        pass
    
    def getTemperatur(self, driverId):
        # temp in 0.1 steps => 286 = 28.6degree
        return 0    
        pass
    
    def getVINVoltage(self, driverId):            
        # VIN in 0.1 steps 253 = 25.3Volt
        return 0      
        pass
    
    def __readSMCByte(self):
        return 0
     
    def __sendBuffer(self, buf, size):            
        return 0
        
    def __readVariable(self, driverId, variableID):
        return 0
        
        
