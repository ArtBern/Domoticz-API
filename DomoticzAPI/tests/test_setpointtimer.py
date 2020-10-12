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
            tmr = dom.SetPointTimer(dev3, True, dom.TimerTypes.TME_TYPE_ON_TIME, 1, 0, dom.TimerDays.Monday | dom.TimerDays.Thuesday, None, 1, 2, 3, 7)
            print (tmr)
            print("Timer exists: {}".format(tmr.exists()))
            print("Adding new timer.")
            tmr.add()
            print("Timer exists: {}".format(tmr.exists()))
            if tmr.exists():
                print ("Thermostat timer successfully created")
                print (tmr)
            else:
                print ("Failed to add timer!!!")
                return
            
            print("\r")
            print("--------------------------------------------------------------------------------")
            print("Update timer")
            print("--------------------------------------------------------------------------------")
            tmr.date = "2020-12-01"
            if (tmr.date is not None):
                raise RuntimeError("Should not be possible to set date for this timertype!!!")

            tmr.occurence = 2
            if (tmr.occurence != 0):
                raise RuntimeError("Should not be possible to set occurence for this timertype!!!")

            tmr.mday = 3
            if (tmr.mday != 0):
                raise RuntimeError("Should not be possible to set mday for this timertype!!!")

            tmr.month = 6
            if (tmr.month != 0):
                raise RuntimeError("Should not be possible to set month for this timertype!!!")
            
            try:
                tmr.timertype = dom.TimerTypes.TME_TYPE_FIXED_DATETIME
                raise RuntimeError("Expected ValueError not raised!!!")
            except ValueError:
                pass
                
            print("\r")
            print("--------------------------------------------------------------------------------")
            print("Negative checks passed.")
            print("Change type to Fixed Date/Time.")            
            print("--------------------------------------------------------------------------------")            
            tmr.setfixeddatetimer("2020-12-02")
            print(tmr)
            print("--------------------------------------------------------------------------------")
            print("Change time.")
            print("--------------------------------------------------------------------------------")           
            tmr.hour = 3
            tmr.minute = 30
            tmr.date = "2020-12-03"
            print (tmr)
            print("--------------------------------------------------------------------------------")
            print("Deactivate timer and set value.")
            print("--------------------------------------------------------------------------------")           
            tmr.active = False
            tmr.temperature = 20.8
            print (tmr)

            tmr1 = dom.SetPointTimer(dev3, True, dom.TimerTypes.TME_TYPE_ON_TIME, 1, 0, dom.TimerDays.Monday | dom.TimerDays.Thuesday, None, 1, 2, 3, 20)
            print("Adding new timer 2.")
            tmr1.add()

            tmr2 = dom.SetPointTimer(dev3, Active=False, Date='2020-12-03', Days=dom.TimerDays.Sunday, MDay=0, Month=0, Occurence=0, Temperature=45, Time='14:30', Type=dom.TimerTypes.TME_TYPE_ON_TIME )
            print("Adding new timer 3.")
            tmr2.add()

            print("--------------------------------------------------------------------------------")
            print("Bulk load timers.")
            print("--------------------------------------------------------------------------------")           
            timers = dom.SetPointTimer.loadbythermostat(dev3)
            for tmr1 in timers:
                print (tmr1)
            
            tmr.delete()
            if tmr.exists():
                print("Failed to delete timer!!!")
            else:
                print("Timer deleted OK.")


    # Cleanup test data
    hw3.delete()


if __name__ == "__main__":
    main()
