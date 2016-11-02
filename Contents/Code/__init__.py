################################################################################
import movies_menu
import troubleshooting_menu
import tvshows_menu

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

    Log.Info('============================================')
    Log.Info('Server:')
    Log.Info(' - OS:        {0}'.format(Platform.OS))
    Log.Info(' - CPU:       {0}'.format(Platform.CPU))
    Log.Info('--------------------------------------------')
    Log.Info('Channel:')
    Log.Info(' - Version: {0}'.format(SharedCodeService.common.VERSION))
    Log.Info('--------------------------------------------')
    Log.Info('Preferences:')
    Log.Info(' - Scrapmagnet version:     {0}'.format(Prefs['SCRAPMAGNET_VERSION']))
    Log.Info(' - Keep files:              {0}'.format(Prefs['KEEP_FILES']))
    Log.Info(' - Movies download dir:     {0}'.format(Prefs['MOVIES_DOWNLOAD_DIR']))
    Log.Info(' - TV shows download dir:   {0}'.format(Prefs['TVSHOWS_DOWNLOAD_DIR']))
    Log.Info('============================================')

    SharedCodeService.scrapmagnet.THREAD_CREATE = Thread.Create
    SharedCodeService.scrapmagnet.stop()
    SharedCodeService.scrapmagnet.start()

################################################################################
@handler(SharedCodeService.common.PREFIX, TITLE, thumb=ICON, art=ART)
def Main():
    Log.Info('============================================')
    Log.Info('Client:')
    Log.Info(' - Product:  {0}'.format(Client.Product))
    Log.Info(' - Platform: {0}'.format(Client.Platform))
    Log.Info('============================================')

    object_container = ObjectContainer(title2=TITLE)

    object_container.add(DirectoryObject(key=Callback(movies_menu.menu), title='Movies', summary='Browse movies.'))
    object_container.add(DirectoryObject(key=Callback(tvshows_menu.menu), title='TV Shows', summary="Browse TV shows."))
    object_container.add(PrefsObject(title='Preferences', summary='Preferences for BitTorrent channel.'))
    object_container.add(DirectoryObject(key=Callback(troubleshooting_menu.menu, title='Troubleshooting'), title='Troubleshooting', summary='Troubleshoot BitTorrent channel.', thumb=troubleshooting_menu.get_menu_thumb()))

    return object_container

################################################################################
def ValidatePrefs():
    SharedCodeService.scrapmagnet.stop()
    SharedCodeService.scrapmagnet.start()
