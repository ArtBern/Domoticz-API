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

    _param_add_device_timer = "addsetpointtimer"
    _param_update_device_timer = "updatesetpointtimer"
    _param_delete_device_timer = "deletesetpointtimer"
    _param_clear_device_timers = "clearsetpointtimers"

    _args_length = 1
    
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
        self._tvalue = float(args[6])
    
    def _comparefields(self, var):
        return self._tvalue == float(var.get("Temperature"))
        
    def _initfields(self, var):
        self._tvalue = float(var.get("Temperature"))
    
    def _addquerystring(self):
        return "&tvalue={}".format(self._tvalue)
        
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
    
