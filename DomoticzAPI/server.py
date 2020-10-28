#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#from .const import(RETURN_EMPTY, RETURN_ERROR, RETURN_OK)
from .api import API
from .setting import Setting
from .translation import Translation
import json
from datetime import datetime
from urllib.parse import urlparse


class Server:

    DEFAULT_ADDRESS = "localhost"
    DEFAULT_PORT = "8080"
    DEFAULT_LANGUAGE = "en"

    # Protocols
    PROTOCOL_HTTP = "http"
    PROTOCOL_HTTPS = "https"

    # rights
    RIGHTS_LOGIN_REQUIRED = -1
    RIGHTS_NOT_DEFINED = 0
    RIGHTS_LOGGED_IN = 2
    RIGHTS = {
        RIGHTS_LOGIN_REQUIRED,
        RIGHTS_NOT_DEFINED,
        RIGHTS_LOGGED_IN,
    }

    # type parameter
    _type = "type"
    _type_command = "command"

    _url_command = "{}={}&".format(_type, _type_command)

    # param parameter
    _param = "param={}"
    _param_checkforupdate = "checkforupdate"
    _param_execute_script = "execute_script"
    _param_getauth = "getauth"
    _param_getlanguage = "getlanguage"
    _param_getuptime = "getuptime"
    _param_log = "addlogmessage"
    _param_reboot = "system_reboot"
    _param_shutdown = "system_shutdown"
    _param_sun = "getSunRiseSet"
    _param_version = "getversion"

    _param_downloadupdate = "downloadupdate"
    _param_downloadready = "downloadready"
    _param_execute_script = "execute_script"

    def __init__(self, address=DEFAULT_ADDRESS, port=DEFAULT_PORT, **kwargs):
        """The Server class represents the Domoticz server
            Args:
                address (:obj:`str`, optional): the IP-address or hostname of your Domoticz installation. Default = "127.0.0.1".
                port (:obj:`str`, optional): the port number of your Domoticz installation. Default = "8080"
                user (:obj:`str`, optional): the username to access Domoticz.
                password (:obj:`str`, optional): the password to access Domoticz.
                url (:obj:`str`, optional): use url to pass protocol/adress/port/user and password to access Domoticz.
        """
        self._address = address
        self._port = port
        self._protocol = 'http'
        self._user = kwargs.get("user")
        self._password = kwargs.get("password")
        self._domUrl = kwargs.get("url")

        self._rights = self.RIGHTS_NOT_DEFINED
        self._currentdate_date = datetime.now().date()
        self._language = self.DEFAULT_LANGUAGE

        if self._domUrl != None:
            url = urlparse(self._domUrl)
            self._protocol = url.scheme.lower()
            if url.username != None:
                self._user = url.username
            if url.password != None:
                self._password = url.password
            if url.port != None:
                self._port = url.port
            else:
                if self._protocol == 'https':
                    self._port = 443
            self._address = url.hostname

        if self._password != None:
            self._rights = self.RIGHTS_LOGIN_REQUIRED

        self._api = API(self)
        self._exists = False

        # Check if authorization is required
        self._getAuth()
        if self._api.status == self._api.OK:
            self._exists = True
        self._setting = Setting(self)
        if self._rights == self.RIGHTS_LOGGED_IN or (
                self._rights == self.RIGHTS_LOGIN_REQUIRED and self._user is not None):
            # No need to initialize all time properties. Next procedures will do that.
            self._getVersion()
            if self._rights == self.RIGHTS_LOGIN_REQUIRED and self._domoticzupdateurl is None:
                self._api.status = self._api.ERROR
                self._api.message = "Invalid login"
            else:
                self._checkForUpdate()
                self._getSunRiseSet(True)
        else:
            self._api.status = self._api.ERROR
            self._api.message = "Authorization is required"
        self._getLanguage()
        self._translation = Translation(self, language=self._language)

    def __str__(self):
        txt = "{}(\"{}\", \"{}\"): {}".format(
            self.__class__.__name__, self._address, self._port, self._exists)
        return txt

    def __getattr__(self, item):
        return None

    # ..........................................................................
    # Private methods
    # ..........................................................................
    def _getAuth(self):
        # /json.htm?type=command&param=getauth
        self._api.querystring = "type=command&param={}".format(
            self._param_getauth)
        self._api.call()
        if self._api.data:
            self._rights = self._api.data.get("rights")

    def _getVersion(self):
        # /json.htm?type=command&param=getversion
        if self._exists:
            self._api.querystring = "type=command&param={}".format(
                self._param_version)
            self._api.call()
            self._build_time = self._api.data.get("build_time")
            self._domoticzupdateurl = self._api.data.get("DomoticzUpdateURL")
            self._dzvents_version = self._api.data.get("dzvents_version")
            self._hash = self._api.data.get("hash")
            self._haveupdate = self._api.data.get("HaveUpdate")
            self._python_version = self._api.data.get("python_version")
            self._revision = self._api.data.get("Revision")
            self._systemname = self._api.data.get("SystemName")
            self._version = self._api.data.get("version")

    def _checkForUpdate(self):
        # /json.htm?type=command&param=checkforupdate
        if self._exists:
            self._api.querystring = "type=command&param={}&forced=true".format(
                self._param_checkforupdate)
            self._api.call()
            self._domoticzupdateurl = self._api.data.get("DomoticzUpdateURL")
            self._haveupdate = self._api.data.get("HaveUpdate")
            self._revision = self._api.data.get("Revision")
            self._systemname = self._api.data.get("SystemName")
            self._statuscode = self._api.data.get("statuscode")

    @staticmethod
    def _str2dt(value, format):
        try:
            return datetime.strptime(value, format)
        except TypeError:
            import time
            return datetime.datetime(*(time.strptime(value, format)[0:6]))
        except:
            return None

    def _getLanguage(self):
        # /json.htm?type=command&param=getlanguage
        if self._exists:
            self._api.querystring = "type=command&param={}".format(
                self._param_getlanguage)
            self._api.call()
            self._language = self._api.data.get("language")

    def _getSunRiseSet(self, now=False):
        # /json.htm?type=command&param=getSunRiseSet
        if self._exists:
            if isinstance(self._currentdate_date, datetime):
                if datetime.now().date() > self._currentdate_date:
                    now = True
            if now:
                self._api.querystring = "type=command&param={}".format(
                    self._param_sun)
                self._api.call()
                self._astrtwilightend = self._api.data.get("AstrTwilightEnd")
                self._astrtwilightstart = self._api.data.get(
                    "AstrTwilightStart")
                self._civtwilightend = self._api.data.get("CivTwilightEnd")
                self._civtwilightstart = self._api.data.get("CivTwilightStart")
                self._nauttwilightend = self._api.data.get("NautTwilightEnd")
                self._nauttwilightstart = self._api.data.get(
                    "NautTwilightStart")
                self._sunrise = self._api.data.get("Sunrise")
                self._sunset = self._api.data.get("Sunset")
                self._sunatsouth = self._api.data.get("SunAtSouth")
                self._daylength = self._api.data.get("DayLength")
                self._servertime = self._api.data.get("ServerTime")
                # Remember the datetime from this call
                if self._api.status == self._api.OK:
                    self._currentdate = self._servertime[:10]  # yyyy-mm-dd
                    self._currentdate_date = self._str2dt(self._servertime, "%Y-%m-%d %H:%M:%S").date()

                    self._servertime_dt = self._str2dt(self._servertime, "%Y-%m-%d %H:%M:%S")
                    sr = self._str2dt(self._currentdate + " " + self._sunrise, "%Y-%m-%d %H:%M")
                    ss = self._str2dt(self._currentdate + " " + self._sunset, "%Y-%m-%d %H:%M")
                    ats = self._str2dt(self._currentdate + " " + self._astrtwilightstart, "%Y-%m-%d %H:%M")
                    ate = self._str2dt(self._currentdate + " " + self._astrtwilightend, "%Y-%m-%d %H:%M")
                    self._is_day = sr < self._servertime_dt < ss
                    self._is_night = (self._servertime_dt < ats) or (
                        self._servertime_dt > ate)
                else:
                    self._currentdate = None
                    self._currentdate_date = None
                    self._is_day = None
                    self._is_night = None
                    self._servertime_dt = None

    def _getConfig(self):
        # /json.htm?type=command&param=getconfig
        # Not required yet. May be interesting to get latitude and longitude. Most is GUI stuff.
        if self._exists:
            pass

    def _getUpTime(self):
        # /json.htm?type=command&param=getuptime
        if self._exists:
            self._api.querystring = "type=command&param={}".format(
                self._param_getuptime)
            self._api.call()
            d = self._api.data.get("days") * 24 * 60 * 60
            h = self._api.data.get("hours") * 60 * 60
            m = self._api.data.get("minutes") * 60
            s = self._api.data.get("seconds")
            self._uptime = d + h + m + s

    # ..........................................................................
    # Public Methods
    # ..........................................................................

    def checkForUpdate(self):
        """
        Retrieves Domoticz version information
        """
        self._checkForUpdate()

    def exists(self):
        """ Check if Domoticz server exists """
        return self._exists

    def has_location(self):
        """ Check if location is defined for sunrise, sunset, etc."""
        return self._setting.get_value("Location") is not None

    def logmessage(self, text):
        """ Send text to the Domoticz log """
        # /json.htm?type=command&param=addlogmessage&message=MESSAGE
        if self._exists:
            self._api.querystring = "type=command&param={}&message={}".format(
                self._param_log,
                text
            )
            self._api.call()

    def reboot(self):
        """Reboot the Domoticz server"""
        # /json.htm?type=command&param=system_reboot
        if self._exists:
            self._api.querystring = "type=command&param={}".format(
                self._param_reboot)
            self._api.call()

    def shutdown(self):
        """Shutdown the Domoticz server"""
        # /json.htm?type=command&param=system_shutdown
        if self._exists:
            self._api.querystring = "type=command&param={}".format(
                self._param_shutdown)
            self._api.call()

    def update(self):
        """Update the Domoticz software"""
        if self._exists:
            self._checkForUpdate()
            if self._haveupdate:
                # /json.htm?type=command&param=downloadupdate
                self._api.querystring = "type=command&param={}".format(
                    self._param_downloadupdate
                )
                self._api.call()
                if self._api.status == self._api.OK:
                    # Wait until download is completed
                    condition = False
                    while not condition:
                        # /json.htm?type=command&param=downloadready
                        self._api.querystring = "type=command&param={}".format(
                            self._param_downloadready
                        )
                        self._api.call()
                        condition = self._api.data.get("downloadok", False)
                    # Download complete: update the software
                    self._api.querystring = "type=command&param={}&scriptname=update_domoticz&direct=false".format(
                        self._param_execute_script
                    )
                    self._api.call()

    # ..........................................................................
    # Properties
    # ..........................................................................
    # /json.htm?type=command&param=getSunRiseSet
    #
    # Used undocumented url's:
    #
    # /json.htm?type=command&param=getversion
    # /json.htm?type=command&param=checkforupdate
    # ..........................................................................

    @property
    def act_time(self):
        """Current date time on the Domoticz server expressed as condensed UTC-label.
        Also returned from device calls, together with the getSunRiseSet values.
        """
        # Calculate acttime. Faster then API calls.
        d = datetime.utcnow()
        epoch = datetime(1970, 1, 1)
        self._acttime = int((d - epoch).total_seconds())
        return self._acttime

    @property
    def address(self):
        """Domoticz server address"""
        return self._address

    @address.setter
    def address(self, value):
        self._address = value

    @property
    def api(self):
        """:obj:`API`"""
        return self._api

    @property
    # getSunRiseSet
    def astrtwilightend(self):
        """"""
        self._getSunRiseSet()
        return self._astrtwilightend

    @property
    def astrtwilightend_dt(self):
        return self._str2dt(self._currentdate + " " + self._astrtwilightend, "%Y-%m-%d %H:%M")

    @property
    # getSunRiseSet
    def astrtwilightstart(self):
        self._getSunRiseSet()
        return self._astrtwilightstart

    @property
    def astrtwilightstart_dt(self):
        return self._str2dt(self._currentdate + " " + self._astrtwilightstart, "%Y-%m-%d %H:%M")

    @property
    # getversion
    def build_time(self):
        return self._build_time

    @property
    def build_time_dt(self):
        return self._str2dt(self._build_time, "%Y-%m-%d %H:%M:%S")

    @property
    # getSunRiseSet
    def civtwilightend(self):
        self._getSunRiseSet()
        return self._civtwilightend

    @property
    def civtwilightend_dt(self):
        return self._str2dt(self._currentdate + " " + self._civtwilightend, "%Y-%m-%d %H:%M")

    @property
    # getSunRiseSet
    def civtwilightstart(self):
        self._getSunRiseSet()
        return self._civtwilightstart

    @property
    def civtwilightstart_dt(self):
        return self._str2dt(self._currentdate + " " + self._civtwilightstart, "%Y-%m-%d %H:%M")

    @property
    # getSunRiseSet
    def daylength(self):
        """Day length"""
        self._getSunRiseSet()
        return self._daylength

    @property
    # getversion & checkforupdate
    def domoticzupdateurl(self):
        """Domoticz update url"""
        return self._domoticzupdateurl

    @property
    # getversion
    def dzvents_version(self):
        """dzVents version"""
        return self._dzvents_version

    @property
    # getversion & checkforupdate
    def haveupdate(self):
        """Domoticz update available?"""
        return self._haveupdate

    @property
    # getversion
    def hash(self):
        """Build hash from Git"""
        return self._hash

    @property
    def is_day(self):
        return self._is_day

    @property
    def is_night(self):
        return self._is_night

    @property
    # getlanguage
    def language(self):
        """Domoticz user interface language"""
        return self._language

    @property
    # getSunRiseSet
    def nauttwilightend(self):
        self._getSunRiseSet()
        return self._nauttwilightend

    @property
    def nauttwilightend_dt(self):
        return self._str2dt(self._currentdate + " " + self._nauttwilightend, "%Y-%m-%d %H:%M")

    @property
    # getSunRiseSet
    def nauttwilightstart(self):
        self._getSunRiseSet()
        return self._nauttwilightstart

    @property
    def nauttwilightstart_dt(self):
        return self._str2dt(self._currentdate + " " + self._nauttwilightstart, "%Y-%m-%d %H:%M")

    @property
    def password(self):
        """Domoticz password"""
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def port(self):
        """Domoticz server port"""
        return self._port

    @port.setter
    def port(self, port):
        self._port = port

    @property
    def protocol(self):
        """http or https"""
        return self._protocol

    @property
    # getversion
    def python_version(self):
        """Python version on Domoticz server"""
        return self._python_version

    @property
    # getversion & checkforupdate
    def revision(self):
        """Domoticz revision"""
        return self._revision

    @property
    # getauth
    def rights(self):
        """Domoticz protection"""
        return self._rights

    @property
    def setting(self):
        """:obj: `Setting`"""
        return self._setting

    @property
    # getSunRiseSet
    def servertime(self):
        """Domoticz server time"""
        self._getSunRiseSet(True)
        return self._servertime

    @property
    def servertime_dt(self):
        """:obj:`datetime` Domoticz server time"""
        return self._str2dt(self._servertime, "%Y-%m-%d %H:%M:%S")

    @property
    # checkforupdate
    def statuscode(self):
        return self._statuscode

    @property
    # getSunRiseSet
    def sunatsouth(self):
        self._getSunRiseSet()
        return self._sunatsouth

    @property
    def sunatsouth_dt(self):
        return self._str2dt(self._currentdate + " " + self._sunatsouth, "%Y-%m-%d %H:%M")

    @property
    # getSunRiseSet
    def sunrise(self):
        self._getSunRiseSet()
        return self._sunrise

    @property
    def sunrise_dt(self):
        return self._str2dt(self._currentdate + " " + self._sunrise, "%Y-%m-%d %H:%M")

    @property
    # getSunRiseSet
    def sunset(self):
        self._getSunRiseSet()
        return self._sunset

    @property
    def sunset_dt(self):
        return self._str2dt(self._currentdate + " " + self._sunset, "%Y-%m-%d %H:%M")

    @property
    # getversion & checkforupdate
    def systemname(self):
        return self._systemname

    @property
    def translation(self):
        return self._translation

    @property
    def uptime(self):
        """Uptime of Domoticz in seconds.

        Updated every 5 seconds.
        """
        self._getUpTime()
        return self._getUpTime

    @property
    def user(self):
        """Domoticz user"""
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    @property
    # getversion
    def version(self):
        """Domoticz version"""
        return self._version
