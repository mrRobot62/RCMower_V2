# -*- coding: utf-8 -*-

import pygame
#import sys
import os
import yaml
#import sys
#import time
#import subprocess
#import evdev

from evdev import *
#from time import sleep
from threading import Thread, Timer
#import threading
from random import randint
from asyncio import *
#from Queue import Queue
from RCMower_Driver import *
from RCMower_Screens import *
from RCMower_Data import *

class RCMower():
    SURF = None
    running = False
    screens = []
    driver = None
    cfg_file = None
    dataVel = None
    screen_size = []
    cnt = 0
    reboot_nodevicefound = False

    codetype = None
    ctrldevice = None
    eventQueue = None

    def __init__(self):
        self.class_name = self.__class__.__name__
        self._load_config()

        print ("prepare framebuffer...")
        self._prepareFramebuffer()

        #---- initiate pygame
        #os.environ["SDL_FBDEV"] = "/dev/fb0"
        pygame.init()
        print ("Framebuffer size: {0} x {1}".format (self.screen_size[0], self.screen_size[1]))

        print ("prepare pygame 1")
        self.SURF = pygame.display.set_mode( (self.screen_size[0], self.screen_size[1]) )
        #---- load screens
        print ("prepare pygame 2")
        self.screens.append(Screen_VELOCITY(self, self.SURF, self.cfg_file["GENERAL"]["SCREEN_CFG"]))

        print("prepare data class")
        #--- initate data class
        self.dataVel = Data_Velocity(self.cfg_file)
        self.dataVel.setSpeedLimits(self.cfg_file['MOTORS']['SPEED_MAP'])
        #--- initate driver class
        print("prepare RCMower driver class")
        self.driver = RCMower_Driver(self, self.cfg_file)
        self.driver.Stop()

        #--- initiate global variables
        self.currentScreenID=0
        self.running = False
        self.restarting = False

        self.reboot_nodevicefound = self.cfg_file["GENERAL"]['REBOOT_NODEVICE']

        self.ESTOP_LEFT = self.cfg_file['CONTROLLER']['ESTOP_LEFT']
        self.ESTOP_RIGHT = self.cfg_file['CONTROLLER']['ESTOP_RIGHT']

        self.eStopButtons = {self.ESTOP_LEFT:True, self.ESTOP_RIGHT:True}

        print("setup event handling")
        #self.eventQueue = PriorityQueue()
        self.ctrldevice = self.cfg_file['GENERAL']['EVDEVICE']
        self.touchdevice = self.cfg_file['GENERAL']['TOUCHDEVICE']
        try:
            print ("get GamePad device...")
            self.ctrldevice = InputDevice(self.ctrldevice)
        except:
            print ("ERROR - can't open device {}".format(self.ctrldevice))
            os._exit(1)
        pass
        print ("setup finished")


    def _prepareFramebuffer(self):
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print ("I'm running under X display = {0}".format(disp_no))

        # Check which frame buffer drivers are available
        # Start with fbcon since directfb hangs with composite output
        drivers = ['fbcon', 'directfb', 'svgalib']
        found = False
        for driver in drivers:
            # Make sure that SDL_VIDEODRIVER is set
            if not os.getenv('SDL_VIDEODRIVER'):
                print ("set SDL_Videodriver({0})".format(driver))
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
            except pygame.error:
                print ('Driver: {0} failed.'.format(driver))
                continue
            found = True
            break

        if not found:
            raise Exception('No suitable video driver found!')

        print ("setup up SDL_evironment variables...")
        os.environ["SDL_FBDEV"] = self.cfg_file['GENERAL']['SDL_FBDEV']
        os.environ["SDL_MOUSEDEV"] = self.cfg_file['GENERAL']['SDL_MOUSEDEV']
        os.environ["SDL_MOUSEDRV"] = self.cfg_file['GENERAL']['SDL_MOUSEDRV']
        print (os.environ)

    def _load_config(self):
        '''
        load central configuration file
        '''
        try:
            cfg_file_name = "config/RCMower_config.yml"
            print ("read central config: '", cfg_file_name, "'")
            with open(cfg_file_name, 'r') as ymlfile:
                self.cfg_file = yaml.load(ymlfile)

            self.screen_size = self.cfg_file["GENERAL"]["SCREEN_SIZE"]

        except:
            print ("no config ", cfg_file_name, " file found")
            #os._exit(1)


    def setCurrentScreenID(self, id):
        self.currentScreenID = id
        pass

    def getCurrentScreenID(self):
        return self.currentScreenID

    def setRunning(self, gui, state=True):
        '''
        callback function

        from Screen_Actions

        '''
        self.running = state
        if (self.running == False):
            gui.stopScreen()
        else:
            gui.startScreen()

        print ("{0} - Set running ({1})".format(self.class_name, self.running))

    def getRunning(self):
        #print ("{0} - get running ({1})".format(self.class_name, self.running))
        return self.running

    def isEstopActive(self, event=None):
        if event != None:
            if event.value == self.cfg_file['CONTROLLER']['ESTOP_LEFT']:
                return self.dataVel.setEStop()
            elif event.value == self.cfg_file['CONTROLLER']['ESTOP_RIGHT']:
                return self.dataVel.setEStop()

        return self.dataVel.resetEStop()

    def checkEvdevAvailable(self):
        '''
        check if gamepad controller is available. if not
        sleep for 5secs and restart application -
        sometimes no event is recognized, so after restart normally it is
        '''
        gui=None
        devices = [InputDevice(fn) for fn in list_devices()]
        gui = self.screens[self.currentScreenID]
        if len(devices) == 0:
            gui.addMultipleLine(1,22,"No EvDev-device found")
            if self.reboot_nodevicefound:
                time.sleep(5)
                self.Do_Restart(gui)
            time.sleep(1.0)
            return False
            pass
        else:
            for dev in devices:
                gui.addMultipleLine(3,18,dev)
            return True
        pass

    #------- ACTION callback functions -----------------------------

    def Do_RunStop(self, gui):
        '''
        callback action funciton.

        called by button click from screen classes

        '''
        msg = "Do_RunStop ({0})".format(self.getRunning())
        print (msg)
        if self.getRunning() == True:
            self.setRunning(gui, False)
            self.dataVel.setSpeed(0,0)
            gui.addMultipleLine(2, 18, msg )
            gui.addMultipleLine(2,22, "ENGINE-STOPPED")
            pass
        else:
            gui.addMultipleLine(3, 18, msg )
            self.setRunning(gui, True)
            gui.addMultipleLine(3,22, "ready for run")
            msg = "SpeedFactor {0}".format(self.dataVel.getSpeedFactor())
            gui.addMultipleLine(3,18,msg)
        time.sleep(0.5)
        pass

    def Do_Restart(self, gui, wait=3.5):
        '''
        callback action funciton.

        called by button click from screen classes

        '''
        gui.addMultipleLine(1, 25, "RESTART APP" )
        msg = "Do_Restart in {0}secs ({1})".format(wait,gui)
        print (msg)
        time.sleep(wait)
        self.timer_hb.stop()
        pygame.display.quit()
        pygame.quit()
        time.sleep(2.5)
        #os.execv(__file__, sys.argv)
        os.execl(sys.executable, sys.executable, *sys.argv)
        pass

    def Do_Shutdown(self, gui):
        msg = "Shutdown initiated..."
        print (msg)
        pass

    def Do_Prev(self, gui):

        '''
        callback action funciton.

        called by button click from screen classes

        '''

        msg = "Do_Prev ({0})".format(self.cnt)
        gui.addMultipleLine(2 , 18, msg )
        print (msg)
        time.sleep(0.5)
        self.cnt += 1
        pass


    def Do_Next(self, gui):

        '''
        callback action funciton.

        called by button click from screen classes

        '''
        msg = "Do_Next ({0})".format(self.cnt)
        gui.addMultipleLine(2 , 18, msg )
        print (msg)
        time.sleep(0.5)
        self.cnt += 1
        pass

    def Do_HeartBeat(self,  *args, **kwargs):
        '''
        called from RepeatedTimer every xxSeconds

        '''
        self.screens[self.currentScreenID].heartBeat()

        pass

    #------------------------------------------------------------------------
    #-- EVENT-Handling
    #--
    #-- devicelistener is called as a daemon thread
    #-- if event is a keyboard or joystick event, put this event
    #-- into a queue
    #--
    #-- inside main loop, this queue is read and events will be processed
    #--
    #-- Priorities
    #-- 0  - EStop
    #-- 1  - Joystick values (ABS_X/Y, ...)
    #-- 5  - Speed-Factors
    #-- 10 - low prio commands
    #-------------------------------------------------------------------------
    def devicelistener(self):
        '''
        this method run as threaed. If current event is a key or a joystick
        put this evento to a queue
        '''
        for event in self.ctrldevice.read_loop():
            prio = 10
            if event.type == ecodes.EV_KEY or event.type == ecodes.EV_ABS:
                #analyseEvent(event)
                #if
                #self.eventQueue.put((prio,event))
                print (event)
                pass

    #--- called from devicelistener
    def analyseEvent(event):
        # is event inside our focus
        if event.type in ecodes.bytype:
            self.codetype = ecodes.bytype[event.type][event.code]
            if event.code == 304:
                self.codetype = 'BTN_A'
        else:
            return

        if (self.isEstopActive(event)):
            self.actionEStop(True)
        pass


    #----------- ACTIONS depending on events -----------------------
    def actionEstop(self, on=True):
        if on:
            self.dataVel.setEStop()
            self.driver.Stop()
            self.isEStop = True
        else:
            self.isEStop = False

        pass

    #-------------------- MAIN LOOP --------------------------------
    def run(self):
        '''
        central loop
        this while loop can be finished if user click restart-button on
        screen. Otherwise, this loop run endless
        '''

        self.timer_hb = RepeatedTimer(0.5,self.Do_HeartBeat, None, None)
        self.dataVel.setMotorDefaults(True,False)
        self.dataVel.setSpeedStop()
        self.dataVel.setEnergy(12.5, 12.2, 89)
        self.dataVel.setSpeedFactor(0.8)
        self.dataVel.setMixerOff()
        self.driver.Stop()
        self.running = False
        self.screens[self.currentScreenID].stopScreen()
        self.screens[self.currentScreenID].addMultipleLine(2,18, "ENGINE-STOPPED")

        self.screens[self.currentScreenID].addMultipleLine(3,18, "checkEvDevDeivce")
        device_cnt = 0
        while device_cnt < 5:
            if (self.checkEvdevAvailable()==False):
                device_cnt +=1
                self.screens[self.currentScreenID].addMultipleLine(2,18, "search evdev")
                time.sleep(1.0)
            else:
                device_cnt = 5

        #
        # analyse device events via daemon thread
        #
        t = Thread(target=self.devicelistener)
        t.daemon = True
        t.start()

        #-----------------------------------
        # MAIN-Loop
        #-----------------------------------
        self.screens[self.currentScreenID].addMultipleLine(3,22, "RUN")
        while self.restarting == False:
 #           if self.eventQueue.empty() != True:

            if (self.getRunning() == True):
                #--- system running
                sl = randint(-255,255)
                sr = randint(-255,255)
                self.dataVel.setSpeed(sl,sr)
                time.sleep(0.25)
            else:
                #--- system stopped
                pass



                #self.dataVel.setSpeed(sl,sr)
                #time.sleep(0.7)
#                pass

            self.screens[self.currentScreenID].checkButtons()
            self.screens[self.currentScreenID].update(self.dataVel.getDataDict())
            self.screens[self.currentScreenID].draw()

            for event in pygame.event.get():
                #print(event)
                if event.type == pygame.QUIT:
                    self.timer_hb.stop()
                    pygame.quit()
                    quit()




        #---------- RESTART initiated ---------------
        self.timer_hb.stop()
        self.timer_hb = None
        pass


class RepeatedTimer(object):
    def __init__(self,t,hFunction, *args, **kwargs):
        self._timer       = None
        self.t            = t
        self.hFunction    = hFunction
        self.args         = args
        self.kwargs       = kwargs
        self.is_running   = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.hFunction(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.t, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False



def main():
    print ("start mower....")
    mower = RCMower();
    mower.setCurrentScreenID(0)
    #mower.setRunning(False)
    mower.run()

    pass

if __name__ == '__main__':
    main()

    os._exit()
