#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .settings import Settings
import urllib.request as request
import urllib.parse as parse
import base64


class Setting:

    _type_settings = "settings"

    _url = "storesettings"

    def __init__(self, server):
        """Settings class, to get Domoticz settings

        Args:
            server (:obj:`Server`): Domoticz server object where to maintain the device            
        """
        self._server = server

    def __str__(self):
        txt = "{}(\"{}\")".format(self.__class__.__name__, self._server)
        return txt

    def _getSettings(self):
        # /json.htm?type=settings
        # Not required yet. Perhaps in the near future to be sure that ALL setting are available for use.
        self._settings = {}
        if self._server.exists():
            self._server._api.querystring = "type={}".format(self._type_settings)
            self._server._api.call()
            if self._server._api.status == self._server._api.OK:
                self._settings = self._server._api.data

    # ..........................................................................
    # Public methods
    # ..........................................................................
    def get_value(self, key):
        """Retrieve the value from a Domoticz setting

        Args:
            key (str): key from a setting, eg. "AcceptNewHardware", "SecPassword", etc
        """
        # Requery settings
        # /json.htm?type=settings
        # Not required yet. Perhaps in the near future to be sure that ALL setting are available for use.
        if key in Settings.KEYS:
            self._getSettings()
  
            return self._settings.get(key)
        else:
            return None

    def set_value(self, key, value):
        """Set a value in the Domoticz settings

        Args:
            key (str): key from a setting, eg. "AcceptNewHardware", "SecPassword", etc
            value: Value for the Domoticz setting
        """
        if key in Settings.KEYS:
            url = "{}{}".format(
                self._server._api.endpoint,
                self._url
            )
            self._getSettings()
            d = self._settings
            # First we have to transform all switches from None/0/1 to <deleted>/on :(
            for k, v in list(d.items()):
                if k in Settings.KEY_SWITCHES:
                    # DisableDzVentsSystem works the opposite way!!!
                    if k == Settings.KEY_DISABLEDZVENTSSYSTEM:
                        if v == Settings.SETTING_ON:
                            try:
                                del d[k]
                            except:
                                pass
                        else:
                            d[k] = "on"
                    else:
                        if v != Settings.SETTING_ON:
                            try:
                                del d[k]
                            except:
                                pass
                        else:
                            # Now the real disaster!!! When you get the values, the keys are sometimes different to set these values!!!
                            if key in (Settings.KEY_CHECKFORUPDATES, Settings.KEY_ENABLEAUTOBACKUP):
                                del d[k]
                                if key == Settings.KEY_CHECKFORUPDATES:
                                    d.update({'checkforupdates': 'on'})
                                if key == Settings.KEY_ENABLEAUTOBACKUP:
                                    d.update({'enableautobackup': 'on'})
                            else:
                                d[k] = "on"
                
                if k in Settings.KEY_ENCODED:
                    d[k] = base64.b64decode(v)
                                
            # Finally: set the value
            if key in Settings.KEY_SWITCHES:
                if value in Settings.SETTING_VALUES:
                    # DisableDzVentsSystem works the opposite way!!!
                    if key == Settings.KEY_DISABLEDZVENTSSYSTEM:
                        if value == Settings.SETTING_ON:
                            try:
                                del d[key]
                            except:
                                pass
                        else:
                            d[key] = "on"
                    else:
                        if value != Settings.SETTING_ON:
                            try:
                                del d[key]
                            except:
                                pass
                        else:
                            d[key] = "on"
            else:
                d[key] = value
            
            # https://github.com/domoticz/domoticz/blob/db346f96e289dc20c0d33c3cffefbb6d4065cc76/main/WebServer.cpp#L8413                    
            d[Settings.KEY_THEMES] = d[Settings.KEY_WEBTHEME]
            
            print("Data" + str(d))
            data = parse.urlencode(d).encode("utf-8")
            req = request.Request(url, data=data)
            try:
                request.urlopen(req)
            except:
                pass
