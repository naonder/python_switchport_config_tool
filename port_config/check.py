#!/usr/bin/env python3
import base_connection, port_config_menu


class Check:
	def __init__(self):
		self.device = input('Input address or hostname of device to connect to: ')
		self.connect = base_connection.connector(self.device)

	def check_config(self):
		# Will show interface status followed by prompt to show running config of a port
		print("\r\nDisplaying list of interfaces..." + "\r\n")
		self.connect.send_command("terminal length 0")
		int_status = self.connect.send_command("show interface status")
		print(int_status + "\r\n")
		while True:
			interface = input("\r\nInput interface/port number to check: ")
			config = self.connect.send_command("show run interface {}".format(interface))
			print(config + "\r\n")
			while True:
				continue_on = input("Check another interface [y|n]? ")
				if continue_on.lower() == "y":
					break
				elif continue_on.lower() == "n":
					print("\r\nReturning to main menu" + "\r\n")
					self.connect.disconnect()
					port_config_menu.main_menu()
				else:
					print('Type either "y" or "n"')

	def get_ip_mac_address(self):
		# Intent is to resolve ARP entry for either MAC or IP address
		while True:
			address = input('\r\nInput MAC or IP address to resolve: ')
			ip_default = self.connect.send_command('sh run | i ip default-gateway')
			try:
				gateway = ip_default.split()[-1]
				print('\r\nAttempting to log into default gateway of device/host....')
				self.connect = base_connection.connector(gateway)
			except IndexError:
				pass
			entry = self.connect.send_command('sh ip arp {} | i Internet'.format(address))
			if not entry:
				print('\r\nAddress has no record of resolution')
			else:
				try:
					ip, mac = entry.split()[1], entry.split()[3]
					if 'Incomplete' in mac:
						print('\r\n{} currently has no known entry. Status is {}'.format(ip, mac))
					else:
						print('\r\nIP address {} resolves to MAC address {}'.format(ip, mac))
				except IndexError:
					print('\r\nError with address resolution')
					pass
			while True:
				continue_on = input("\r\nCheck for another address [y|n]? ")
				if continue_on.lower() == "y":
					break
				elif continue_on.lower() == "n":
					print("\r\nReturning to main menu" + "\r\n")
					self.connect.disconnect()
					port_config_menu.main_menu()
				else:
					print('\r\nType either "y" or "n"')
