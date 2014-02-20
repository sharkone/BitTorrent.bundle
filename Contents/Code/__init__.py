################################################################################
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
	object_container = ObjectContainer(title2=TITLE)
	object_container.add(DirectoryObject(key=Callback(thepiratebay_menu.menu), title='The Pirate Bay', thumb=R('thepiratebay.png')))
	object_container.add(DirectoryObject(key=Callback(yts_menu.menu), title="YTS", thumb=R('yts.png')))
	object_container.add(PrefsObject(title='Preferences'))
	return object_container
