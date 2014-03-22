################################################################################
import movies_menu
import yts_menu

################################################################################
TITLE  = 'BitTorrent'
ART    = 'art-default.jpg'
ICON   = 'icon-default.png'

################################################################################
def Start():
	DirectoryObject.thumb  = R(ICON)
	ObjectContainer.art    = R(ART)
	ObjectContainer.title1 = TITLE
	VideoClipObject.art    = R(ART)
	VideoClipObject.thumb  = R(ICON)

################################################################################
@handler(SharedCodeService.common.PREFIX, TITLE, thumb=ICON, art=ART)
def Main():
	Log.Info('Server Platform: {0} ({1})'.format(Platform.OS, Platform.CPU))
	Log.Info('Client Platform: {0}'.format(Client.Platform))

	object_container = ObjectContainer(title2=TITLE)

	if Platform.OS not in ('Linux', 'MacOSX', 'Windows'):
		object_container.header  = 'Not supported'
		object_container.message = 'The {0} channel is not supported on {1} servers.'.format(TITLE, Platform.OS)
	else:
		object_container.add(DirectoryObject(key=Callback(movies_menu.menu), title='Movies'))
		object_container.add(DirectoryObject(key=Callback(yts_menu.menu), title="YTS", thumb=R('yts.png')))
		object_container.add(PrefsObject(title='Preferences'))

	return object_container
