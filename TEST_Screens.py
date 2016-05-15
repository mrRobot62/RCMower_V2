# -*- coding: utf-8 -*-
import pygame, sys, os
from pygame.locals import *
from ast import literal_eval
from _ast import TryExcept
from pygame.surface import Surface

from RCMower_Screens import *

def main():
    
    pygame.init()
    disp = pygame.display.set_mode(480,320)

    RED=(255,0,0)
    GREEN=(0,255,0)
    BLUE=(0,0,255)
    WHITE(255,255,255)
    BLACK(0,0,0)    
    
    
    
    motor_scr = Screen_MOTOR(surface, 'RCMower_Screens.yml')
    pass


if __name__ == '__main__':
    main()
    os._exit()
    