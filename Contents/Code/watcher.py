###############################################################################
import os
import subprocess
import time
import torrent2http
import urllib2

###############################################################################
WATCHER_INSTANCE_RUNNING = False

###############################################################################
def thread_proc(watch_directory, timeout):
	port_checker = Watcher(watch_directory, timeout)
	port_checker.run()

###############################################################################
class Watcher:
	###########################################################################
	class Port:
		#######################################################################
		def __init__(self, port_number, timeout):
			self.number               = port_number
			self.timeout              = timeout
			self.last_connection_time = Datetime.Now()
			self.is_cancelable        = False

		#######################################################################
		def check(self):
			if not self.is_cancelable:
				self.is_cancelable = torrent2http.is_cancelable(self.number)
			
			if not self.is_cancelable or self.has_connections():
				# Update timestamp
				self.last_connection_time = Datetime.Now()
			else:
				# Wait for timeout
				if (Datetime.Now() - self.last_connection_time) > self.timeout:
					return False

			return True

		#######################################################################
		def has_connections(self):
			if Platform.OS == 'Windows':
				return self.has_connections_windows()
			elif Platform.OS == 'MacOSX':
				return self.has_connections_macosx()
			Log.Error('[BitTorrent][Watcher] Unsupported OS: {0}'.format(Platform.OS))
			return False

		#######################################################################
		def has_connections_windows(self):
			process              = subprocess.Popen('C:\\Windows\\System32\\NETSTAT.EXE -an', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			process_output       = process.communicate()
			process_output_lines = process_output[0].splitlines()
			
			for line in process_output_lines:
				if ':{0}'.format(self.number) in line:
					words = line.split()
					if ':{0}'.format(self.number) in words[1]:
						if 'ESTABLISHED' in words[3]:
							return True
			return False

		#######################################################################
		def has_connections_macosx(self):
			try:
				process_command      = ['/usr/sbin/lsof', '-n', '-i4TCP']
				process              = subprocess.Popen(process_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				process_output       = process.communicate()
				process_output_lines = process_output[0].splitlines()

				for line in process_output_lines:
					if ':{0}->'.format(self.number) in line:
						if '(ESTABLISHED)' in line:
							return True
			except Exception as exception:
				Log.Error('[BitTorrent][Watcher][has_connections_macosx] Unhandled exception: {0}'.format(exception))

			return False

	###########################################################################
	def __init__(self, watch_directory, timeout):
		self.watch_directory = watch_directory
		self.timeout         = timeout
		self.ports           = []

	###########################################################################
	def run(self):
		try:
			global WATCHER_INSTANCE_RUNNING
		
			if not WATCHER_INSTANCE_RUNNING:
				WATCHER_INSTANCE_RUNNING = True
				Log.Info('[BitTorrent][Watcher] Watching ' + self.watch_directory)
				while True:
					self.update()
					time.sleep(5)
				WATCHER_INSTANCE_RUNNING = False
		except Exception as exception:
			Log.Error('[BitTorrent][Watcher] Unhandled exception: {0}'.format(exception))

	###########################################################################
	def update(self):
		# Find new ports to check
		file_names = os.listdir(self.watch_directory)
		for file_name in file_names:
			file_path = os.path.join(self.watch_directory, file_name)
			if os.path.isfile(file_path) and file_name.isdigit():
				port_number = int(file_name)
				if not self.is_watching_port(port_number):
					Log.Info('[BitTorrent][Watcher][{0}] Adding to watch list'.format(port_number))
					self.ports.append(self.Port(port_number, self.timeout))
		# Check ports
		useless_ports = []
		for port in self.ports:
			if port.check():
				Log.Info('[BitTorrent][Watcher][{0}] Active'.format(port.number))
			else:
				Log.Info('[BitTorrent][Watcher][{0}] Inactive'.format(port.number))
				self.shutdown(port.number)
				os.remove(os.path.join(self.watch_directory, str(port.number)))
				useless_ports.append(port)
				Log.Info('[BitTorrent][Watcher][{0}] Removing from watch list'.format(port.number))
		# Remove useless ports
		for port in useless_ports:
			self.ports.remove(port)

	###########################################################################
	def is_watching_port(self, port_number):
		for port in self.ports:
			if port.number == port_number:
				return True
		return False

	###########################################################################
	def shutdown(self, port_number):
		try:
			torrent2http.shutdown(port_number)
			Log.Info('[BitTorrent][Watcher][{0}] Shutdown successful'.format(port_number))
		except Exception as exception:
			Log.Error('[BitTorrent][Watcher][{0}] Shutdown failed: {1}'.format(port_number, exception))
