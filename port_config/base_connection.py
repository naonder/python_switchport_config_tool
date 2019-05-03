#!/usr/bin/env python3

import netmiko
import json
import port_config_menu


def connector(address):
    with open("/path/to/creds/file.json") as credentials:
        creds = json.load(credentials)

    name = creds["username"]
    passwrd = creds["password"]
    ios = "cisco_ios"
    secret_passwrd = creds["enablepw"]

    netmiko_exceptions = (netmiko.ssh_exception.NetMikoTimeoutException,
                          netmiko.ssh_exception.NetMikoAuthenticationException)

    try:
        connection = netmiko.ConnectHandler(username=name, password=passwrd, device_type=ios, ip=address,
                                            secret=secret_passwrd)
        if ">" in connection.find_prompt():
            connection.enable()
        return connection
    except netmiko_exceptions as e:
        print("\r\nFailed to ", address, e)
        print('\r\nReturning to main menu...')
        port_config_menu.main_menu()
