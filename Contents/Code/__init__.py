################################################################################
import kickasstorrents_menu
import thepiratebay_menu
import yts_menu

################################################################################
TITLE  = 'BitTorrent'
ART    = 'art-default.jpg'
ICON   = 'icon-default.png'

################################################################################
def Start():
	ObjectContainer.art    = R(ART)
	ObjectContainer.title1 = TITLE
	VideoClipObject.art    = R(ART)
	VideoClipObject.thumb  = R(ICON)

################################################################################
@handler(SharedCodeService.common.PREFIX, TITLE)
def Main():
	Log.Info('Server Platform: {0} ({1})'.format(Platform.OS, Platform.CPU))
	Log.Info('Client Platform: {0}'.format(Client.Platform))

	object_container = ObjectContainer(title2=TITLE)

	if Platform.OS not in ('MacOSX', 'Windows'):
		object_container.header  = 'Not supported'
		object_container.message = 'The {0} channel is not supported on {1} servers.'.format(TITLE, Platform.OS)
	else:
		object_container.add(DirectoryObject(key=Callback(kickasstorrents_menu.menu), title='KickassTorrents', thumb=R('kickasstorrents.png')))
		object_container.add(DirectoryObject(key=Callback(thepiratebay_menu.menu), title='The Pirate Bay', thumb=R('thepiratebay.png')))
		object_container.add(DirectoryObject(key=Callback(yts_menu.menu), title="YTS", thumb=R('yts.png')))
		object_container.add(PrefsObject(title='Preferences'))

	return object_container
