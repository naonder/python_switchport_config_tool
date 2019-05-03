#!/usr/bin/env python3
import base_connection, port_config_menu
import time
import getpass
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


class Config:

    def __init__(self):
        self.device = input('Input address or hostname of device to connect to: ')
        self.connect = base_connection.connector(self.device)
        self.username = getpass.getuser()

    def port_enable(self):
        # Allows user to enable a port
        print("\r\nDisplaying list of interfaces..." + "\r\n")
        self.connect.send_command("terminal length 0")
        int_status = self.connect.send_command("show interface status")
        print(int_status + "\r\n")
        while True:
            no_shut_config = []
            interface = input("Input interface/port number to enable: ")
            no_shut_config.append("interface {}".format(interface))
            no_shut_config.append(" shut")
            no_shut_config.append(" no shut")
            "\n".join(no_shut_config)
            output = self.connect.send_config_set(no_shut_config)
            if '% Invalid input detected' in output:
                print('\r\nSelected port not found!')
                Config.port_enable(self)
            while True:
                continue_on = input("Enable another interface [y|n]? ")
                if continue_on.lower() == "y":
                    break
                elif continue_on.lower() == "n":
                    print("Returning to main menu" + "\r\n")
                    self.connect.send_command("wr mem")
                    self.connect.disconnect()
                    port_config_menu.main_menu()
                else:
                    print('Type either "y" or "n"')

    def port_description(self):
        # Same concept as port_enable(), except can simply add a description to an interface
        print("\r\nDisplaying list of interfaces..." + "\r\n")
        self.connect.send_command("terminal length 0")
        int_status = self.connect.send_command("show interface status")
        print(int_status + "\r\n")

        while True:
            desc_config = []
            interface = input("Input interface/port number to add/change a description on: ")
            description = input('Input a description for the interface: ')
            desc_config.append("interface {}".format(interface))
            desc_config.append(' description ' + description)
            "\n".join(desc_config)
            output = self.connect.send_config_set(desc_config)
            if '% Invalid input detected' in output:
                print('\r\nSelected port not found!')
                Config.port_description(self)
            while True:
                continue_on = input("Add a description to another interface [y|n]? ")
                if continue_on.lower() == "y":
                    break
                elif continue_on.lower() == "n":
                    print("\r\nReturning to main menu" + "\r\n")
                    self.connect.send_command("wr mem")
                    self.connect.disconnect()
                    port_config_menu.main_menu()
                    break
                else:
                    print('\r\nType either "y" or "n"')

    def port_config(self):
        # Initialize a blank config list, show interface status, then prompt for an interface. If interface is a trunk,
        # alert but allow to continue, or if port is connected to another network device, alert will pop and will return
        # to main menu
        print("\r\nDisplaying VLANs as well as interfaces...." + "\r\n")
        interface_config = []
        self.connect.send_command("terminal length 0")
        vlan_brief = self.connect.send_command('show vlan brief')
        int_status = self.connect.send_command("show interface status")
        print("\r\n")
        vlan_lines = vlan_brief.splitlines()[3:]
        skips = ['Fa', 'Gi', 'Te', 'Ge']
        for line in vlan_lines:
            try:
                vlan_num, vlan = line.split()[0], line.split()[1]
                if not any(word in vlan_num for word in skips):
                    print(vlan_num, vlan)
            except IndexError:
                pass
        time.sleep(2)
        print(int_status)
        print("\r\n")

        # Prompt for interface to configure and then begin to create the config for it
        interface = input("Input interface/port number to configure: ")
        interface_config.append("default interface {}".format(interface))
        interface_config.append("!Previous command defaults the interface to a blank config")
        interface_config.append("interface {}".format(interface))
        interface_config.append(' switchport')
        config = self.connect.send_command("show run interface {}".format(interface))

        '''Check for errors in interface selection, if so, restart port config(). 
        Also, check if port is connected to another cdp neighbor. 
        If so, exit out, if not but port is a trunk, warn that port is a trunk and give option to exit'''
        if '% Invalid input detected' in config:
            print('\r\nInvalid input detected, choose another port')
            Config.port_config(self)
        cdp_neighbors = self.connect.send_command("sh cdp neighbors {}".format(interface))
        cdplines = cdp_neighbors.splitlines()
        cdp_entry = ['NSW', 'NRT', 'nsw', 'nrt', 'rtn', 'RTN']  # Change these as needed
        for line in cdplines:
            if any(word in line for word in cdp_entry):
                print("\r\nPort is connected to another network device, returning to device menu....")
                port_config_menu.main_menu()

        lines = config.splitlines()
        for config in lines:
            print(config)
            if "switchport mode trunk" in config:
                choice = input("WARNING, port is a trunk; Type 'yes' to continue, else type anything to return: ")
                if choice == "yes":
                    print("Continuing with port configuration")
                else:
                    print("\r\n" + "Returning to device menu...")

        # Select what type of port this will be and then open up the proper config file to use
        while True:
            port_type = input("\r\nIs this a user or printer port?" "\r\n1 = user" "\r\n2 = printer" '\r\n3 = camera'
                              "\r\nInput selection here: ")
            if port_type == "1":
                config_type = open("/path/to/config/userport.txt", "r")
                voice_vlan = input("\r\nInput voice vlan to use | 0 = none: ")
                switchport_type = 'user'
                if voice_vlan is not "0":
                    interface_config.append(" switchport voice vlan {}".format(voice_vlan))
                break
            elif port_type == "2":
                config_type = open("/path/to/config/printerport.txt", "r")
                switchport_type = 'printer'
                break
            elif port_type == '3':
                config_type = open('/path/to/config/cameraport.txt', 'r')
                switchport_type = 'camera'
                break
            else:
                print("Choose either 1 for a user port or 2 for a printer port")

        # Prompt for access vlan to use as well as description
        vlan = input("\r\nInput vlan to use: ")
        description = input("\r\nInput port description to use | i.e - User Port #Jack Number: ")

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
            commit_check = input('\r\nConfirm you want to commit port changes [y|n] (no returns to port config menu): ')
            if commit_check.lower() == "y":
                self.connect.send_command("send log 5 {} reconfigured port {}".format(self.username, interface))
                self.connect.send_command("send log 5 {} is now a {} port in vlan {}".format(interface,
                                                                                             switchport_type, vlan))
                self.connect.send_config_set(interface_config)
                running_config = self.connect.send_command("show run interface {}".format(interface))
                print("\r\nConfig committed to interface" + "\r\n" + running_config)
                self.send_to_teams(interface, vlan, switchport_type, self.username, self.device)
                print("\r\nReturning to device menu...")
                break
            elif commit_check.lower() == "n":
                Config.port_config(self)
                break
            else:
                print('\r\nType either "y" or "n"')
        config_type.close()
        self.connect.send_command("wr mem")
        self.connect.disconnect()
        port_config_menu.main_menu()

    def send_to_teams(self, interface, vlan, type, user, device): # Will send alert to specified space in Teams
        teams_webhook_url = 'https://api.ciscospark.com/v1/webhooks/incoming/yoururlhere'
        headers = {'Content-Type': 'application/json'}
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        payload = {'markdown': '***Port config change completed***<br> **User:** {}<br> **Device:** {}<br> '
                               '**Interface:** {}<br> **Type:** {}<br> **VLAN:** {}<br>'.format(user, device,
                                                                                                interface, type, vlan)}
        requests.post(teams_webhook_url, headers=headers, verify=False, json=payload)



