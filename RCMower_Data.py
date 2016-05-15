# -*- coding: utf-8 -*-

class RCMower_Data(object):
    
    data = None 
    cfg_file = None
    def __init__(self, cfg_file):
        self.cfg_file = cfg_file
        pass
     
    @staticmethod       
    def map(self, v, imin, imax, omin, omax):
        '''
        map value in a min/max range into a new
        output ange out_min/out_max

        example :
            value = 127 (in_min=0, in_max=255)
            map to out_min=0, out_max=3200    => new value = 1600
   
           value = 255 (in_min=0, in_max=255)
           map to out_min=0, out_max=3200    => new value = 3200
        '''
        return (v-imin)*(omax-omin)/(imax-imin)+omin
        
    @staticmethod       
    def constrain(self, v, a, b):       
        '''
        check if v is >= a AND <= b
        return a if v is < a
        return b if v is > b
        else return v
        '''
        if v < a:
            return a
        if v > b:
            return b
        return v
        
    def adjust(self, v, adjustvalue=127):
        '''
        adjust value to zero and calculate it to a speed vector
        used for mapping joystick values. Center-position on joystick is
        127.
        
        step 1: this value is mapped to zero
        step 2: map value to max speed
        step 3: check limits
        step 4: adjust with speed factor
        '''        
        v -= adjustvalue
        if (v > 0):
            v = self.map(v,0,adjustvalue, 0, self.speedLimit[1])
        pass
    
