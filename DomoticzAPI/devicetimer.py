#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .api import API
from .server import Server
from .device import Device
from datetime import datetime
from enum import IntFlag
from .utilities import (bool_2_int, int_2_bool, bool_2_str, str_2_bool)
from abc import ABC
from .basetimer import BaseTimer, TimerDays

class DeviceTimer(BaseTimer):

    _param_add_device_timer = "addtimer"
    _param_update_device_timer = "updatetimer"
    _param_delete_device_timer = "deletetimer"
    _param_clear_device_timers = "clearstimers"
    _param_timers = "timers"

    _args_length = 3
    
    def __init__(self, device, *args, **kwargs):
        """ DeviceTimer class
            Args:
                device (Device): Domoticz device object where to maintain the timer
                    idx (:obj:`int`): ID of an existing timer
                or
                    active (:obj:`bool`):  true/false
                    timertype (:obj:`int`): Type of the timer
                        TME_TYPE_BEFORE_SUNRISE = 0
                        TME_TYPE_AFTER_SUNRISE = 1
                        TME_TYPE_ON_TIME = 2
                        TME_TYPE_BEFORE_SUNSET = 3
                        TME_TYPE_AFTER_SUNSET = 4
                        TME_TYPE_FIXED_DATETIME = 5
                    hour (:obj:`int`): Hour
                    min (:obj:`int`): Minute
                    date (:obj:`str`):  Date for TME_TYPE_FIXED_DATETIME type. Format is "YYYY-MM-DD" ("2020-12-25")
                    days (:obj:`int`): Days combination for timer
                        EveryDay = 0
                        Monday = 1
                        Thuesday = 2
                        Wednesday = 4
                        Thursday = 8
                        Friday = 16
                        Saturday = 32
                        Sunday = 64
                    temerature (:obj:`float`): Value for timer
                    
        """
        
        super().__init__(device, *args, **kwargs)
    
    def _initargs(self, args):
        self._command = int(args[6])
        self._level = int(args[7])
        self._color = args[8]
        self._randomness = bool(args[9])
        self._occurence = int(args[10])
    
    def _comparefields(self, var):
        return self._command == int(var.get("Command")) \
            and self._level == int(var.get("Level")) \
            and self._color == var.get("Color") \
            and self._randomness == str_2_bool(var.get("Randomness"))
            
            
    def _initfields(self, var):
        self._command = int(var.get("Command")) 
        self._level = int(var.get("Level")) 
        self._color = var.get("Color") 
        self._randomness = str_2_bool(var.get("Randomness")) 
           
    def _addquerystring(self):
        return "&command={}&level={}&color={}&randomness={}&".format(self._tvalue)
        
    def _addstr(self):
        return ", Temperature: {}".format(self._tvalue)
        
    # ..........................................................................
    # Properties
    # ..........................................................................
    
    @property
    def temperature(self):
        """float: Timer temerature."""
        return self._tvalue

    @temperature.setter
    def temperature(self, value):
        self._tvalue = float(value)
        self._update()
    
