#!/usr/bin/env python
""" evdev.py

This is a Python interface to the Linux input system's event device.
Events can be read from an open event file and decoded into spiffy
python objects. The Event objects can optionally be fed into a Device
object that represents the complete state of the device being monitored.

Copyright (C) 2003-2004 Micah Dowty <micah@navi.cx>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import struct, sys, os, time
from fcntl import ioctl
import Event

__all__ = ["Event", "Device"]

class BaseDevice(object):
    """Base class representing the state of an input device, with axes and buttons.
       Event instances can be fed into the Device to update its state.
       """
    def __init__(self):
        self.axes = {}
        self.buttons = {}
        self.name = None

    def __repr__(self):
        return "<Device name=%r axes=%r buttons=%r>" % (
            self.name, self.axes, self.buttons)

    def update(self, event):
        f = getattr(self, "update_%s" % event.type, None)
        if f:
            f(event)

    def update_EV_KEY(self, event):
        self.buttons[event.code] = event.value

    def update_EV_ABS(self, event):
        self.axes[event.code] = event.value

    def update_EV_REL(self, event):
        self.axes[event.code] = self.axes.get(event.code, 0) + event.value

    def __getitem__(self, name):
        """Retrieve the current value of an axis or button,
           or zero if no data has been received for it yet.
           """
        if name in self.axes:
            return self.axes[name]
        else:
            return self.buttons.get(name, 0)


# evdev ioctl constants. The horrible mess here
# is to silence silly FutureWarnings
EVIOCGNAME_512 = ~int(~0x82004506L & 0xFFFFFFFFL)
EVIOCGID       = ~int(~0x80084502L & 0xFFFFFFFFL)
EVIOCGBIT_512  = ~int(~0x81fe4520L & 0xFFFFFFFFL)
EVIOCGABS_512  = ~int(~0x80144540L & 0xFFFFFFFFL)


class Device(BaseDevice):
    """An abstract input device attached to a Linux evdev device node"""
    
    def __init__(self, device):
        BaseDevice.__init__(self)
        print "Device: %s" % device
	try:
        	self.fd = os.open(device, os.O_RDWR | os.O_NONBLOCK)
        	self.packetSize = struct.calcsize(Event.Event.format)
        	self.readMetadata()
	except OSError, e:
		print ">>>> %s" % str(e)


    def poll(self):
        """Receive and process all available input events"""
	print "Device.poll()"
        while 1:
            try:
                buffer = os.read(self.fd, self.packetSize)
            except OSError,e:
		print "e %s" % str(e)
                return
            #self.update(Event(unpack=buffer))
            BaseDevice.update(Event(unpack=buffer))

    def readMetadata(self):
        """Read device identity and capabilities via ioctl()"""
        buffer = "\0"*512

        # Read the name
        self.name = ioctl(self.fd, EVIOCGNAME_512, buffer)
        self.name = self.name[:self.name.find("\0")]

        # Read info on each absolute axis
        absmap = Event.Event.codeMaps['EV_ABS']
        buffer = "\0" * struct.calcsize("iiiii")
        self.absAxisInfo = {}
        for name, number in absmap.nameMap.iteritems():
            values = struct.unpack("iiiii", ioctl(self.fd, EVIOCGABS_512 + number, buffer))
            values = dict(zip(( 'value', 'min', 'max', 'fuzz', 'flat' ),values))
            self.absAxisInfo[name] = values

    def update_EV_ABS(self, event):
        """Scale the absolute axis into the range [-1, 1] using absAxisInfo"""
        try:
            info = self.absAxisInfo[event.code]
        except KeyError:
            return
        range = float(info['max'] - info['min'])
        self.axes[event.code] = (event.value - info['min']) / range * 2.0 - 1.0

class SonyF710(Device):
    '''
        specialized class to handle a Sony Gamepad F710
        
    '''
    JOY_X = "ABS_X"
    JOY_Y = "ABS_Y"
    JOY_Z = "ABS_Z"
    JOY_RZ = "ABS_RZ"
    
    BTN_X="BTN_A"
    BTN_Y="BTN_X"
    BNT_A="BTN_B"
    BTN_B="BTN_C"
    
    BTN_LT="BTN_TL"
    BTN_RT="BTN_TR"
    BTN_LB="BTN_Y"
    BTN_RB="BTN_Z"
    
    def __init__(self, event):
        Device.__init__(self, event)
        #super(Device,self).__init__()
        self.axes={}
        self.buttons={}
     
    def poll(self):
	print "SonyF710.poll()"
        #super(Device,self).poll()
	#Device.poll()
        Device.poll(self)    
                     
    def __repr__(self):
        return "<Sony F710 axes=%r buttons=%r>" % (
            self.axes, self.buttons)


        
    def isButton(self, button):
        if self.buttons[button] == 1:
            return True
        
        return False
    
    def getJoystickValue(self, joystick, map):
        value = self.axes[joystick]
        if map.count() == 4:
            value = self.map(value, map[0], map[1], map[2], map[3])
        return value
    
    
    def map(self, value, in_min, in_max, out_min, out_max):
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
           
