#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .api import API
from .server import Server
from .device import Device

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

    _type_add_device_timer = "addtimer"
 
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
        # New timer:      def __init__(self, server, device, type=TME_TYPE_ON_TIME):
        elif len(args) == 2:
            self._idx = None
            self._timertype = args[0]
            if int(args[0]) in self.TME_TYPES:
                self._timertype = int(args[0])
            else:
                self._timertype = None
        else:
            self._idx = kwargs.get("idx")
            if self._idx is None:
                self._hardware = kwargs.get("device")
                self._timertype = kwargs.get("type")

        self._api = self._server.api
        self._init()

    def __str__(self):
        return "{}({}, {}, {})".format(self.__class__.__name__,
                                           str(self._server),
                                           self._idx,
                                           self._timertype)

    # ..........................................................................
    # Private methods
    # ..........................................................................
    def _init(self):
        if self._idx is not None:
            # Get all schedules(timers) for Devices: /json.htm?type=schedules&filter=device
            querystring = "type=schedules&filter=device"
        else:
            querystring = ""
        self._api.querystring = querystring
        self._api.call()
        if self._api.is_OK() and self._api.has_payload():
            for var in self._api.payload:
                if (self._idx is not None and int(var.get("TimerID")) == self._idx):
                    self._idx = int(var.get("TimerID"))
                    self._timertype = int(var.get("TimerType"))
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
                and self._device is not None \
                and self._type is not None :
            # /json.htm?type=command&param=addtimer&idx=DeviceRowID&active=true&timertype=2&hour=0&min=20&randomness=false&command=0&days=1234567
            self._api.querystring = "type={}&idx={}&active=true&timertype={}&hour=0&min=20&randomness=false&command=0&days=1234567".format(
                self._type_add_device_timer,
                self._device._idx,
                self._timertype)
            self._api.call()
            if self._api.status == self._api.OK:
                self._idx = int(self._api.data.get("idx"))
                self._init()

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


