#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import DomoticzAPI as dom
from datetime import datetime
import time


def main():
    print("********************************************************************************")
    print("Test script ..................: {} ({})".format(__file__, dom.VERSION))
    print("********************************************************************************")
    server = dom.Server("localhost", "81")
    print(server)
    print("\r")

    print("********************************************************************************")
    print("Create new hardware")
    print("********************************************************************************")
    hw3 = dom.Hardware(server, type=15, name="Test Hardware") 
    hw3.add()
    print("{}: {} - {}".format(hw3, server.api.status, server.api.title))

    if hw3.exists():
        print("\r")
        print("********************************************************************************")
        print("Add device to new hardware")
        print("********************************************************************************")
        dev3 = dom.Device(server, hw3, "Test Thermostat",
                          type=242, subtype=1)  # Thermostat
        print("dev3.hardware: {}".format(dev3.hardware))
        print("{}: {} - {}".format(dev3, server.api.status, server.api.title))

        dev3.add()
        print("{}: {} - {}".format(dev3, server.api.status, server.api.title))
        if dev3.exists():
            print("Thermostat successfully created")
            print("Name: {}".format(dev3.name))
            print("Status: {}".format(dev3.data))
            tmr = dom.DeviceTimer(dev3, dom.DeviceTimer.TME_TYPE_ON_TIME, 1, 0, dom.TimerDays.Monday | dom.TimerDays.Thuesday, 5, None)
            print("Timer exists: {}".format(tmr.exists()))
            print("Adding new timer.")
            tmr.add()
            print("Timer exists: {}".format(tmr.exists()))
            if tmr.exists():
                print ("Device timer successfully created")
                print (tmr)
            else:
                print ("Failed to add timer!!!")
                return
            
            print("\r")
            print("--------------------------------------------------------------------------------")
            print("Update timer")
            print("--------------------------------------------------------------------------------")
            tmr.date = "2020-12-01"
            tmr.timertype = dom.DeviceTimer.TME_TYPE_FIXED_DATETIME
            tmr.hour = 2
            tmr.minute = 30
            
            print (tmr)
            


    # Cleanup test data
    hw3.delete()


if __name__ == "__main__":
    main()
