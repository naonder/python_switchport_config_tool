#!/usr/bin/env python3
import netmiko
import sys
import json
import time
import datetime

today_date = time.strftime("%d-%b-%Y")

with open('path/to/creds.json') as credentials:
    creds = json.load(credentials)

name = creds["username"]
passwrd = creds["password"]
ios = "cisco_ios"
secret_passwrd = creds["enablepw"]
log_file = open('/path/to/log_{}.txt'.format(today_date), 'a')

netmiko_exceptions = (netmiko.ssh_exception.NetMikoTimeoutException,
                      netmiko.ssh_exception.NetMikoAuthenticationException)

start_time = datetime.datetime.now()

print("\r\nThis tool is to be used strictly to check port configurations and/or configure user/printer ports."
      "\r\nUnauthorized use is strictly forbidden. All activity will be logged." + "\r\n")

device = input("Input address or hostname of device: ")
log_file.write('\r\n' + '*' * 79)
log_file.write('\r\n' + '*' * 79)
log_file.write('\r\nUser has connected to {} at {}'.format(device, start_time) + '\r\n')


# Main menu - currently five possible choices/functions can be called depending on option selected
def main():
    while True:
        selection = input("Enter a selection:" "\r\n1 = check configuration" "\r\n2 = configure port"
                          "\r\n3 = enable port" "\r\n4 = add port description" "\r\n5 = quit"
                          "\r\nInput a choice here: ")
        if selection == "1":
            check_config()
            break
        elif selection == "2":
            port_config()
            break
        elif selection == "3":
            port_enable()
            break
        elif selection == '4':
            port_description()
            break
        elif selection == "5":
            end_time = datetime.datetime.now()
            log_file.write('\r\n' * 2)
            log_file.write('User has disconnected from {} at {}'.format(device, end_time) + '\r\n' * 2)
            log_file.close()
            sys.exit()
        else:
            print("\r\nChoose either 1, 2, 3, or 4" + "\r\n")


# Main function used to connect to devices. Will return value to use in other functions as needed
def device_connect():
    try:
        connect = netmiko.ConnectHandler(username=name, password=passwrd, device_type=ios, ip=device,
                                         secret=secret_passwrd)
        if ">" in connect.find_prompt():
            connect.enable()
        return connect
    except netmiko_exceptions as e:
        print("Failed to ", device, e)


def check_config():
    # Will show interface status followed by prompt to show running config of a port
    print("\r\nLogging into device and displaying list of interfaces, standby...." + "\r\n")
    connection = device_connect()
    connection.send_command("terminal length 0")
    int_status = connection.send_command("show interface status")
    print(int_status + "\r\n")
    while True:
        interface = input("Input interface/port number to check: ")
        config = connection.send_command("show run interface {}".format(interface))
        print(config + "\r\n")
        while True:
            continue_on = input("Check another interface [y|n]? ")
            if continue_on == "y":
                break
            elif continue_on == "n":
                print("Returning to main menu" + "\r\n")
                connection.disconnect()
                main()
                break
            else:
                print('Type either "y" or "n"')


def port_enable():
    # Same as above, except this time a user can enable a port
    print("\r\nLogging into device and displaying list of interfaces, standby...." + "\r\n")
    connection = device_connect()
    connection.send_command("terminal length 0")
    int_status = connection.send_command("show interface status")
    print(int_status + "\r\n")
    while True:
        no_shut_config = []
        interface = input("Input interface/port number to enable: ")
        no_shut_config.append("interface {}".format(interface))
        no_shut_config.append(" no shut")
        "\n".join(no_shut_config)
        output = connection.send_config_set(no_shut_config)
        if '% Invalid input detected' in output:  # If a typo, or non-existent port, restart function
            print('\r\nInvalid input detected, choose another port')
            port_enable()
        log_file.write('\r\nPort {} has been enabled'.format(interface))
        while True:
            continue_on = input("Enable another interface [y|n]? ")
            if continue_on == "y":
                break
            elif continue_on == "n":
                print("Returning to main menu" + "\r\n")
                connection.send_command("wr mem")
                connection.disconnect()
                main()
                break
            else:
                print('Type either "y" or "n"')


