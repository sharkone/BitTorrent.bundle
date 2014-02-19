###############################################################################
import common
import os
import socket
import subprocess

###############################################################################
def start_torrent(url, magnet):
	try:
		port = start_torrent2http(url, magnet)
		
		status_json = JSON.ObjectFromURL(get_url(port, 'status'), cacheTime=0, timeout=300)
			
		if int(status_json['state']) >= 3:
			ls_json      = JSON.ObjectFromURL(get_url(port, 'ls'), cacheTime=0, timeout=300)
			biggest_file = get_biggest_video_file(ls_json['files'])
			
			complete_pieces = biggest_file['complete_pieces']
			total_pieces    = biggest_file['total_pieces']
			pieces_ratio    = (float(complete_pieces) / float(total_pieces)) * 100.0
			if pieces_ratio > 0.5:
				file_url = get_url(port, 'files/') + String.Quote(biggest_file['name'])
				return IndirectResponse(VideoClipObject, key=file_url)
			else:
				Log.Info('[BitTorrent][torrent2http][{0}] Not enough pieces yet: {1}/{2} -> {3}% @ {4} kb/s'.format(port, complete_pieces, total_pieces, pieces_ratio, status_json['download_rate']))
		else:
			Log.Info('[BitTorrent][torrent2http][{0}] Not ready yet: {1}'.format(port, status_json['state']))
			
	except Exception as exception:
		Log.Error('[BitTorrent][torrent2http] Unhandled exception: {0}'.format(exception))

	Thread.Sleep(2)
	return IndirectResponse(VideoClipObject, key=Callback(common.play_torrent, url=url, magnet=magnet))

###############################################################################
def start_torrent2http(url, magnet):
	port_instance = get_port_instance(url)
	if port_instance[1]:
		Log.Info('[BitTorrent][torrent2http][{0}] Found running instance'.format(port_instance[0]))
	else:
		Log.Info('[BitTorrent][torrent2http][{0}] Starting new instance'.format(port_instance[0]))
		set_port_instance(url, port_instance[0])

		env = os.environ.copy()
		if Platform.OS == 'MacOSX':
			env['DYLD_LIBRARY_PATH'] = get_exec_dir()

		command = '\"{0}\" -bind=\":{1}\" -keep={2} -dlpath=\"{3}\" -dlrate={4} -ulrate={5} -max-idle={6} -uri=\"{7}\"'.format(get_exec_path(), port_instance[0], Prefs['KEEP_FILES'], Prefs['DOWNLOAD_DIR'], Prefs['MAX_DOWNLOAD_RATE'], Prefs['MAX_UPLOAD_RATE'], 30, magnet)
		subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

	return port_instance[0]

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
	Log.Error('[BitTorrent][torrent2http] Unsupported OS: {0}'.format(Platform.OS))

###############################################################################
def get_exec_path():
	if Platform.OS == 'Windows':
		return os.path.join(get_exec_dir(), 'torrent2http.exe')
	elif Platform.OS == 'MacOSX':
		return os.path.join(get_exec_dir(), 'torrent2http')
	Log.Error('[BitTorrent][torrent2http] Unsupported OS: {0}'.format(Platform.OS))

###############################################################################
def set_port_instance(url, port):
	if not Dict['instances']:
		Dict['instances'] = {}
	Dict['instances'][url] = port
	Dict.Save()

###############################################################################
def get_port_instance(url):
	if Dict['instances']:
		if url in Dict['instances']:
			port = Dict['instances'][url]
			if is_instance_running(port):
				return (port, True)
			else:
				Log.Error('[BitTorrent][torrent2http][{0}][get_port_instance] Removing zombie instance'.format(port))
				del Dict['instances'][url]
				Dict.Save()

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('', 0))
	downloader_port = s.getsockname()[1]
	s.close()
	return (downloader_port, False) 	

###############################################################################
def is_instance_running(port):
	try:
		status_json = JSON.ObjectFromURL(get_url(port, 'status'), cacheTime=0, timeout=5)
		return True
	except Exception as exception:
		return False
