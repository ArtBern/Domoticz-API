#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .api import API
from .server import Server
from .device import Device

class DeviceTimer:

    _type_add_device_timer = "addtimer"
 
    def __init__(self, server, *args, **kwargs):
        """ DeviceTimer class

            Args:
                server (Server): Domoticz server object where to maintain the device            
                    idx (:obj:`int`, optional): ID of an existing device
                or
                    device (:obj:`obj`, optional): Device to add device timer
                        type (:obj:`int`, optional): Device type
        """
        self._idx = None
        self._device = None
        self._type = None
        if isinstance(server, Server) and server.exists():
            self._server = server
        else:
            self._server = None
        # Existing device: def __init__(self, server, idx)
        if len(args) == 1:
            # For existing device
            #   dev = dom.Device(server, 180)
            self._idx = int(args[0])
        # New device:      def __init__(self, server, device, type=None):
        elif len(args) == 2:
            self._idx = None
            if isinstance(args[0], Device):
                if args[0].exists():
                    self._device = args[0]
            else:
                self._device = None
            self._type = args[1]
        else:
            self._idx = kwargs.get("idx")
            if self._idx is None:
                self._hardware = kwargs.get("device")
                self._type = kwargs.get("type")

        self._api = self._server.api
        self._init()

    def __str__(self):
        return "{}({}, {})".format(self.__class__.__name__,
                                           str(self._server),
                                           self._idx)

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
                if (self._idx is not None and int(var.get("idx")) == self._idx):
                    self._idx = int(var.get("idx"))
                    self._type = int(var.get("Type"))
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
                self._type)
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
        return not (self._idx is None or self._hardware is None)

    def has_battery(self):
        """ Check if this device is using a battery """
        return not (self._batterylevel is None or self._batterylevel == NUM_MAX)

    def is_blind(self):
        return self._typeimg == "blinds"

    def is_dimmer(self):
        return ((self.is_switch() and self._switchtype == "Dimmer") or (self._isdimmer == True))

    def is_favorite(self):
        return int_2_bool(self._favorite)

    def is_hygrometer(self):
        return self._humidity is not None

    def is_motion(self):
        return self._typeimg == "motion"

    def is_switch(self):
        return self._switchtype is not None

    def is_thermometer(self):
        return self._temp is not None

    def reset_security_status(self, value):
        """ Reset security status for eg. Smoke detectors """
        if self.exists():
            if self.is_switch():
                if value in self.switch_reset_security_statuses:
                    # /json.htm?type=command&param=resetsecuritystatus&idx=IDX&switchcmd=VALUE
                    self._api.querystring = "type=command&param={}&idx={}&switchcmd={}".format(
                        self._param_reset_security_status,
                        self._idx,
                        value
                    )
                    self._api.call()
                    self._init()

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

    def update_switch(self, value, level=0):
        if self.exists():
            if self.is_switch():
                if value in self.SWITCH_LIGHT_VALUES:
                    # /json.htm?type=command&param=switchlight&idx=IDX&switchcmd=On
                    # /json.htm?type=command&param=switchlight&idx=IDX&switchcmd=Off
                    # /json.htm?type=command&param=switchlight&idx=IDX&switchcmd=Toggle
                    self._api.querystring = "type=command&param={}&idx={}&switchcmd={}".format(
                        self._param_switch_light,
                        self._idx,
                        value
                    )
                    self._api.call()
                    self._init()

    @property
    def value(self, key):
        """Retrieve the value from a device property 
        Can be used if the property is not available/unknown

        Args:
            key (str): key from a property, eg. "Level", etc
        """
        found_dict = {}
        if self.exists():
            # Retrieve status of specific device: /json.htm?type=devices&rid=IDX&displayhidden=1
            self._api.querystring = "type={}&rid={}&displayhidden=1".format(
                self._type_devices,
                self._idx)
            self._api.call()
            if self._api.status == self._api.OK:
                if self._api.payload:
                    for result_dict in self._api.payload:
                        if int(result_dict.get("idx")) == self._idx:
                            # Found device :)
                            found_dict = result_dict
                            break
        return found_dict.get(key)

    @value.setter
    def value(self, key, value):
        if key in self._type_set_used_keys:
            # /json.htm?type=setused&idx=IDX&used=true|false
            self._api.querystring = "type={}&idx={}&used={}&{}={}".format(
                self._type_set_used,
                self._idx,
                self._used,
                key,
                value
            )
            self._api.call()
            self._init()
        elif key in self._param_update_device_keys:
            # self.update(self._nvalue, self._svalue, self._batterylevel, self._rssi)
            pass

    # ..........................................................................
    # Properties
    # ..........................................................................

    @property
    def addjmulti(self):
        return self._addjmulti

    @property
    def addjmulti2(self):
        return self._addjmulti2

    @property
    def addjvalue(self):
        return self._addjvalue

    @property
    def addjvalue2(self):
        return self._addjvalue2

    @property
    def barometer(self):
        return self._barometer

    @property
    def batterylevel(self):
        return self._batterylevel

    @batterylevel.setter
    def batterylevel(self, value):
        self._batterylevel = value

    @property
    def cameraidx(self):
        return self._cameraidx

    @property
    def chill(self):
        return self._chill

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if isinstance(value, Color) and self.exists():
            if self.is_switch():
                # /json.htm?type=command&param=setcolbrightnessvalue&idx=IDX&color=COLOR&brightness=LEVEL
                self._api.querystring = "type=command&param={}&idx={}&color={}&brightness={}".format(
                    self._param_set_color_brightness,
                    self._idx,
                    value.color,
                    self._level
                )
                self._api.call()
                self._init()

    @property
    def counter(self):
        return self._counter

    @property
    def counterdeliv(self):
        return self._counterdeliv

    @property
    def counterdelivtoday(self):
        return self._counterdelivtoday

    @property
    def countertoday(self):
        return self._countertoday

    @property
    def current(self):
        return self._current

    @property
    def customimage(self):
        return self._customimage

    @property
    def data(self):
        return self._data

    @property
    def daytime(self):
        return self._daytime

    @property
    def description(self):
        return self._description

    @property
    def desc(self):
        return self._desc

    @property
    def dewpoint(self):
        return self._dewpoint

    @property
    def dimmertype(self):
        return self._dimmertype

    @property
    def direction(self):
        return self._direction

    @property
    def directionstr(self):
        return self._directionstr

    @property
    def displaytype(self):
        return self._displaytype

    @property
    # For some reason this attribute in Domoticz is an 'int'. Boolean is more logical.
    def favorite(self):
        return int_2_bool(self._favorite)

    @favorite.setter
    def favorite(self, value):
        # /json.htm?type=command&param=makefavorite&idx=IDX&isfavorite=FAVORITE
        if isinstance(value, bool) and self.exists():
            int_value = bool_2_int(value)
            self._api.querystring = "type=command&param={}&idx={}&isfavorite={}".format(
                self._param_make_favorite,
                self._idx,
                str(int_value)
            )
            self._api.call()
            if self._api.status == self._api.OK:
                self._favorite = int_value

    @property
    def forecast(self):
        return self._forecast

    @property
    def forecaststr(self):
        return self._forecaststr

    @property
    def gust(self):
        return self._gust

    @property
    def hardware(self):
        return self._hardware

    @property
    def havedimmer(self):
        return self._havedimmer

    @property
    def havegroupcmd(self):
        return self._havegroupcmd

    @property
    def havetimeout(self):
        return self._havetimeout

    @property
    def hidden(self):
        return self._name[:1] == "$"

    @hidden.setter
    def hidden(self, value):
        if value and self._name[:1] != "$":
            self.name = "${}".format(self._name)
        elif not value and self._name[:1] == "$":
            self.name = self._name[1:]
        else:
            pass

    @property
    def humidity(self):
        return self._humidity

    @property
    def humiditystatus(self):
        return self._humiditystatus

    @property
    def id(self):
        return self._id

    @property
    def idx(self):
        return self._idx

    @property
    def image(self):
        return self._image

    @property
    def internalstate(self):
        return self._internalstate

    @property
    def issubdevice(self):
        return self._issubdevice

    @property
    def lastupdate(self):
        return self._lastupdate

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        if self.is_switch():
            # /json.htm?type=command&param=switchlight&idx=IDX&switchcmd=Set%20Level&level=LEVEL
            self._api.querystring = "type=command&param={}&idx={}&switchcmd={}&level={}".format(
                self._param_switch_light,
                self._idx,
                self.SWITCH_SET_LEVEL,
                value
            )
            self._api.call()
            self._init()

    @property
    def levelactions(self):
        return self._levelactions

    @property
    def levelint(self):
        return self._levelint

    @property
    def levelnames(self):
        return self._levelnames

    @property
    def leveloffhidden(self):
        return self._leveloffhidden

    @property
    def maxdimlevel(self):
        return self._maxdimlevel

    @property
    def mode(self):
        return self._mode

    @property
    def modes(self):
        return self._modes

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if self.exists():
            # /json.htm?type=command&param=renamedevice&idx=idx&name=
            self._api.querystring = "type=command&param={}&idx={}&name={}".format(
                self._param_rename_device,
                self._idx,
                value
            )
            self._api.call()
            if self._api.status == self._api.OK:
                self._name = value

    @property
    def notifications(self):
        return self._notifications

    @property
    def nvalue(self):
        self._values()
        return self._nvalue

    @property
    def options(self):
        return self._options

    @property
    def planid(self):
        return int(self._planid) if self._planid is not None else None

    @property
    def planids(self):
        return self._planids

    @property
    def pressure(self):
        return self._pressure

    @property
    def protected(self):
        return self._protected

    @property
    def quality(self):
        return self._quality

    @property
    def radiation(self):
        return self._radiation

    @property
    def rain(self):
        return self._rain

    @property
    def rainrate(self):
        return self._rainrate

    @property
    def selectorstyle(self):
        return self._selectorstyle

    @property
    def sensortype(self):
        return self._sensortype

    @property
    def sensorunit(self):
        return self._sensorunit

    @property
    def server(self):
        return self._server

    @property
    def setpoint(self):
        return self._setpoint

    @property
    def shownotifications(self):
        return self._shownotifications

    @property
    def signallevel(self):
        return self._signallevel

    @signallevel.setter
    def signallevel(self, value):
        self._signallevel = value

    @property
    def speed(self):
        return self._speed

    @property
    def state(self):
        self._values()
        return self._state

    @property
    def subtype(self):
        return self._subtype

    @property
    def svalue(self):
        self._values()
        return self._svalue

    @property
    def temp(self):
        return self._temp

    @property
    def timers(self):
        return self._timers

    @property
    def type(self):
        return self._type

    @property
    def typeimg(self):
        return self._typeimg

    @property
    def unit(self):
        return self._unit

    @property
    def until(self):
        return self._until

    @property
    def usage(self):
        return self._usage

    @property
    def usagedeliv(self):
        return self._usagedeliv

    @property
    # For some reason this attribute in Domoticz is an 'int'. Boolean is more logical.
    def used(self):
        return int_2_bool(self._used)

    @used.setter
    def used(self, value):
        # The url needs "true" or "false"!!!
        if isinstance(value, bool) and self.exists():
            # /json.htm?type=setused&idx=IDX&used=true|false
            self._api.querystring = "type={}&idx={}&used={}".format(
                self._type_set_used,
                self._idx,
                bool_2_str(value)
            )
            self._api.call()
            if self._api.status == self._api.OK:
                self._used = bool_2_int(value)

    @property
    def uvi(self):
        return self._uvi

    @property
    def valuequantity(self):
        return self._valuequantity

    @property
    def valueunits(self):
        return self._valueunits

    @property
    def visibilty(self):
        return self._visibility

    @property
    def voltage(self):
        return self._voltage

    @property
    def xoffset(self):
        return self._xoffset

    @property
    def yoffset(self):
        return self._yoffset
