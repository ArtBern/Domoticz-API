#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .scene import Scene
from .utilities import (bool_2_int, int_2_bool, bool_2_str, str_2_bool)
from abc import ABC
from .basetimer import BaseTimer, TimerDays

class SceneTimer(BaseTimer):

    _param_add_device_timer = "addscenetimer"
    _param_update_device_timer = "updatescenetimer"
    _param_delete_device_timer = "deletescenetimer"
    _param_clear_device_timers = "clearscenetimers"
    _param_timers = "scenetimers"
    
    _args_length = 3
    
    def __init__(self, device, *args, **kwargs):
        """ SceneTimer class
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
    def loadbyscene(scene):
        result = []
        if isinstance(scene, Scene) and scene.exists():
            api = scene._api
            querystring = "type={}&idx={}".format(SceneTimer._param_timers, scene._idx)
            api.querystring = querystring
            api.call()
            if api.is_OK() and api.has_payload():
                for var in api.payload:
                    var["is_from_factory"] = True
                    timr = SceneTimer(scene, **var)
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



