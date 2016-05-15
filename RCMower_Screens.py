import pygame, sys, os, time
import abc
import yaml
import txtlib

class RCMower_AbstractScreen(object):
    __metaclass__  = abc.ABCMeta   
    
    multipleLines = []
    mLines = None
    currentBGColor = None
    
    def __init__(self, parent, surface, screen_config_file):
        self.parent = parent
        self.SCREENSURFACE = surface
        pygame.init()
        self.screen_config_file_name = "config/RCMower_Screens.yml"
        self.screen_config_file = None
        self.text = None
        self.__loadConfig()
        self.actionRunning = False
        print ("init RCMower_AbstractScreen finished")
        pass
    
    def __loadConfig(self):
        try:
            #print ("read cfg file:'",self.screen_config_file_name,"'")
            #print ("=> ", os.getcwd())
            with open(self.screen_config_file_name, 'r') as ymlfile:
                self.screen_config_file = yaml.load(ymlfile)    
    
            self.def_font_name = self.screen_config_file['GENERAL']['FONT']
            self.def_size = self.screen_config_file['GENERAL']['SIZE']
            self.def_fgc1 = self.screen_config_file['GENERAL']['FGCOLOR1']
            self.def_bgc1 = self.screen_config_file['GENERAL']['BGCOLOR1']
            self.def_fgc2 = self.screen_config_file['GENERAL']['FGCOLOR2']
            self.def_bgc2 = self.screen_config_file['GENERAL']['BGCOLOR2']
            self.def_fgc3 = self.screen_config_file['GENERAL']['FGCOLOR3']
            self.def_bgc3 = self.screen_config_file['GENERAL']['BGCOLOR3']
            self.def_MAX_MLINES = self.screen_config_file['GENERAL']['MAX_MULTIPLE_LINES']
            self.def_font = pygame.font.SysFont(self.def_font_name, self.def_size)
            self.currentBGColor = self.def_bgc1
            
        except OSError as err: 
            print ("Error {0}".format(err))
            print ("can't load ", self.screen_config_file_name, " configuration file")
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
        pass
    def setRunning(self, state=True):
        self.actionRunning = state
    
    def getRunning(self):
        return self.actionRunning

    @abc.abstractmethod
    def refresh(self):
        raise NotImplementedError
     
    @abc.abstractmethod
    def stopScreen(self):
        raise NotImplementedError
 
    @abc.abstractmethod
    def startScreen(self):
        raise NotImplementedError
 
 

    def getBGColor(self):
        return self.currentBGColor
    
    def setBGColor(self, bgcolor):
        print("set BGColor({})".format(hex(bgcolor)))
        self.currentBGColor = bgcolor
        
    def checkButton(self, buttonName, section):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        #print("Mouse ({})".format(mouse))

        x = section['X']
        y = section['Y']
        w = section['W']
        h = section['H']
        
        if (x+w > mouse[0] > x and y+h > mouse[1] > y):
            if click[0] :
                print("Button {2} {3}=> Mouse ({0}, Pos {1})".format(click, mouse, buttonName, section))
                return True
        return False        
   
    def checkButtons(self):        
        for button in self.screen_config_file['BUTTONS']:
            action = None
            section = self.screen_config_file['BUTTONS'][button]
            try:
                action = getattr(self.parent,section['ACTION'])
            except:
                if (action != None):
                    print ("type of action ({0})".format(type(action)))
                else:
                    print ("action = None, callback {0}".format(section['ACTION']))
                raise
                
            if self.checkButton(button, section) and action != None and self.getRunning() == False:
                print ("{0}  - call action {1}".format("checkButtons", action))
                self.setRunning()
                action(self)
                break
        self.setRunning(False)    
        pass

    def _drawSingleLineText(self, key, section):
        fgc = None
        bgc = None
        value = self.data[key]["VALUE"]
        #-- get details per section
        x = section['X']
        y = section['Y']
        # -- check default values
        
        #-- is a data specific foreground or background-color used
        #print ("=> {0} ".format(self.data[key]))
        try:
            fgc = self.data[key]['FGCOLOR']
            if fgc == None:
                raise
        except:
            try:
                fgc = section["FGCOLOR"]
                if fgc == None:
                    raise
            except:
                fgc = self.def_fgc1
                #print ("set FG default")
                
        #-- background color
        try:
            bgc = self.data[key]['BGCOLOR']
            if bgc == None:
                raise
        except:
            try:
                bgc = section["BGCOLOR"]
                if bgc == None:
                    raise
            except:
                bgc = self.def_bgc1
                #print ("set BG default")

        #-- read screen field defined font font & size
        try:
            size = section['SIZE']
        except:
            size = self.def_size
            
        try:
            fnt_name = section['FONT']
            # -- screen font
            fnt = pygame.font.SysFont(fnt_name, size)
        except:
            fnt = self.def_font
           # print ("use default font")
            fnt.size(size)
        
        # -- get value to display
        # -- defined coordinates are center points
        # -- depending on text size, text will be set to exact
        # -- center position
        bgc = None
        #if fgc == None:
        #print (">> V:{0:<5} BG:{1:<7} S:{2:<5}".format(value, hex(self.getBGColor()), size))
        if key == 'RIGHT':
            pygame.draw.rect(self.SCREENSURFACE,  pygame.Color(self.getBGColor()), (680-80, 150-50, 160,100))#fnt.render('    ',True,pygame.Color(0x505050FF))
        if key == 'LEFT':
            pygame.draw.rect(self.SCREENSURFACE,  pygame.Color(self.getBGColor()), (200-80, 150-50, 160,100))#fnt.render('    ',True,pygame.Color(0x505050FF))
        
        #time.sleep(0.1)
        
        text = fnt.render(str(value), True, pygame.Color(fgc))
        textRect = text.get_rect()
        textRect.center = (x,y)

        # -- show current value at defined position with color and font
        #self.SCREENSURFACE.blit(area, areaRect)
        self.SCREENSURFACE.blit(text, textRect)

        pass
    
    def addMultipleLine(self, level, size, text):
        '''
        add a new line onto multipleLineArray
        
        the new line is inserted on postion 0
        max lines = MAX_MULTIPLE_LINES
        
        '''
        
