#from Pololu_SMC import Pololu_SMC
from Pololu_SMC_mock import Pololu_SMC
from time import sleep


class Motors (object):
    '''
    Wrapper-Class around xxxx_Pololu_SMC driver

    This class handels two motors (drivers) and build a user friendly interface


    Author:    LunaX

    History
    APRIL 2015    initial

    '''

    current_speed=[0,0]

    def __init__(self, driverLeftId, driverRightId, serial, baud, resetGPIO, errorGPIO, callbackFuncError):
        '''
            Constructor
            driverLeftID     physical SMC ID
            driverRightID    physical SMC ID
            serial            serial device
            baud              baud rate
            resetGPIO         reset GPIO-Pin, IF LOW, SMC reset
            errorGPIO         HIGH if error occurred
            callbackFuncError callback function if error occurred

        '''
        self.motor = Pololu_SMC(serial, baud, resetGPIO, errorGPIO, callbackFuncError)
        self.driverLeft = driverLeftId
        self.driverRight = driverRightId
        self.callbackFuncError = callbackFuncError
        sleep(0.5)
        self.motor.ExitSafeStart(self.driverLeft)
        self.motor.ExitSafeStart(self.driverRight)

        self.InverseMotors(False, False)
        sleep(0.5)

        pass

    def __repr__(self):
        msg = "Motors_Speed[%r, %r] inverse [%r, %r]"
        #print msg % (self.current_speed[0], self.current_speed[1],
        #             self.inverse[0], self.inverse[1] )


    def getMaxSpeed():
        return self.motor.getMaxSpeed()

    def getMinSpeed():
        return self.motor.getMinSpeed()

    def InverseMotors(self, inverseLeft=False, inverseRight=False):
        '''
        reverse motor movement. Useful if left or right (or both) motors should
        be initial turn into opposite direction

        '''
        self.inverse = [inverseLeft, inverseRight]
        #print "inverse [left,right]",self.inverse
        pass


    def Go(self, speed=()):
        '''
           Both motors turn into the same direction. If speed is positive, Motors turn CW, otherwise CCW

        '''
        if (speed[0] >= 0):
            self.motor.Forward(self.driverLeft, speed[0], self.inverse[0])
        else:
            #print "BWD - L"
            self.motor.Backward(self.driverLeft, speed[0], self.inverse[0])

        if (speed[1] >= 0):
            self.motor.Forward(self.driverRight, speed[1], self.inverse[1])
        else:
            #print "BWD - R"
            self.motor.Backward(self.driverRight, speed[1], self.inverse[1])

        self.current_speed = speed
        pass


    def SmoothStop(self, duration=1000):
        '''
        Stop motors smoothly in duration-ms from current speed down to 0
        '''

        pass

    def Shutdown(self):
        self.Stop()
        self.motor.Close()
        pass

    def Stop(self):
        self.motor.Stop(self.driverLeft)
        self.motor.Stop(self.driverRight)
        pass

    def Start(self):
        self.motor.ExitSafeStart(self.driverLeft)
        self.motor.ExitSafeStart(self.driverRight)
        pass