def port_description():
    # Same concept as port_enable(), except can simply add a description to an interface
    print("\r\nLogging into device and displaying list of interfaces, standby...." + "\r\n")
    connection = device_connect()
    connection.send_command("terminal length 0")
    int_status = connection.send_command("show interface status")
    print(int_status + "\r\n")
    
    while True:
        no_shut_config = []
        interface = input("Input interface/port number to add/change a description on: ")
        description = input('Input a description for the interface: ')
        no_shut_config.append("interface {}".format(interface))
        no_shut_config.append(' description ' + description)
        "\n".join(no_shut_config)
        output = connection.send_config_set(no_shut_config)
        if '% Invalid input detected' in output:  # If a typo, or non-existent port, restart function
            print('\r\nInvalid input detected, choose another port')
            port_description()
        log_file.write('\r\nPort {} had {} added as a description'.format(interface, description))
        while True:
            continue_on = input("Add a description to another interface [y|n]? ")
            if continue_on == "y":
                break
            elif continue_on == "n":
                print("Returning to main menu" + "\r\n")
                connection.send_command("wr mem")
                connection.disconnect()
                main()
                break
            else:
                print('Type either "y" or "n"')


def port_config():
    # Initialize a blank config list, show interface status, then prompt for an interface. If interface is a trunk,
    # alert but allow to continue, or if port is connected to another network device, alert will pop and will return
    # to main menu
    print("\r\nLogging into device, displaying VLANs as well as interfaces, standby...." + "\r\n")
    connection = device_connect()
    interface_config = []
    connection.send_command("terminal length 0")
    vlan_brief = connection.send_command('show vlan brief')
    int_status = connection.send_command("show interface status")
    print("\r\n")
    print(vlan_brief + '\r\n')
    time.sleep(2)
    print(int_status)
    print("\r\n")
    
    # Prompt for interface to configure and then begin to create the config for it
    interface = input("Input interface/port number to configure: ")
    interface_config.append("default interface {}".format(interface))
    interface_config.append("!Previous command defaults the interface to a blank config")
    interface_config.append("interface {}".format(interface))
    config = connection.send_command("show run interface {}".format(interface))
    
    # Check for errors in interface selection, if so, restart port config(). Also, check if port is connected to another
    # cdp neighbor. If so, exit out, if not but port is a trunk, warn that port is a trunk and give option to exit
    if '% Invalid input detected' in config:
        print('\r\nInvalid input detected, choose another port')
        port_config()
    cdp_neighbors = connection.send_command("sh cdp neighbors {}".format(interface))
    cdplines = cdp_neighbors.splitlines()
    for line in cdplines:
        if "your.domain.com" in line:  # Here we'll use domain-name to determine if CDP neighbor
            print("Port is connected to another network device, returning to main menu....")
            connection.disconnect()
            main()
    lines = config.splitlines()
    for config in lines:
        print(config)
        if "switchport mode trunk" in config:
            choice = input("WARNING, port is a trunk; Type 'yes' to continue, else type anything to return: ")
            if choice == "yes":
                print("Continuing with port configuration")
            else:
                print("\r\n" + "Returning to main menu...")
                connection.disconnect()
                main()
    
    # Select what type of port this will be and then open up the proper config file to use
    while True:
        port_type = input("\r\nIs this a user or printer port?" "\r\n1 = user" "\r\n2 = printer"
                          "\r\nInput selection here: ")
        if port_type == "1":
            user_port = open("/path/to/userport.txt", "r")
            voice_vlan = input("Input voice vlan to use | 0 = none: ")
            config_type = user_port
            if voice_vlan is not "0":
                interface_config.append(" switchport voice vlan {}".format(voice_vlan))
            break
        elif port_type == "2":
            printer_port = open("/path/to/printerport.txt", "r")
            config_type = printer_port
            break
        else:
            print("Choose either 1 for a user port or 2 for a printer port")

    # Prompt for access vlan to use as well as description
    vlan = input("Input vlan to use: ")
    description = input("Input port description to use | i.e - User Port #Jack Number: ")

    # Begin to create port config, append some basic points and then read from config file for the rest depending on
    # port type chosen prior
    interface_config.append(" switchport access vlan {}".format(vlan))
    interface_config.append(" description {}".format(description))
    lines = config_type.read().splitlines()
    for line in lines:
        interface_config.append(line)
    "\n".join(interface_config)
    print("\r\nTentative config follows:" + '\r\n')
    print("\n".join(interface_config) + "\r\n")
    while True:
        commit_check = input('Confirm you want to commit port changes [y|n] (no returns to port config menu): ')
        if commit_check == "y":
            connection.send_command("send log 5 Reconfiguring port {}".format(interface))
            connection.send_config_set(interface_config)
            running_config = connection.send_command("show run interface {}".format(interface))
            print("\r\nConfig committed to interface" + "\r\n" + running_config)
            log_file.write('\r\nPort {} has been reconfigured for vlan {} as {}'.format(interface, vlan,
                                                                                              description))
            print("\r\nReturning to main menu...")
            break
        elif commit_check == "n":
            port_config()
            break
        else:
            print('Type either "y" or "n"')
    config_type.close()
    connection.send_command("wr mem")
    connection.disconnect()
    main()


if __name__ == "__main__":
    main()
