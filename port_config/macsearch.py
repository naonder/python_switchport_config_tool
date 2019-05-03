#!/usr/bin/env python3

import base_connection


def mac_search():
    # Get interface where MAC address shows up on
    def mac_trace(mac_address):
        search_mac = connect.send_command('sh mac address-table | i {}'.format(mac_address))
        search_int = search_mac.split()[-1]
        return search_int

    # Check CDP neighbor info to see next device to connect to if necessary
    def get_cdp_neighbor(nei_interface):
        # Check if CDP neighbor is a switch
        cdp_info = connect.send_command('show cdp neighbors {} | i S I'.format(nei_interface))
        if cdp_info:
            # Attempt to grab the neighbor ID as well as the address of it
            neighbor_id = connect.send_command('show cdp neighbors {} det | i Device ID:'.format(nei_interface))
            addresses = connect.send_command('show cdp neighbors {} det | i IP address:'.format(nei_interface))
            try:
                neighbor = neighbor_id.split()[-1]
            except IndexError:
                neighbor = None
                pass
            try:
                address = addresses.splitlines()[0].split()[-1]
            except IndexError:
                address = None
                pass
            return neighbor, address
        else:
            neighbor = None
            address = None
            return neighbor, address

    # If interface is a port-channel, grab last member of channel to check for CDP info
    def get_port_channel_interface(port_channel):
        port_channel_start = port_channel.split()[-1]
        port_channel_members = connect.send_command('show interface {} | i Members'.format(port_channel_start))
        member = port_channel_members.split()[-1]
        return member

    def mac_address_input():
        mac_address = input('\r\nType in MAC address you want to search for (must be 12 hexadecimal characters): ')
        return mac_address

    # Attempt to convert MAC address to an integer in base 16
    # This will verify if characters are hex or not
    def char_validator(validate_mac):
        dividers = '.-: '
        new_mac = ''.join(c for c in validate_mac if c not in dividers)
        try:
            int(new_mac, 16)
            return True
        except ValueError:
            print('\r\nInvalid character detected')
            return None

    # Verify if MAC address is at 12 characters when dividers are removed
    def len_validator(validate_mac):
        dividers = '.-: '
        new_mac = ''.join(c for c in validate_mac if c not in dividers)
        if len(new_mac) != 12:
            print('\r\nMAC address is not the correct length')
            return None
        else:
            return True

    # Once MAC address is verified, this will format it to be 'Cisco' like
    def mac_formatter(unformatted_mac):
        dividers = '.-: '
        new_mac = ''.join(c for c in unformatted_mac if c not in dividers)
        formatted_mac = new_mac.lower()[0:4] + '.' + new_mac.lower()[4:8] + '.' + new_mac.lower()[8:]
        return formatted_mac

    device_address = input('Input address or hostname of device to connect to: ')
    first_device_address = device_address

    # Will pass MAC address in various methods to determine if valid
    while True:
        check_mac = mac_address_input()
        if not char_validator(check_mac):
            print('Input a valid MAC address...')
        elif not len_validator(check_mac):
            print('Input a valid MAC address...')
        else:
            mac = mac_formatter(check_mac)
            break

    # Will start searching for a MAC address using first host provided
    print('\r\nSearching for MAC address {}, standby...'.format(mac))
    next_device = [first_device_address]
    next_device_name = [first_device_address]  # Used only for showing name of device when address is found

    search = 1
    # Loop through devices while searching for the address
    while search == 1:
        for device in next_device:
            connect = base_connection.connector(device)
            try:
                interface = mac_trace(mac)
                if 'Po' in interface:  # If interface is a port-channel, will attempt to grab CDP info on member link
                    neighbor_interface = get_port_channel_interface(interface)
                    new_device_name, addy = get_cdp_neighbor(neighbor_interface)
                    next_device[0] = addy  # Set next_device to CDP neighbor to log into next
                    next_device_name[0] = new_device_name  # Set name to display next switch we'll connect to
                    print('\r\nAddress is not on {}, will check on {}...'.format(device, new_device_name))
                    connect.disconnect()
                else:
                    new_device, addy = get_cdp_neighbor(interface)
                    if not new_device and not addy:  # If CDP info is blank, address should be on this interface
                        print('\r\nMAC address is on device {} attached to interface {}'.format
                              (next_device_name[0], interface))
                        connect.disconnect()
                        print('\r\nReturning to Main Menu....')
                        search = 0
                    else:
                        new_device_name, addy = get_cdp_neighbor(interface)
                        next_device[0] = addy  # Set next_device to CDP neighbor to log into next
                        next_device_name[0] = new_device_name  # Set name to display next switch we'll connect to
                        print('\r\nAddress is not on {}, will check on {}...'.format(device, new_device_name))
                        connect.disconnect()

            # If issue is that MAC address isn't found, will display a note and close out
            except IndexError:
                print('\r\nAddress not detected, try again later or make sure correct MAC address has been entered')
                print(
                    '\r\n***Note that this does not mean the device is not plugged in. It just means the switch has not'
                    ' seen the device yet or in the recent past***')
                connect.disconnect()
                print('\r\nReturning to Main Menu....')
                search = 0


if __name__ == '__main__':
    mac_search()
