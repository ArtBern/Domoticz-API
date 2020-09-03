#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .api import API
from .server import Server
from .device import Device
from datetime import datetime

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

    _type_add_device_timer = "addsetpointtimer"
 
    def __init__(self, server, device, *args, **kwargs):
        """ DeviceTimer class

            Args:
                server (Server): Domoticz server object where to maintain the timer
                device (Device): Domoticz device object where to maintain the timer
                    idx (:obj:`int`, optional): ID of an existing timer
                or
                    type (:obj:`int`, optional): Device type
        """
        self._idx = None
        self._device = None
        self._timertype = None
        self._hour = None
        self._min = None
        self._days = None
        if isinstance(server, Server) and server.exists():
            self._server = server
        else:
            self._server = None
        if isinstance(device, Device) and device.exists():
            self._device = device
        else:
            self._device = None
        # Existing timer: def __init__(self, server, device, idx)
        if len(args) == 1:
            # For existing timer
            #   tmr = dom.DeviceTimer(server, device, 5)
            self._idx = int(args[0])
        # New timer:      def __init__(self, server, device, type=TME_TYPE_ON_TIME, hour=0, min=0, days=128):
        elif len(args) == 4:
            self._idx = None
            if int(args[0]) in self.TME_TYPES:
                self._timertype = int(args[0])
            else:
                self._timertype = None
            
            self._hour = int(args[1])
            self._min = int(args[2])
            self._days = int(args[3])
            
        else:
            self._idx = kwargs.get("idx")
            if self._idx is None:
                self._hardware = kwargs.get("device")
                self._timertype = kwargs.get("type")

        self._api = self._server.api
        self._init()

    def __str__(self):
        return "{}({}, {}, ID:{}, TimerType:{}, Hour:{}, Min:{},Days:{} )".format(self.__class__.__name__,
                                           str(self._server),
                                           str(self._device),
                                           self._idx,
                                           self._timertype,
                                           self._hour,
                                           self._min,
                                           self._days)

    # ..........................................................................
    # Private methods
    # ..........................................................................
    def _init(self, aftercreate=False):
    
        # Get all schedules(timers) for Device: /json.htm?type=timers&idx=1
        querystring = "type=setpointtimers&idx={}".format(self._device._idx)
        print(querystring)
        self._api.querystring = querystring
        self._api.call()
        if self._api.is_OK() and self._api.has_payload():
            for var in self._api.payload:
                print(1)
                t = datetime.strptime(var.get("Time"),"%H:%M")
                if aftercreate:
                    print("{} {}:{} {}".format(int(var.get("Type")), t.hour, t.minute, int(var.get("Days"))))
                    if self._timertype == int(var.get("Type")) \
                            and self._hour == t.hour \
                            and self._min == t.minute \
                            and self._days == int(var.get("Days")):
                        if self._idx < int(var.get("idx")):
                            self._idx = int(var.get("idx"))
                            print(self._idx)
                    
                else:
                        if (self._idx is not None and int(var.get("idx")) == self._idx):
                            self._idx = int(var.get("idx"))
                            self._timertype = int(var.get("Type"))
                            self._hour = t.hour
                            self._min = t.minute
                            self._days = int(var.get("Days"))
                            break

    def _update(self, key, value):
        if key in ("nvalue", "svalue", "battery", "rssi"):
            pass

    def _values(self):
                # The only way to get a current value from a device is by calling:
        #
        #   /type=events&param=currentstates
        #
        # Where:
        #   idx = self._idx
        #   value = nvalue (if string, then take value before '/' in values)
        #
        if self.exists():
            # /json.htm?type=events&param=currentstates
            self._api.querystring = "type={}&param={}".format(
                self._type_events,
                self._param_current_states)
            self._api.call()
            found_dict = {}
            if self._api.status == self._api.OK and self._api.payload:
                for result_dict in self._api.payload:
                    if self._idx is not None and result_dict.get("id") == self.idx:
                        # Found device :)
                        found_dict = result_dict
                        break
            self._state = found_dict.get("value")
            values = found_dict.get("values")  # like: "0/333.000;919936.000"
            try:
                self._nvalue = int(values.split("/")[0])
                self._svalue = values.split("/")[1]
            except:
                self._nvalue = None
                self._svalue = None

    # ..........................................................................
    # Public methods
    # ..........................................................................
    def add(self):
        if self._idx is None \
                and self._device is not None:
            # /json.htm?type=command&param=addtimer&idx=DeviceRowID&active=true&timertype=2&hour=0&min=20&randomness=false&command=0&days=1234567
            self._api.querystring = "type=command&param={}&idx={}&active=true&timertype={}&hour={}&min={}&randomness=false&command=0&days={}".format(
                self._type_add_device_timer,
                self._device._idx,
                self._timertype,
                self._hour,
                self._min,
                self._days)
            self._api.call()
            print (self._api.querystring)
            if self._api.status == self._api.OK:
                self._init(True)

    def delete(self):
        if self.exists():
            # /json.htm?type=deletedevice&idx=IDX
            self._api.querystring = "type={}&idx={}".format(
                self._type_delete_device,
                self._idx)
            self._api.call()
            if self._api.status == self._api.OK:
                self._hardware = None
                self._idx = None

    def exists(self):
        """ Check if device exists in Domoticz """
        return not (self._idx is None or self._device is None)


    def setused(self, used):
        if self.exists() and isinstance(used, bool):
            # /json.htm?type=setused&idx=IDX&used=true|false
            self._api.querystring = "type={}&idx={}&used={}".format(
                self._type_set_used,
                self._idx,
                bool_2_str(used)
            )
            self._api.call()
            self._init()

    def update(self, nvalue, svalue, battery, rssi):
        # /json.htm?type=command&param=udevice&idx=IDX&nvalue=NVALUE&svalue=SVALUE
        if self.exists() and (nvalue is not None or svalue is not None):
            self._api.querystring = "type=command&param={}&idx={}".format(
                self._param_update_device,
                self._idx)
            if nvalue is not None:
                self._api.querystring += "&nvalue={}".format(nvalue)
            if svalue is not None:
                self._api.querystring += "&svalue={}".format(svalue)
            # Optional parameters
            if battery is not None and isinstance(battery, int):
                self._api.querystring += "&battery={}".format(battery)
            if rssi is not None and isinstance(rssi, int):
                self._api.querystring += "&rssi={}".format(rssi)
            self._api.call()
            self._init()


