#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .api import API
from .server import Server
from .device import Device
from .scene import Scene
from datetime import datetime
from enum import IntFlag, IntEnum
from .utilities import (bool_2_int, int_2_bool, bool_2_str, str_2_bool)
from abc import ABC, abstractmethod

class TimerDays (IntFlag):
    EveryDay = 0
    Monday = 1
    Thuesday = 2
    Wednesday = 4
    Thursday = 8
    Friday = 16
    Saturday = 32
    Sunday = 64
    
class TimerTypes (IntEnum):
    TME_TYPE_BEFORE_SUNRISE = 0
    TME_TYPE_AFTER_SUNRISE = 1
    TME_TYPE_ON_TIME = 2
    TME_TYPE_BEFORE_SUNSET = 3
    TME_TYPE_AFTER_SUNSET = 4
    TME_TYPE_FIXED_DATETIME = 5
    TME_TYPE_DAYSODD = 6
    TME_TYPE_DAYSEVEN = 7
    TME_TYPE_WEEKSODD = 8
    TME_TYPE_WEEKSEVEN = 9
    TME_TYPE_MONTHLY = 10
    TME_TYPE_MONTHLY_WD = 11
    TME_TYPE_YEARLY = 12
    TME_TYPE_YEARLY_WD = 13
    TME_TYPE_BEFORESUNATSOUTH = 14
    TME_TYPE_AFTERSUNATSOUTH = 15
    TME_TYPE_BEFORECIVTWSTART = 16
    TME_TYPE_AFTERCIVTWSTART = 17
    TME_TYPE_BEFORECIVTWEND = 18
    TME_TYPE_AFTERCIVTWEND = 19
    TME_TYPE_BEFORENAUTTWSTART = 20
    TME_TYPE_AFTERNAUTTWSTART = 21
    TME_TYPE_BEFORENAUTTWEND = 22
    TME_TYPE_AFTERNAUTTWEND = 23
    TME_TYPE_BEFOREASTTWSTART = 24
    TME_TYPE_AFTERASTTWSTART = 25
    TME_TYPE_BEFOREASTTWEND = 26
    TME_TYPE_AFTERASTTWEND = 27
    TME_TYPE_END = 28
    
    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_ 
        
    
