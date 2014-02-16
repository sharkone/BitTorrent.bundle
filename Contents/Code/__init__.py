################################################################################
import common
import thepiratebay
import torrent2http
import yts
import watcher

################################################################################
TITLE  = 'BitTorrent'
ART    = 'art-default.jpg'
ICON   = 'icon-default.png'

################################################################################
def Start():
	HTTP.CacheTime         = CACHE_1DAY
	ObjectContainer.art    = R(ART)
	ObjectContainer.title1 = TITLE
	VideoClipObject.art    = R(ART)
	VideoClipObject.thumb  = R(ICON)
	Thread.Create(watcher.thread_proc, watch_directory=torrent2http.get_bin_dir(), timeout=Datetime.Delta(seconds=30))

################################################################################
@handler(common.PREFIX, TITLE)
def Main():
	object_container = ObjectContainer(title2=TITLE)
	object_container.add(DirectoryObject(key=Callback(thepiratebay.menu), title='The Pirate Bay', thumb=R('thepiratebay.png')))
	object_container.add(DirectoryObject(key=Callback(yts.menu), title="YTS", thumb=R('yts.png')))
	object_container.add(PrefsObject(title='Preferences'))
	return object_container
