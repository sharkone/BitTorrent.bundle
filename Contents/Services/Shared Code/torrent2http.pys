###############################################################################
import os
import socket
import subprocess

###############################################################################
def start_torrent(url, magnet):
	try:
		port     = start_torrent2http(url, magnet)
		json_url = get_url(port, 'ls')
		json 	 = JSON.ObjectFromURL(json_url, cacheTime=0, timeout=300)
		file 	 = get_biggest_video_file(json['files'])
		file_url = get_url(port, 'files/') + String.Quote(file['name'])
		return IndirectResponse(VideoClipObject, key=file_url)
	except Exception as exception:
		Log.Error('[BitTorrent] [torrent2http] Unhandled exception: {0}'.format(exception))

###############################################################################
def start_torrent2http(url, magnet):
	downloader_port    = 5001
	downloader_running = False
	
	for file_name in os.listdir(get_bin_dir()):
		file_path = os.path.join(get_bin_dir(), file_name)
		if os.path.isfile(file_path) and file_name.isdigit():
			file_fd 	 = os.open(file_path, os.O_RDONLY)
			file_content = os.read(file_fd, 1024)
			os.close(file_fd)
			if file_content == url:
				Log.Info('[BitTorrent][torrent2http] Found port file: {0}'.format(file_path))
				downloader_port    = int(file_name)
				downloader_running = True
				break

	if not downloader_running:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(('', 0))
		downloader_port = s.getsockname()[1]
		s.close()

		downloader_port_file = os.path.join(get_bin_dir(), str(downloader_port))
		Log.Info('[BitTorrent][torrent2http] Writing port file: {0}'.format(downloader_port_file))
		
		downloader_port_fd   = os.open(downloader_port_file, os.O_CREAT | os.O_RDWR)
		os.write(downloader_port_fd, url)
		os.close(downloader_port_fd)

		env = os.environ.copy()
		if Platform.OS == 'MacOSX':
			env['DYLD_LIBRARY_PATH'] = get_exec_dir()

		# TODO: Make that look nicer
		command = '\"{0}\" -bind=\":{1}\" -keep={2} -dlpath=\"{3}\" -magnet=\"{4}\"'.format(get_exec_path(), downloader_port, True, get_download_dir(), magnet)
		subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

	return downloader_port

###############################################################################
def get_url(port, page):
	return 'http://' + Network.Address + ':' + str(port) + '/' + page

###############################################################################
def get_biggest_video_file(files):
	biggest_file = None
	for file in files:
		if file['name'].endswith(('.avi', '.mp4', '.mkv')):
			if biggest_file == None or file['size'] > biggest_file['size']:
				biggest_file = file
	return biggest_file

###############################################################################
def get_bin_dir():
	bundle_directory = os.path.join(os.getcwd(), '..', '..', '..', 'Plug-ins', 'BitTorrent.bundle')
	bundle_directory = bundle_directory.replace('\\\\?\\', '')
	return os.path.normpath(os.path.join(bundle_directory, 'Contents', 'Bin'))

###############################################################################
def get_exec_dir():
	if Platform.OS == 'Windows':
		return os.path.join(get_bin_dir(), 'Windows')
	elif Platform.OS == 'MacOSX':
		return os.path.join(get_bin_dir(), 'MacOSX')
	Log.Error('[BitTorrent] [torrent2http] Unsupported OS: {0}'.format(Platform.OS))

###############################################################################
def get_exec_path():
	if Platform.OS == 'Windows':
		return os.path.join(get_exec_dir(), 'torrent2http.exe')
	elif Platform.OS == 'MacOSX':
		return os.path.join(get_exec_dir(), 'torrent2http')
	Log.Error('[BitTorrent] [torrent2http] Unsupported OS: {0}'.format(Platform.OS))

###############################################################################
def get_download_dir():
	return os.path.join(os.path.expanduser("~"), 'Downloads', 'BitTorrent')
