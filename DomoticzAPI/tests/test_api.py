#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import DomoticzAPI as dom


def main():
    print("********************************************************************************")
    print("Test script .............. : {} ({})".format(__file__, dom.VERSION))
    print("********************************************************************************")

    server = dom.Server("192.168.1.16", "81")
    if server.exists():
        print("\r")
        print("--------------------------------------------------------------------------------")
        print("Current properties")
        print("--------------------------------------------------------------------------------")
        print("server.api ............... : {}".format(server.api))
        print("server.api.data .......... : {}".format(server.api.data))
        print("server.api.endpoint ...... : {}".format(server.api.endpoint))
        print("server.api.message ....... : {}".format(server.api.message))
        print("server.api.payload ....... : {}".format(server.api.payload))
        print("server.api.querystring ... : {}".format(server.api.querystring))
        print("server.api.status ........ : {}".format(server.api.status))
        print("server.api.title ......... : {}".format(server.api.title))
        print("server.api.url ........... : {}".format(server.api.url))
        print("\r")
        print("--------------------------------------------------------------------------------")
        print("Setting properties")
        print("--------------------------------------------------------------------------------")
        print("server.api.message         = test")
        server.api.message = "test"
        print("server.api.message ....... : {}".format(server.api.message))
        print("server.api.status          = test")
        server.api.status = "test"
        print("server.api.status ........ : {}".format(server.api.status))
        print("server.api.title           = test")
        server.api.title = "test"
        print("server.api.title ......... : {}".format(server.api.title))
        print("server.api.querystring     = type=command&param=getversion")
        server.api.querystring = "type=command&param=getversion"
        print("server.api.querystring ... : {}".format(server.api.querystring))
        print("\r")
        print("--------------------------------------------------------------------------------")
        print("Call methods")
        print("--------------------------------------------------------------------------------")
        print("Method ................... : {} with {}".format(
            "call", server.api.querystring))
        server.api.call()
        print("\r")
        print("--------------------------------------------------------------------------------")
        print("New properties")
        print("--------------------------------------------------------------------------------")
        print("server.api ............... : {}".format(server.api))
        print("server.api.data .......... : {}".format(server.api.data))
        print("server.api.message ....... : {}".format(server.api.message))
        print("server.api.payload ....... : {}".format(server.api.payload))
        print("server.api.querystring ... : {}".format(server.api.querystring))
        print("server.api.status ........ : {}".format(server.api.status))
        print("server.api.title ......... : {}".format(server.api.title))
        print("server.api.url ........... : {}".format(server.api.url))
        print("version .................. : {}".format(
            server.api.data.get("version")))
    else:
        print("Server not found!!!")
        print(server.api.message)


if __name__ == "__main__":
    main()
