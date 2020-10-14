#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .api import API
from .device import Device
from .utilities import (bool_2_int, int_2_bool, bool_2_str, str_2_bool)
from abc import ABC
from .basetimer import BaseTimer, TimerDays

class SetPointTimer(BaseTimer):

    _param_add_device_timer = "addsetpointtimer"
    _param_update_device_timer = "updatesetpointtimer"
    _param_delete_device_timer = "deletesetpointtimer"
    _param_clear_device_timers = "clearsetpointtimers"
    _param_timers = "setpointtimers"
    
    _args_length = 1
    
    def __init__(self, device, *args, **kwargs):
        """ SetPointTimer class
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
        self._tvalue = float(args[0])
    
    def _comparefields(self, var):
        return self._tvalue == float(var.get("Temperature"))
        
    def _initfields(self, var):
        self._tvalue = float(var.get("Temperature", 0))
    
    def _addquerystring(self):
        return "&tvalue={}".format(self._tvalue)
        
    def _addstr(self):
        return ", Temperature: {}".format(self._tvalue)
    
    @staticmethod
    def loadbythermostat(device):
        result = []
        if isinstance(device, Device) and device.exists() and device.type == "Thermostat":
            api = device.hardware.api
            querystring = "type={}&idx={}".format(SetPointTimer._param_timers, device._idx)
            api.querystring = querystring
            api.call()
            if api.is_OK() and api.has_payload():
                for var in api.payload:
                    var["is_from_factory"] = True
                    timr = SetPointTimer(device, **var)
                    result.append(timr)
        return result
            
    # ..........................................................................
    # Properties
    # ..........................................................................
    
    @property
    def temperature(self):
        """float: Timer temperature."""
        return self._tvalue

    @temperature.setter
    def temperature(self, value):
        self._tvalue = float(value)
        self._update()
    