class Data_Velocity(RCMower_Data):
    '''
        Speed:
            From controller values between -127 to +127 are send
            <0  = backward
            >=0 = forward
            
            Both Pololu controllers handels speed values between
            -3200(backward) & +3200(forward)

            Speedvalue for display is mapped between
            -255 to +255
            
            Stored value inside this class is value from controller

        'LEFT':{'DATA':1, 'VALUE':0, "FGCOLOR":None, "BGCOLOR":None},
        LEFT    => major data topic
        DATA    => Data value (e.g. boolean value, int value) used for special purposes
        VALUE   => Display value
        FGCOLOR => special foreground color (e.g. red if value is negativ)
        BGCOLOR => special background color 

    '''    
    
    
    isMixer1 = False
    isMixer2 = False
    
    speedLimit=[]
    motor_speedmap=[]
    controller_speedmap=[]
    gui_speedmap=[]
    
    dataChanged = False
    
    speed = {
        'LEFT':{'DATA':1, 'VALUE':0, "FGCOLOR":None, "BGCOLOR":None},
        'RIGHT':{'DATA':2, 'VALUE':0, "FGCOLOR":None, "BGCOLOR":None},
        'REVERSE_LEFT':{'VALUE':'', 'DATA': False},
        'REVERSE_RIGHT':{'VALUE':'', 'DATA': False},
        'MIXER1':{'VALUE':'', 'DATA': False},
        'MIXER2':{'VALUE':'', 'DATA': False},
        'SPEED_FACTOR':{'VALUE':0.0},
        'VOLT':{'VALUE':0.0},
        'AMPERE':{'VALUE':0.0},
        'CAPACITY':{'VALUE':0.0},
        'OFFSET':{'VALUE':0},
        'CHANGED':{'VALUE':False},
        'ESTOP':{'VALUE':False}
             }
             
    def __init__(self,cfg_file):
        '''
        gui_smap    = gui speedmap
        ctrl_smap   = controller speedmap
        smc_smap    = Pololu speedmap
        '''
        super(self.__class__,self).__init__(cfg_file) 
        self.gui_speedmap = self.cfg_file['GUI']['SPEED_MAP']
        self.controller_speedmap = self.cfg_file['CONTROLLER']['SPEED_MAP']
        self.motor_speedmap = self.cfg_file['MOTORS']['SPEED_MAP']
        self.setMixerOff() # all mixer off
        
        pass
    
    def isDataChanged(self):
        return self.dataChanged
    
    def __setDataChanged(self):
        self.speed['CHANGED']['VALUE'] = True
        self.dataChanged = True
    
    def setSpeedLimits(self, min, max):
        '''
        set speedLimit Array
        [0] = min
        [1] = max
        '''
        self.speedLimit=[]
        self.speedLimit.append(min)
        self.speedLimit.append(max)
        self.__setDataChanged()
        
    def setSpeedLimits(self, speedList):
        '''
        maximum speed values (Pololu-values => [-3200,3200])
        (min,max) 
        '''
        self.speedLimit = speedList
        self.__setDataChanged()
     
    def getSpeedLimits(self, index=None):
        '''
        return a speed limit list or only entry [MIN=0] or [MAX=1] 
        
        Values are Pololu-Values !
        
        '''
        if index == 0:
            return self.speedLimit[0]
        if index == 1:
            return self.speedLimit[1]
        return self.speedLimit        
    
    def setSpeed(self, left, right):
        '''
        set speed value for left & right motor
        change color if value is negative
        
        value represent the controller value (-127 to 127)
        
        '''
        self.__setDataChanged()
        self.speed['LEFT']['FGCOLOR']=None
        self.speed['RIGHT']['FGCOLOR']=None
        self.speed['LEFT']['BGCOLOR']=None
        self.speed['RIGHT']['BGCOLOR']=None
        
        if left < 0:
            self.speed['LEFT']['FGCOLOR']=0xFF0000FF
        if right < 0:
            self.speed['RIGHT']['FGCOLOR']=0xFF0000FF

        self.speed['LEFT']['VALUE']=left
        self.speed['RIGHT']['VALUE']=right
        pass
    
    def setSpeedStop(self):
        self.__setDataChanged()
        self.setSpeed(0,0)
        pass


    def getMotorSpeed(self):
        '''
        mapped speed values to Pololu-Values (-3200...+3200)
        '''
        sl = self.speed['LEFT']['VALUE']
        sr = self.speed['RIGHT']['VALUE']
        #sl = self.map(sl, )
        speed = (self.map(sl, self.controller_speedmap[0], self.controller_speedmap[1],self.motor_speedmap[0], self.motor_speedmap[1]),self.map (sr, self.controller_speedmap[0], self.controller_speedmap[1],self.motor_speedmap[0], self.motor_speedmap[1]))   
        return speed
        
        
    def setMotorDefaults(self, revLeft, revRight):
        self.__setDataChanged()
        self.speed['LEFT']['DATA']=1
        if revLeft:
            self.speed['REVERSE_LEFT']['VALUE']="R"
        else:
            self.speed['REVERSE_LEFT']['VALUE']=""
            
        self.speed['REVERSE_LEFT']['DATA']= revLeft   

        self.speed['RIGHT']['DATA']=2
        if revRight:
            self.speed['REVERSE_RIGHT']['VALUE']="R"
        else:
            self.speed['REVERSE_RIGHT']['VALUE']=""
        self.speed['REVERSE_RIGHT']['DATA']= revRight         
        pass
    
    def setEnergy(self, volt, ampere, capacity):
        self.__setDataChanged()
        self.speed['VOLT']['VALUE']=volt
        self.speed['AMPERE']['VALUE']=ampere
        self.speed['CAPACITY']['VALUE']=str(capacity)+"%"
        pass
    
    def setMixer1(self, onoff):
        self.__setDataChanged()
        if onoff == True:
            self.speed['MIXER1']['VALUE'] ="MIXER1"
        else:           
            self.speed['MIXER1']['VALUE'] =""
        
        self.speed['MIXER1']['DATA'] = onoff
        pass  
        
    def setMixer2(self, onoff):
        self.__setDataChanged()
        if onoff == True:
            self.speed['MIXER2']['VALUE'] ="MIXER2"
        else:           
            self.speed['MIXER2']['VALUE'] =""
        
        self.speed['MIXER2']['DATA'] = onoff
        pass  

    def setMixerOff(self, id=0):
        self.__setDataChanged()
        if id == 1:
            self.setMixer1(False)
        elif id == 2:
            self.setMixer2(False)
        else:
            self.setMixer1(False)
            self.setMixer2(False)
        pass

    def setMixerOn(self, id=1):
        '''
        set mixer on (default mixer1)
        if unsed id, all mixers are off
        '''
        self.__setDataChanged()
        if id == 1:
            self.setMixer1(True)
            self.setMixer2(False)
            
        elif id == 2:
            self.setMixer2(True)
            self.setMixer1(False)
        else:
            self.setMixer1(False)
            self.setMixer2(False)
        pass

    def isMixer1(self):
        return self.speed['MIXER1']['DATA']

    def isMixer2(self):
        return self.speed['MIXER2']['DATA']


    def setSpeedFactor(self, factor):
        self.__setDataChanged()
        self.speed['SPEED_FACTOR']['VALUE']=factor
        pass
    
    def getSpeedFactor(self):
        return self.speed['SPEED_FACTOR']['VALUE']
        
    def getDataDict(self):
        return self.speed

    def setEStop(self):
        '''
        Emergency stop - stop all motors 
        '''
        self.__setDataChanged()
        self.speed['ESTOP']['VALUE']=True
        self.setSpeedStop()
        return True
        
    def resetEStop(self):
        self.__setDataChanged()
        self.speed['ESTOP']['VALUE']=False
        return False
        
        
        