class BaseTimer(ABC):

    _args_length = 0

    @abstractmethod
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
        self._date = None
        self._occurence = 0
        self._mday = 0
        self._month = 0
        
        if (isinstance(device, Device) or isinstance(device, Scene)) and device.exists():
            self._device = device
        else:
            self._device = None

        # Existing timer: def __init__(self, device, idx)
        if len(args) == 1:
            # For existing timer
            #   tmr = dom.DeviceTimer(device, 5)
            self._idx = int(args[0])
        # New timer:      def __init__(self, device, active, type=TME_TYPE_ON_TIME, hour=0, min=0, days=128, tvalue=25, date=None):
        elif len(args) == 9 + self._args_length:
            self._idx = None
            self._timertype = TimerTypes(args[1])
            self._active = bool(args[0])
            self._hour = int(args[2])
            self._min = int(args[3])
            self._days = TimerDays(args[4])
            self._date = BaseTimer._checkDateFormat(args[5])
            self._occurence = int(args[6])
            self._mday = int(args[7])
            self._month = int(args[8])
                        
            self._initargs(args[9:])
            
            self.__checkTypeAndValues(self._timertype, self._date, self._occurence, self._mday, self._month)
                            
        else:
            idx = kwargs.get("idx")
            #print(kwargs)
            self._idx = int(idx) if idx is not None else None
            if self._idx is not None:
 
                if kwargs.get("is_from_factory"): 
                    self._fillfrompayload(kwargs)
                    return
             
            else:
                self._fillfromkwargs(kwargs)

        self._api = self._device._api
        self._init()
        
    def __checkTypeAndValues(self, timertype, date, occurence, mday, month):
        if (timertype == TimerTypes.TME_TYPE_FIXED_DATETIME):
            if (date is None):
                raise ValueError("Date should be specified for TME_TYPE_FIXED_DATETIME.")
            else:
                self._occurence = 0
                self._mday = 0
                self._month = 0
        elif (timertype == TimerTypes.TME_TYPE_MONTHLY):
            if (mday == 0):
                raise ValueError("Month day should be specified for TME_TYPE_MONTHLY.")
            else:
                self._date = None
                self._occurence = 0
                self._mday = 0
        elif (timertype == TimerTypes.TME_TYPE_MONTHLY_WD):
            if (occurence == 0):
                raise ValueError("Occurence should be specified for TME_TYPE_MONTHLY_WD.")
            else:
                self._date = None
                self._mday = 0
                self._month = 0
        elif (timertype ==  TimerTypes.TME_TYPE_YEARLY):
            if (mday == 0 or month ==0):
                raise ValueError("Day and Month should be specified for TME_TYPE_YEARLY.")
            else:
                self._date = None
                self._occurence = 0
        elif (timertype ==  TimerTypes.TME_TYPE_YEARLY_WD):
            if (occurence == 0 or month ==0):
                raise ValueError("Occurence and Month should be specified for TME_TYPE_YEARLY_WD")
            else:
                self._mday = 0
                self._date = None
        else:
            self._date = None
            self._occurence = 0
            self._mday = 0
            self._month = 0
    
    @abstractmethod
    def _initargs(self, args):
        pass
        
    @abstractmethod
    def _comparefields(self, var):
        pass
        
    @abstractmethod
    def _initfields(self, var):
        pass
        
    @abstractmethod
    def _addquerystring(self):
        pass  
        
    @abstractmethod
    def _addstr(self):
        pass
    
    def __str__(self):
        return "{}({}, ID:{}, Active: {}, TimerType:{}, Hour:{}, Min:{}, Days:{}, Date:{}, Occurence:{}, MDay:{}, Month:{} {})".format(self.__class__.__name__,
                                           str(self._device),
                                           self._idx,
                                           self._active,
                                           repr(self._timertype),
                                           self._hour,
                                           self._min,
                                           repr(self._days),
                                           self._date,
                                           self._occurence,
                                           self._mday,
                                           self._month,
                                           self._addstr())
    # ..........................................................................
    # Private methods
    # ..........................................................................
    def _fillfrompayload(self, var):
        t = datetime.strptime(var.get("Time"),"%H:%M")
        self._idx = int(var.get("idx"))
        self._active = str_2_bool(var.get("Active"))
        self._timertype = TimerTypes(int(var.get("Type")))
        self._hour = t.hour
        self._min = t.minute
        self._days = TimerDays(int(var.get("Days")))
        self._date = BaseTimer._checkDateFormat(var.get("Date"))
        self._occurence = int(var.get("Occurence")) 
        self._mday = int(var.get("MDay")) 
        self._month = int(var.get("Month"))
        
        self._initfields(var)

    def _fillfromkwargs(self, var):
        t = datetime.strptime(var.get("Time", "00:00"),"%H:%M")
        self._active = str_2_bool(var.get("Active", False))
        self._timertype = TimerTypes(int(var.get("Type", TimerTypes.TME_TYPE_ON_TIME)))
        self._hour = t.hour
        self._min = t.minute
        self._days = TimerDays(int(var.get("Days", 0)))
        self._date = BaseTimer._checkDateFormat(var.get("Date", None))
        self._occurence = int(var.get("Occurence", 0)) 
        self._mday = int(var.get("MDay", 1)) 
        self._month = int(var.get("Month", 1))
        
        self._initfields(var)
   

    
    def _init(self, aftercreate=False):
    
        querystring = "type={}&idx={}".format(self._param_timers, self._device._idx)
        self._api.querystring = querystring
        self._api.call()
        if self._api.is_OK() and self._api.has_payload():
            for var in self._api.payload:
                t = datetime.strptime(var.get("Time"),"%H:%M")
                if aftercreate:
                    #print("{} {} {}:{} {} Date:{}".format(str_2_bool(var.get("Active")), int(var.get("Type")), t.hour, t.minute, int(var.get("Days")), var.get("Date")))
                    if self._timertype == TimerTypes(int(var.get("Type"))) \
                            and self._active == str_2_bool(var.get("Active")) \
                            and self._hour == t.hour \
                            and self._min == t.minute \
                            and self._days == TimerDays(int(var.get("Days"))) \
                            and self._date == BaseTimer._checkDateFormat(var.get("Date")) \
                            and self._occurence == int(var.get("Occurence")) \
                            and self._mday == int(var.get("MDay")) \
                            and self._month == int(var.get("Month")) \
                            and self._comparefields(var):
                        if self._idx is None or self._idx < int(var.get("idx")):
                            self._fillfrompayload(var)
                    
                else:
                    #print("{} {} {}:{} {} Date:{}".format(var.get("idx"), int(var.get("Type")), t.hour, t.minute, int(var.get("Days")), var.get("Date")))
                    if (self._idx is not None and int(var.get("idx")) == self._idx):
                        self._fillfrompayload(var)
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
            self._api.querystring = "type=command&param={}&idx={}&active={}&timertype={}&hour={}&min={}&randomness=false&command=0&days={}&date={}&occurence={}&mday={}&month={}{}".format(
                self._param_add_device_timer,
                self._device._idx,
                bool_2_str(self._active),
                self._timertype,
                self._hour,
                self._min,
                self._days.value,
                self._date if BaseTimer._checkDateFormat(self._date) is not None else "",
                self._occurence,
                self._mday,
                self._month,
                self._addquerystring())
            #print(self._api.querystring)
            self._api.call()
            if self._api.status == self._api.OK:
                self._init(True)
            else:
                print ("Not ok adding timer")

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
    
    def _update(self):
        
        if self.exists():
            self._api.querystring = "type=command&param={}&idx={}&active={}&timertype={}&hour={}&min={}&randomness=false&command=0&days={}&date={}&occurence={}&mday={}&month={}{}".format(
                self._param_update_device_timer,
                self._idx,
                bool_2_str(self._active),
                self._timertype,
                self._hour,
                self._min,
                self._days.value,
                self._date,
                self._occurence,
                self._mday,
                self._month,
                self._addquerystring())
            #print(self._api.querystring)
            self._api.call()
            self._init()
            
    def setfixeddatetimer(self, date):
        valueChecked = BaseTimer._checkDateFormat(date)
        self.__checkTypeAndValues(TimerTypes.TME_TYPE_FIXED_DATETIME, valueChecked, self._occurence, self._mday, self._month)
        
        self._date = valueChecked
        self._timertype = TimerTypes.TME_TYPE_FIXED_DATETIME
        self._update()
        
    def setmonthlytimer(self, mday):
        self.__checkTypeAndValues(TimerTypes.TME_TYPE_MONTHLY, self._date, self._occurence, mday, self._month)
        
        self._mday = mday
        self._timertype = TimerTypes.TME_TYPE_MONTHLY
        self._update()
        
    def setmonthlywdtimer(self, occurence):
        self.__checkTypeAndValues(TimerTypes.TME_TYPE_MONTHLY_WD, self._date, occurence, self._mday, self._month)
        
        self._occurence = occurence
        self._timertype = TimerTypes.TME_TYPE_MONTHLY_WD
        self._update()
        
    def setyearlytimer(self, mday, month):
        self.__checkTypeAndValues(TimerTypes.TME_TYPE_YEARLY, self._date, self._occurence, mday, month)
        
        self._mday = mday
        self._month = month
        self._timertype = TimerTypes.TME_TYPE_YEARLY
        self._update()
        
    def setyearlywdtimer(self, occurence, month):
        self.__checkTypeAndValues(TimerTypes.TME_TYPE_YEARLY_WD, self._date, occurence, self._mday, month)
        
        self._occurence = occurence
        self._month = month
        self._timertype = TimerTypes.TME_TYPE_YEARLY_WD
        self._update()

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
        self._update()
            
    @property
    def timertype(self):
        """int: Timer type, eg. TME_TYPE_ON_TIME."""
        return self._timertype

    @timertype.setter
    def timertype(self, value):
        if value in TimerTypes:
            self.__checkTypeAndValues(TimerTypes(int(value)), self._date, self._occurence, self._mday, self._month)   
            self._timertype = TimerTypes(int(value))
            self._update()
    
    @property
    def hour(self):
        """int: Timer hour."""
        return self._hour

    @hour.setter
    def hour(self, value):
        if value >= 0 and value <= 24:
            self._hour = value
            self._update()
            
    @property
    def minute(self):
        """int: Timer minute."""
        return self._min

    @minute.setter
    def minute(self, value):
        if value >= 0 and value <= 60:
            self._min = value
            self._update()
            
    @property
    def date(self):
        """int: Timer date."""
        return self._date

    @date.setter
    def date(self, value):
        valueChecked = BaseTimer._checkDateFormat(value)
        self.__checkTypeAndValues(self._timertype, valueChecked, self._occurence, self._mday, self._month)
        self._date = valueChecked
        self._update()

    @property
    def occurence(self):
        """int: Timer occurence."""
        return self._occurence

    @occurence.setter
    def occurence(self, value):
        self.__checkTypeAndValues(self._timertype, self._date, int(value), self._mday, self._month)
        self._occurence = int(value)
        self._update()
    
    @property
    def mday(self):
        """int: Timer mday."""
        return self._mday

    @mday.setter
    def mday(self, value):
        self.__checkTypeAndValues(self._timertype, self._date, self._occurence, int(value), self._month)
        self._mday = int(value)
        self._update()
    
    @property
    def month(self):
        """int: Timer month."""
        return self._month

    @month.setter
    def month(self, value):
        self.__checkTypeAndValues(self._timertype, self._date, self._occurence, self._mday, int(value))
        self._month = int(value)
        self._update()
    