#        level = 3
#        size = 20        

        msg = '''\n<size="{0}"><font="Courier"><b><color="{1}">{2}</color></font></size>'''

        if level <= 1:
            color="255,0,0"
            l="ERROR"
        elif level == 2:
            color="242,183,1"
            l="WARN"
        elif level >= 3:
            color="51,153,102"
            l="INFO"
        
        msg = msg.format(size,color,text)
        self.multipleLines[:0] = [msg]

        #print ("Len ({0}), MAX ({1})".format(len(self.multipleLines), self.def_MAX_MLINES))    
        if len(self.multipleLines) > self.def_MAX_MLINES:
            self.multipleLines[self.def_MAX_MLINES:]
        
        #print ("addMultipleLine ({0})".format(msg))
        #print ("Size mlines {}".format(len(self.multipleLines)))
        #print (self.multipleLines)
        self.mLines_update = True
        pass
    
    def _drawMultipleLine(self, rect):
        if len(self.multipleLines) == 0 or self.mLines_update != True:
            #print ("no multiple lines available")
            return
        html = ""
        for l in self.multipleLines:
            html += l
    
        #--- "remove" old entries
        #pygame.draw.rect(self.SCREENSURFACE,self.getBGColor(),(325,73,195,315))
    
        #self.mLines.
        #print (html)
        self.mLines.html (html)
        self.mLines.update(pygame.Color(self.getBGColor()))
        #print (html)
        self.SCREENSURFACE.blit(self.mLines.area, rect )
        self.mLines.reset()
        self.mLines_update = False
        
    def dump_cfg(self):
        print ("--- yml screen config ------------------")
        for section in self.screen_cfg:
            print(section)
        print ("---------------------------------")
            

    

