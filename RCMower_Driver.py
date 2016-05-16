# -*- coding: utf-8 -*-

from Motors import Motors

def Err():
    pass

class RCMower_Driver(object):
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config

        l_id = self.config['MOTORS']['LEFT']['ID']
        r_id = self.config['MOTORS']['RIGHT']['ID']
        serial = self.config['GENERAL']['SERIAL']
        baud = self.config['GENERAL']['BAUD']
        g_rst = self.config['GPIO']['MOTOR_RESET']
        g_err = self.config['GPIO']['MOTOR_ERROR']

        self.motors = Motors(l_id, r_id, serial, baud, g_rst, g_err, getattr(RCMower_Driver, "MotorErrorCallback"))
 #       self.motors = Motors(l_id, r_id, serial, baud, g_rst, g_err, Err)
        self.motors.Stop()
        self.motors.InverseMotors(self.config['MOTORS']['LEFT']['REVERSE'], self.config['MOTORS']['RIGHT']['REVERSE'])

    #@staticmethod
    def MotorErrorCallback(self):
        pass

    def Stop(self):
        self.motors.Stop()
        pass

    def Go(dataVel):
        self.motors.Go(dataVel.getMotorSpeed())
        pass
