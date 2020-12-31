#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import DomoticzAPI as dom


def main():
    print("********************************************************************************")
    print("Test script ................ : {} ({})".format(__file__, dom.VERSION))
    print("********************************************************************************")
    server = dom.Server("localhost", "81")
    print(server.setting)
 
    key = "Title"
    value = server.setting.get_value(key)
    print("Current {}: {}".format(key, value))
    server.setting.set_value(key, "DomoticzAPI Test")
    print("Test {}: {}".format(key, server.setting.get_value(key)))
    server.setting.set_value(key, value)
    print("Restored {}: {}".format(key, server.setting.get_value(key)))
    
    key = dom.Settings.KEY_WEBTHEME
    value = server.setting.get_value(key)
    print("Current theme {}: {}".format(key, value))
    server.setting.set_value(key, "elemental")
    print("Test theme {}: {}".format(key, server.setting.get_value(key)))
    server.setting.set_value(key, value)
    print("Restored theme {}: {}".format(key, server.setting.get_value(key)))
    
    # Check ON/OF (checkbox) switch in the settings
    key = dom.Settings.KEY_ALLOWWIDGETORDERING
    value = server.setting.get_value(key)
    print("Current {}: {}".format(key, value))
    if value == dom.Settings.SETTING_ON:
        server.setting.set_value(key, dom.Settings.SETTING_OFF)
    else:
        server.setting.set_value(key, dom.Settings.SETTING_ON)
    print("Test {}: {}".format(key, server.setting.get_value(key)))
    server.setting.set_value(key, value)
    print("Restored {}: {}".format(key, server.setting.get_value(key)))

    key = "BatterLowLevel"
    print("{}: {}".format(key, server.setting.get_value(key)))
    key = "AcceptNewHardware"
    print("{}: {}".format(key, server.setting.get_value(key)))
    key = "WeightUnit"
    print("{}: {}".format(key, server.setting.get_value(key)))
    
    key = dom.Settings.KEY_ACTIVETIMERPLAN
    value = server.setting.get_value(key);
    print("ActiveTimerPlan ................ : {}".format(value))
    server.setting.set_value(key, 1)
    print("ActiveTimerPlan ................ : {}".format(server.setting.get_value(key)))
    server.setting.set_value(key, 2)
    print("ActiveTimerPlan ................ : {}".format(server.setting.get_value(key)))
    server.setting.set_value(key, value)

if __name__ == "__main__":
    main()