class Screen_VELOCITY(RCMower_AbstractScreen):
    '''
    Screen description class
    
    This class represent a display mask(screen) with defined fields.
    A field represent data on a defined x/y postion with a foreground
    and background color and a font
    
    
    update()
    This method is used to store external screen data
    
    draw()
    This method is used to show transfered data onto the display. 
    Mostly this method is called from the main system continousely


    data parameter
    represent a data structure which must be equal (same keys) as defined
    inside the screen configuration file (yml)
    
    For Screen_VELOCITY
    { 
        "LEFT":{"VALUE":0},
        "RIGHT":{"VALUE":-200,"FGCOLOR":0xFF0000, "BGCOLOR":0x0000FF},
        "REVERSE_LEFT":{"VALUE": True},
        "REVERSE_RIGHT":{"VALUE":False},
        "RUNNING":{"VALUE":"RUN"},
        "SPEED_FACTOR":{"VALEU":0.8},
        "XBEE":{"VALUE":8.0}
    }

    '''    
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    hb_toggle = True
    
    def __init__(self, parent, surface, screen_config_file):
        super(self.__class__,self).__init__(parent, surface, screen_config_file)
        self.FPSCLOCK=pygame.time.Clock()
        self.class_name = self.__class__.__name__
        self.screen_name = self.class_name.split("_")[1]
        print ("Class {0}".format(self.screen_name))
        self.__loadScreenConfig()
        self.mLines = txtlib.Text(self.mline_area, "Courier")
        self.mLines_update = False
        #self.refresh()
        print ("init Screen_VELOCITY finished")
        pass
    
    
    def __loadScreenConfig(self):
        bgr_file = self.screen_config_file[self.screen_name]["BACKGROUND_IMAGE"]
        mlsection = self.screen_config_file[self.screen_name]["LOG"]
        self.mline_xy = (mlsection['X'], mlsection['Y'])
        self.mline_area = (mlsection['W'], mlsection['H'])
        self.mline_size = mlsection['SIZE']
        self.bgr_image = pygame.image.load(os.path.join("images", bgr_file))
        #print ("Screen ({0}), Background ({1})".format(self.screen_name, bgr_file))
        pass
           
    def heartBeat(self):
        fgc = self.screen_config_file[self.screen_name]['HEARTBEAT']['FGCOLOR']
        bgc = self.screen_config_file[self.screen_name]['HEARTBEAT']['BGCOLOR']
        pos = (self.screen_config_file[self.screen_name]['HEARTBEAT']['X'], self.screen_config_file[self.screen_name]['HEARTBEAT']['Y'])
        if (self.hb_toggle):
            pygame.draw.circle(self.SCREENSURFACE, pygame.Color(fgc),pos,6,0)
            self.hb_toggle = False
        else:
            pygame.draw.circle(self.SCREENSURFACE, pygame.Color(bgc),pos,6,0)
            self.hb_toggle = True
        pass
    
    def update(self, data):
        self.data = data
        pass
    
    def stopScreen(self):
        print ("stopScreen()")
        self.setBGColor(self.def_bgc2)
        self.refresh(self.getBGColor())
        pass
    
    def startScreen(self):
        print ("startScreen()")
        self.setBGColor(self.def_bgc1)
        self.refresh()
        pass
    
    def refresh(self, bgc=None):
        if bgc == None:
            bgc = self.def_bgc1
        self.setBGColor(bgc)
        #print ("BG-Color ({0})".format(self.def_bgc1))
        background = pygame.Surface(self.SCREENSURFACE.get_size())
        background.fill(pygame.Color(bgc))
        self.SCREENSURFACE.blit(background, pygame.rect.Rect(0,0,800,480))
        self.SCREENSURFACE.blit(self.bgr_image, pygame.rect.Rect(0,0,800,480))
        
        pygame.display.flip()
        pass

    def draw(self, data=None):
        '''
        iterate through all key from data dictionary. This dict contain
        a subset (or all) fields which can be displayed on this screen
        
        '''
        
        if (data != None):
            self.data = data
        #print ("Display-DATA ({})".format(self.data))
        #-- iterate through all keys in data dictionary
        for key in self.data:
            #print ("==> KEY ({})".format(key))
            # -- is key available inside screen definition
            if key in self.screen_config_file[self.screen_name]:
                section = self.screen_config_file[self.screen_name][key]
                #print ("Section ({0}) Content ({1})".format(key, section)) 

                #--- Draw Speed (speed, ...
                self._drawSingleLineText(key, section)

                #--- draw logging informations (multiline)
                self._drawMultipleLine(self.mline_xy)

            else:
                #print ("Data key ({0}) not found in ({1})".format(key, self.screen_config_file_name))
                #print (self.screen_config_file)
                pass

        pygame.display.flip()
        pass

