################################################################################
PREFIX = '/video/bittorrent'

################################################################################
import torrent2http

################################################################################
@route(PREFIX + '/play_torrent')
@indirect
def play_torrent(url, magnet):
	return torrent2http.start_torrent(url, magnet)
