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
    _param_clear_device_timers = "cleartimers"
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
        self._randomness = str_2_bool(args[0])
        self._command = int_2_bool(args[1])
        self._level = int(args[2])
    
    def _comparefields(self, var):
        return self._randomness == str_2_bool(var.get("Randomness")) \
                and self._command == int_2_bool(var.get("Cmd")) \
                and self._level == int(var.get("Level"))
        
    def _initfields(self, var):
        self._randomness = str_2_bool(var.get("Randomness", "false")) 
        self._command = int_2_bool(var.get("Cmd", 0))
        self._level = int(var.get("Level", 100))
    
    def _addquerystring(self):
        return "&randomness={}&command={}&level".format(self._randomness, self._command, self._level)
        
    def _addstr(self):
        return ", Randomness: {}, Command: {}, Level: {}".format(self._randomness, self._command, self._level)
    
    @staticmethod
    def loadbydevice(device):
        result = []
        if isinstance(device, Device) and device.exists() and device.type != "Thermostat":
            api = device.hardware.api
            querystring = "type={}&idx={}".format(SetPointTimer._param_timers, device._idx)
            api.querystring = querystring
            api.call()
            if api.is_OK() and api.has_payload():
                for var in api.payload:
                    var["is_from_factory"] = True
                    timr = DeviceTimer(device, **var)
                    result.append(timr)
        return result
            
    # ..........................................................................
    # Properties
    # ..........................................................................
    
    @property
    def randomness(self):
        """bool: Timer randomness."""
        return self._randomness

    @randomness.setter
    def randomness(self, value):
        self._randomness = str_2_bool(value)
        self._update()

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, value):
        self._command = int_2_bool(value)
        self._update()
    
    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        self._level = int(value)
        self._update()



