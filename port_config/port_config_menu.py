#!/usr/bin/env python3

import macsearch, check, config
import sys

banner = '''optional, remove if you don't need'''


def main_menu():
    while True:
        selection = input("\r\nEnter a selection:" "\r\n1 = check configuration" "\r\n2 = configure port"
                          "\r\n3 = enable port" "\r\n4 = add port description"
                          "\r\n5 = search by MAC address" "\r\n6 = attempt to resolve MAC to IP address"
                          '\r\n7 = exit'
                          "\r\nInput a choice here: ")
        if selection == "1":
            checking = check.Check()
            checking.check_config()
        elif selection == "2":
            config_port = config.Config()
            config_port.port_config()
        elif selection == "3":
            enable_port = config.Config()
            enable_port.port_enable()
        elif selection == '4':
            descr_port = config.Config()
            descr_port.port_description()
        elif selection == '5':
            macsearch.mac_search()
        elif selection == "6":
            resolve = check.Check()
            resolve.get_ip_mac_address()
        elif selection == '7':
            sys.exit()
        else:
            print("\r\nChoose either 1, 2, 3, 4, 5, 6, or 7" + "\r\n")


if __name__ == '__main__':
    print('\r\n' + banner)
    main_menu()
