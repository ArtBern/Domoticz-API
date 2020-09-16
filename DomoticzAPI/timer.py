#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .api import API
from .server import Server
from .hardware import Hardware
from .color import Color
from .const import (NUM_MAX, NUM_MIN)
from .utilities import (bool_2_int, bool_2_str, int_2_bool)


class Device:

    _type_devices = "devices"
    _type_create_device = "createdevice"
    _type_create_dummy = "createvirtualsensor"
    _type_delete_device = "deletedevice"
    _type_set_used = "setused"
    _type_events = "events"

    _param_make_favorite = "makefavorite"
    _param_rename_device = "renamedevice"
    _param_update_device = "udevice"
    _param_switch_light = "switchlight"
    _param_set_color_brightness = "setcolbrightnessvalue"
    _param_reset_security_status = "resetsecuritystatus"
    _param_current_states = "currentstates"

    _type_set_used_keys = {
        "addjmulti",
        "addjmulti2",
        "addjvalue",
        "addjvalue2",
        "clock",
        "customimage",
        "description",
        "deviceid",
        "fmode",
        "maindeviceidx",
        "mode",
        "name",
        "protected",
        "setpoint",
        "state",
        "strparam1",
        "strparam2",
        "switchtype",
        "tmode",
        "unit",
        "until",
    }

    _param_update_device_keys = {
        "nvalue",
        "svalue",
        "battery",
        "rssi",
    }

    SWITCH_CLOSE_INLINE_RELAY = "Close inline relay"
    SWITCH_CLOSED = "Closed"
    SWITCH_LOCKED = "Locked"
    SWITCH_NORMAL = "Normal"
    SWITCH_OFF = "Off"
    SWITCH_ON = "On"
    SWITCH_OPEN = "Open"
    SWITCH_PANIC_END = "Panic End"
    SWITCH_STOP = "Stop"
    SWITCH_SET_LEVEL = "Set Level"
    SWITCH_STOP_INLINE_RELAY = "Stop inline relay"
    SWITCH_TOGGLE = "Toggle"
    SWITCH_UNLOCKED = "Unlocked"
    # Parameters used for: switchlight
    SWITCH_LIGHT_VALUES = {
        SWITCH_ON,
        SWITCH_OFF,
        SWITCH_TOGGLE,
    }
    SWITCH_SECURITY_VALUES = {
        SWITCH_NORMAL,
        SWITCH_PANIC_END,
    }

    # Parameters used for: resetsecuritystatus
    switchNormal = "Normal"
    switchPanicEnd = "Panic End"

    switch_reset_security_statuses = {
        switchPanicEnd,
        switchNormal,
    }

    def __init__(self, server, *args, **kwargs):
        """ Device class

            Args:
                server (Server): Domoticz server object where to maintain the device            
                    idx (:obj:`int`, optional): ID of an existing device
                or
                    hardware (:obj:`obj`, optional): Hardware to add device
                    name (:obj:`str`, optional): Name of the device
                        type (:obj:`int`, optional): Device type
                        subtype (:obj:`int`, optional): Subtype of device
                    or 
                        typename (:obj:`str`, optional): Type name of the device
        """
        self._idx = None
        self._hardware = None
        self._name = None
        self._type = None
        self._subtype = None
        self._typename = None
        self._htype = None
        self._nvalue = None
        self._svalue = None
        if isinstance(server, Server) and server.exists():
            self._server = server
        else:
            self._server = None
        # Existing device: def __init__(self, server, idx)
        if len(args) == 1:
            # For existing device
            #   dev = dom.Device(server, 180)
            self._idx = int(args[0])
        # New device:      def __init__(self, server, hardware, name, type=None, subtype=None):
        elif len(args) == 2:
            self._idx = None
            if isinstance(args[0], Hardware):
                if args[0].exists():
                    self._hardware = args[0]
            else:
                self._hardware = None
            self._name = args[1]
            # Try to get named parameters
            self._subtype = kwargs.get("subtype")
            self._type = kwargs.get("type")
            self._typename = kwargs.get("typename")
        else:
            self._idx = kwargs.get("idx")
            if self._idx is None:
                self._hardware = kwargs.get("hardware")
                self._name = kwargs.get("name")
                self._subtype = kwargs.get("subtype")
                self._type = kwargs.get("type")
                self._typename = kwargs.get("typename")
        if self._typename is not None:
            self._type = None
            self._subtype = None
        self._api = self._server.api
        self._init()

    def __str__(self):
        return "{}({}, {}: \"{}\")".format(self.__class__.__name__,
                                           str(self._server),
                                           self._idx,
                                           self._name)

    # ..........................................................................
    # Private methods
    # ..........................................................................
    def _init(self):
        if self._idx is not None:
            # Retrieve status of specific device: /json.htm?type=devices&rid=IDX&displayhidden=1
            querystring = "type={}&rid={}&displayhidden=1".format(
                self._type_devices,
                self._idx)
        elif self._name is not None:
            # Get all devices: /json.htm?type=devices&displayhidden=1
            querystring = "type={}&displayhidden=1".format(
                self._type_devices)
        else:
            querystring = ""
        self._api.querystring = querystring
        self._api.call()
        found_dict = {}
        if self._api.status == self._api.OK:
            d = self._api.data
            # For some reason next property is only given in device and scene calls.
            self._server._acttime = d.get("ActTime")
            # Update the server properties.
            self._server._astrtwilightend = d.get("AstrTwilightEnd")
            self._server._astrtwilightstart = d.get("AstrTwilightStart")
            self._server._civtwilightend = d.get("CivTwilightEnd")
            self._server._civtwilightstart = d.get("CivTwilightStart")
            self._server._daylength = d.get("DayLength")
            self._server._nauttwilightend = d.get("NautTwilightEnd")
            self._server._nauttwilightstart = d.get("NautTwilightStart")
            self._server._servertime = d.get("ServerTime")
            self._server._sunatsouth = d.get("SunAtSouth")
            self._server._sunrise = d.get("Sunrise")
            self._server._sunset = d.get("Sunset")
            # In param=getversion it is "version"
            self._server._version = d.get("app_version")
            # Search for the given device
            if self._api.payload:
                for result_dict in self._api.payload:
                    if (self._idx is not None and int(result_dict.get("idx")) == self._idx) \
                            or (self._name is not None and result_dict.get("Name") == self._name):
                        # Found device :)
                        found_dict = result_dict
                        break
        # Update device properties
        # The list below may be not complete!!!
        self._addjmulti = found_dict.get("AddjMulti")
        self._addjmulti2 = found_dict.get("AddjMulti2")
        self._addjvalue = found_dict.get("AddjValue")
        self._addjvalue2 = found_dict.get("AddjValue2")
        self._barometer = found_dict.get("Barometer")
        self._batterylevel = found_dict.get("BatteryLevel", NUM_MAX)
        self._cameraidx = found_dict.get("CameraIdx")
        self._chill = found_dict.get("Chill")
        self._color = Color(color=found_dict.get("Color", "{}"))
        self._counter = found_dict.get("Counter")
        self._counterdeliv = found_dict.get("CounterDeliv")
        self._counterdelivtoday = found_dict.get("CounterDelivToday")
        self._countertoday = found_dict.get("CounterToday")
        self._current = found_dict.get("Current")
        self._customimage = found_dict.get("CustomImage")
        self._data = found_dict.get("Data")
        self._daytime = found_dict.get("DayTime")
        self._description = found_dict.get("Description")
        self._desc = found_dict.get("Desc")
        self._dewpoint = found_dict.get("DewPoint")
        self._dimmertype = found_dict.get("DimmerType")
        self._direction = found_dict.get("Direction")
        self._directionstr = found_dict.get("DirectionStr")
        self._displaytype = found_dict.get("displaytype")
        self._favorite = found_dict.get("Favorite")
        self._forecast = found_dict.get("Forecast")
        self._forecaststr = found_dict.get("ForecastStr")
        self._forecast_url = found_dict.get("forecast_url")  # base64 encoded
        self._gust = found_dict.get("Gust")
        self._havedimmer = found_dict.get("HaveDimmer")
        self._havegroupcmd = found_dict.get("HaveGroupCmd")
        self._havetimeout = found_dict.get("HaveTimeout")
        self._humidity = found_dict.get("Humidity")
        self._humiditystatus = found_dict.get("HumidityStatus")
        self._id = found_dict.get("ID")
        dummy = found_dict.get("idx", self._idx)
        self._idx = int(dummy) if dummy is not None else None
        # Next property available with:
        #     /json.htm?type=command&param=getlightswitches
        #     /json.htm?type=devices&filter=light&used=true&order=Name
        self._isdimmer = found_dict.get("IsDimmer")
        self._image = found_dict.get("Image")
        self._internalstate = found_dict.get("InternalState")
        self._issubdevice = found_dict.get("IsSubDevice")
        self._lastupdate = found_dict.get("LastUpdate")
        self._level = found_dict.get("Level")
        self._levelactions = found_dict.get("LevelActions")
        self._levelint = found_dict.get("LevelInt")
        self._levelnames = found_dict.get("LevelNames")
        self._leveloffhidden = found_dict.get("LevelOffHidden")
        self._maxdimlevel = found_dict.get("MaxDimLevel")
        self._mode = found_dict.get("Mode")
        self._modes = found_dict.get("Modes")
        self._name = found_dict.get("Name", self._name)
        self._notifications = found_dict.get("Notifications")
        self._options = found_dict.get("Options")
        # The first RoomPlan to which this device was assigned?
        self._planid = found_dict.get("PlanID")
        # List of RoomPlan idxs containg this device
        self._planids = found_dict.get("PlanIDs")
        self._pressure = found_dict.get("Pressure")
        self._protected = found_dict.get("Protected")
        self._quality = found_dict.get("Quality")
        self._radiation = found_dict.get("Radiation")
        self._rain = found_dict.get("Rain")
        self._rainrate = found_dict.get("RainRate")
        self._selectorstyle = found_dict.get("SelectorStyle")
        self._sensortype = found_dict.get("SensorType")
        self._sensorunit = found_dict.get("SensorUnit")
        self._setpoint = found_dict.get("SetPoint")
        self._shownotifications = found_dict.get("ShowNotifications")
        self._signallevel = found_dict.get("SignalLevel")
        self._speed = found_dict.get("Speed")
        self._state = found_dict.get("State")
        self._status = found_dict.get("Status")
        self._strparam1 = found_dict.get("StrParam1")
        self._strparam2 = found_dict.get("StrParam2")
        self._subtype = found_dict.get("SubType", self._subtype)
        self._switchtype = found_dict.get("SwitchType")
        self._switchtypeval = found_dict.get("SwitchTypeVal")
        self._temp = found_dict.get("Temp")
        self._timers = found_dict.get("Timers")
        self._trend = found_dict.get("trend")
        self._type = found_dict.get("Type", self._type)
        self._typeimg = found_dict.get("TypeImg")
        self._unit = found_dict.get("Unit")
        self._until = found_dict.get("Until")
        self._used = found_dict.get("Used")
        self._usage = found_dict.get("Usage")
        self._usagedeliv = found_dict.get("UsageDeliv")
        self._usedbycamera = found_dict.get("UsedByCamera")
        self._uvi = found_dict.get("UVI")
        self._valuequantity = found_dict.get("ValueQuantity")
        self._valueunits = found_dict.get("ValueUnits")
        self._visibility = found_dict.get("Visibility")
        self._voltage = found_dict.get("Voltage")
        self._xoffset = found_dict.get("XOffset")
        self._yoffset = found_dict.get("YOffset")

        # Some info from the hardware also comes
        hardwareid = found_dict.get("HardwareID")
        if hardwareid is not None:
            hw = Hardware(self._server, idx=hardwareid)
            if hw.exists():
                self._hardware = hw
                self._hardware._hardwaretype = found_dict.get("HardwareType")
            else:
                self._hardware = None

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
                and self._hardware is not None \
                and self._name is not None \
                and self._type is not None \
                and self._subtype is not None:
            # /json.htm?type=createdevice&idx=IDX&sensorname=SENSORNAME&devicetype=DEVICETYPE&devicesubtype=SUBTYPE
            self._api.querystring = "type={}&idx={}&sensorname={}&devicetype={}&devicesubtype={}".format(
                self._type_create_device,
                self._hardware._idx,
                self._name,
                self._type,
                self._subtype)
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
