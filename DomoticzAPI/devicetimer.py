#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .api import API
from .server import Server
from .device import Device
from datetime import datetime
from enum import IntFlag
from .utilities import (bool_2_int, int_2_bool, bool_2_str, str_2_bool)

class TimerDays (IntFlag):
    EveryDay = 0
    Monday = 1
    Thuesday = 2
    Wednesday = 4
    Thursday = 8
    Friday = 16
    Saturday = 32
    Sunday = 64
    
class DeviceTimer:

    TME_TYPE_BEFORE_SUNRISE = 0
    TME_TYPE_AFTER_SUNRISE = 1
    TME_TYPE_ON_TIME = 2
    TME_TYPE_BEFORE_SUNSET = 3
    TME_TYPE_AFTER_SUNSET = 4
    TME_TYPE_FIXED_DATETIME = 5
    TME_TYPES = [
        TME_TYPE_BEFORE_SUNRISE,
        TME_TYPE_AFTER_SUNRISE,
        TME_TYPE_ON_TIME,
        TME_TYPE_BEFORE_SUNSET,
        TME_TYPE_AFTER_SUNSET,
        TME_TYPE_FIXED_DATETIME 
    ]

    _param_add_device_timer = "addsetpointtimer"
    _param_update_device_timer = "updatesetpointtimer"
    _param_delete_device_timer = "deletesetpointtimer"
    _param_clear_device_timers = "clearsetpointtimers"

 
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
        self._idx = None
        self._device = None
        self._active = True
        self._timertype = None
        self._hour = None
        self._min = None
        self._days = TimerDays.EveryDay
        self._tvalue = None
        self._date = None
        
        if isinstance(device, Device) and device.exists():
            self._device = device
        else:
            self._device = None
        #print(args)    
        # Existing timer: def __init__(self, device, idx)
        if len(args) == 1:
            # For existing timer
            #   tmr = dom.DeviceTimer(device, 5)
            self._idx = int(args[0])
        # New timer:      def __init__(self, device, active, type=TME_TYPE_ON_TIME, hour=0, min=0, days=128, tvalue=25, date=None):
        elif len(args) == 7:
            self._idx = None
            if int(args[1]) in self.TME_TYPES:
                self._timertype = int(args[1])
            else:
                self._timertype = None
            self._active = bool(args[0])
            self._hour = int(args[2])
            self._min = int(args[3])
            self._days = TimerDays(args[4])
            self._tvalue = float(args[5])
            self._date = DeviceTimer._checkDateFormat(args[6])
            
            if (self._timertype == self.TME_TYPE_FIXED_DATETIME \
                and self._date is None):
                raise ValueError("Date should be specified for TME_TYPE_FIXED_DATETIME.")
                
            
        else:
            idx = kwargs.get("idx")
            self._idx = int(idx) if idx is not None else None
            if self._idx is None:
                self._timertype = kwargs.get("timertype")

        self._api = self._device.hardware.api
        self._init()

    def __str__(self):
        return "{}({}, ID:{}, Active: {}, TimerType:{}, Hour:{}, Min:{},Days:{}, Value:{}, Date: {} )".format(self.__class__.__name__,
                                           str(self._device),
                                           self._idx,
                                           self._active,
                                           self._timertype,
                                           self._hour,
                                           self._min,
                                           self._days.name,
                                           self._tvalue,
                                           self._date)

    # ..........................................................................
    # Private methods
    # ..........................................................................
    def _init(self, aftercreate=False):
    
        # Get all schedules(timers) for Device: /json.htm?type=timers&idx=1
        querystring = "type=setpointtimers&idx={}".format(self._device._idx)
        self._api.querystring = querystring
        self._api.call()
        if self._api.is_OK() and self._api.has_payload():
            for var in self._api.payload:
                t = datetime.strptime(var.get("Time"),"%H:%M")
                if aftercreate:
                    #print("{} {} {}:{} {} Date:{}".format(str_2_bool(var.get("Active")), int(var.get("Type")), t.hour, t.minute, int(var.get("Days")), var.get("Date")))
                    if self._timertype == int(var.get("Type")) \
                            and self._active == str_2_bool(var.get("Active")) \
                            and self._hour == t.hour \
                            and self._min == t.minute \
                            and self._days == TimerDays(int(var.get("Days"))) \
                            and self._tvalue == float(var.get("Temperature")) \
                            and self._date == DeviceTimer._checkDateFormat(var.get("Date")):
                        if self._idx is None or self._idx < int(var.get("idx")):
                            self._idx = int(var.get("idx"))
                            self._active = str_2_bool(var.get("Active"))
                            self._timertype = int(var.get("Type"))
                            self._hour = t.hour
                            self._min = t.minute
                            self._days = TimerDays(int(var.get("Days")))
                            self._tvalue = float(var.get("Temperature"))
                            self._date == DeviceTimer._checkDateFormat(var.get("Date"))
                    
                else:
                    #print("{} {} {}:{} {} Date:{}".format(var.get("idx"), int(var.get("Type")), t.hour, t.minute, int(var.get("Days")), var.get("Date")))
                    if (self._idx is not None and int(var.get("idx")) == self._idx):
                        self._active = str_2_bool(var.get("Active"))
                        self._timertype = int(var.get("Type"))
                        self._hour = t.hour
                        self._min = t.minute
                        self._days = TimerDays(int(var.get("Days")))
                        self._tvalue = float(var.get("Temperature"))
                        self._date = DeviceTimer._checkDateFormat(var.get("Date"))
                        break
    
    
    @staticmethod 
    def _checkDateFormat(str):
        return datetime.strptime(str, '%Y-%m-%d').strftime('%Y-%m-%d') if str and str != "" else None
    
    # ..........................................................................
    # Public methods
    # ..........................................................................
    def add(self):
        if self._idx is None \
                and self._device is not None:
            self._api.querystring = "type=command&param={}&idx={}&active={}&timertype={}&hour={}&min={}&randomness=false&command=0&days={}&tvalue={}&date={}".format(
                self._param_add_device_timer,
                self._device._idx,
                bool_2_str(self._active),
                self._timertype,
                self._hour,
                self._min,
                self._days.value,
                self._tvalue,
                self._date)
            #print(self._api.querystring)
            self._api.call()
            if self._api.status == self._api.OK:
                self._init(True)

    def delete(self):
        if self.exists():
            self._api.querystring = "type=command&param={}&idx={}".format(
                self._param_delete_device_timer,
                self._idx)
            self._api.call()
            if self._api.status == self._api.OK:
                self._device = None
                self._idx = None

    def exists(self):
        """ Check if device timer exists in Domoticz """
        return not (self._idx is None or self._device is None)

    def __update(self):
        
        if self.exists():
            self._api.querystring = "type=command&param={}&idx={}&active={}&timertype={}&hour={}&min={}&randomness=false&command=0&days={}&tvalue={}&date={}".format(
                self._param_update_device_timer,
                self._idx,
                bool_2_str(self._active),
                self._timertype,
                self._hour,
                self._min,
                self._days.value,
                self._tvalue,
                self._date)
            #print(self._api.querystring)
            self._api.call()
            self._init()
            
    def setdatetimer(self, date):
        valueChecked = DeviceTimer._checkDateFormat(date)
        if (valueChecked is None):
            raise ValueError("Date should be specified for TME_TYPE_FIXED_DATETIME.")
        self._date = valueChecked
        self._timertype = self.TME_TYPE_FIXED_DATETIME
        self.__update()

    # ..........................................................................
    # Properties
    # ..........................................................................
    @property
    def api(self):
        """:obj:`API`: API object."""
        return self._api

    @property
    def idx(self):
        """int: Unique id for this timer."""
        return self._idx
        
    @property
    def device(self):
        """:obj:`Device`: Domoticz device object where to maintain the timer"""
        return self._device

    @property
    def active(self):
        """bool: Is Timer active."""
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        self.__update()
            
    @property
    def timertype(self):
        """int: Timer type, eg. TME_TYPE_ON_TIME."""
        return self._timertype

    @timertype.setter
    def timertype(self, value):
        if value in self.TME_TYPES:
            if (value == self.TME_TYPE_FIXED_DATETIME \
                and self._date is None):
                raise ValueError("Date should be specified for TME_TYPE_FIXED_DATETIME. Use setdatetimer(date) method.")
            self._timertype = value
            self.__update()
    
    @property
    def hour(self):
        """int: Timer hour."""
        return self._hour

    @hour.setter
    def hour(self, value):
        if value >= 0 and value <= 24:
            self._hour = value
            self.__update()
            
    @property
    def minute(self):
        """int: Timer minute."""
        return self._min

    @minute.setter
    def minute(self, value):
        if value >= 0 and value <= 60:
            self._min = value
            self.__update()
            
    @property
    def date(self):
        """int: Timer date."""
        return self._date

    @date.setter
    def date(self, value):
        valueChecked = DeviceTimer._checkDateFormat(value)
        if (self._timertype == self.TME_TYPE_FIXED_DATETIME \
            and valueChecked is None):
            raise ValueError("Date should be specified for TME_TYPE_FIXED_DATETIME.")
        elif (self._timertype != self.TME_TYPE_FIXED_DATETIME):
            raise ValueError("Not able to update date for non-TME_TYPE_FIXED_DATETIME timer type. Use setdatetimer(date) method.")
        self._date = valueChecked
        self.__update()
    
    @property
    def temperature(self):
        """float: Timer temerature."""
        return self._min

    @temperature.setter
    def temperature(self, value):
        self._tvalue = float(value)
        self.__update()
    
