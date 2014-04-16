################################################################################
import anime_menu
import cherrytorrent_launcher
import movies_menu
import tvshows_menu

import tracking

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

    cherrytorrent_launcher.start_cherrytorrent()

################################################################################
@handler(SharedCodeService.common.PREFIX, TITLE, thumb=ICON, art=ART)
def Main():
    tracking.people_set()
    tracking.track('Started channel')

    Log.Info('Server Platform: {0} ({1})'.format(Platform.OS, Platform.CPU))
    Log.Info('Client Product: {0} ({1})'.format(Client.Product, Client.Platform))
    Log.Info('Channel Version: {0}'.format(SharedCodeService.common.VERSION))

    object_container = ObjectContainer(title2=TITLE)
    object_container.add(DirectoryObject(key=Callback(anime_menu.menu), title='Anime'))
    object_container.add(DirectoryObject(key=Callback(movies_menu.menu), title='Movies'))
    object_container.add(DirectoryObject(key=Callback(tvshows_menu.menu), title='TV Shows'))
    object_container.add(PrefsObject(title='Preferences'))
    return object_container
