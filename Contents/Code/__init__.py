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

    Log.Info('============================================')
    Log.Info('Server:')
    Log.Info(' - OS:  {0}'.format(Platform.OS))
    Log.Info(' - CPU: {0}'.format(Platform.CPU))
    Log.Info('--------------------------------------------')
    Log.Info('Channel:')
    Log.Info(' - Version: {0}'.format(SharedCodeService.common.VERSION))
    Log.Info('--------------------------------------------')
    Log.Info('Preferences:')
    Log.Info(' - Torrent incoming port:   {0}'.format(Prefs['INCOMING_PORT']))
    Log.Info(' - Maximum download rate:   {0}'.format(Prefs['MAX_DOWNLOAD_RATE']))
    Log.Info(' - Maximum upload rate:     {0}'.format(Prefs['MAX_UPLOAD_RATE']))
    Log.Info(' - VPN Fix enabled:         {0}'.format(Prefs['VPN_FIX']))
    Log.Info(' - Keep files:              {0}'.format(Prefs['KEEP_FILES']))
    Log.Info(' - Anime download dir:      {0}'.format(Prefs['ANIME_DOWNLOAD_DIR']))
    Log.Info(' - Movies download dir:     {0}'.format(Prefs['MOVIES_DOWNLOAD_DIR']))
    Log.Info(' - TV shows download dir:   {0}'.format(Prefs['TVSHOWS_DOWNLOAD_DIR']))
    Log.Info(' - KickAssTorrents enabled: {0}'.format(Prefs['USE_KICKASSTORRENTS_PROVIDER']))
    Log.Info(' - KickAssTorrents URL:     {0}'.format(Prefs['KICKASSTORRENTS_PROVIDER_URL']))
    Log.Info(' - The Pirate Bay enabled:  {0}'.format(Prefs['USE_THEPIRATEBAY_PROVIDER']))
    Log.Info(' - The Pirate Bay URL:      {0}'.format(Prefs['THEPIRATEBAY_PROVIDER_URL']))
    Log.Info(' - YTS enabled:             {0}'.format(Prefs['USE_YTS_PROVIDER']))
    Log.Info(' - YTS URL:                 {0}'.format(Prefs['YTS_PROVIDER_URL']))
    Log.Info('============================================')
    
    tracking.people_set()
    cherrytorrent_launcher.start_cherrytorrent()

################################################################################
@handler(SharedCodeService.common.PREFIX, TITLE, thumb=ICON, art=ART)
def Main():
    Log.Info('============================================')
    Log.Info('Client:')
    Log.Info(' - Product:  {0}'.format(Client.Product))
    Log.Info(' - Platform: {0}'.format(Client.Platform))
    Log.Info('============================================')

    tracking.track('/')

    object_container = ObjectContainer(title2=TITLE)
    object_container.add(DirectoryObject(key=Callback(anime_menu.menu), title='Anime', summary='Browse anime'))
    object_container.add(DirectoryObject(key=Callback(movies_menu.menu), title='Movies', summary='Browse movies'))
    object_container.add(DirectoryObject(key=Callback(tvshows_menu.menu), title='TV Shows', summary="Browse TV shows"))
    object_container.add(PrefsObject(title='Preferences', summary='Preferences for BitTorrent channel'))
    object_container.add(DirectoryObject(key=Callback(about_menu), title='About', summary='About BitTorrent channel', thumb=R('about.png')))
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/about')
def about_menu():
    tracking.track('/About')

    object_container = ObjectContainer(title2='About')
    object_container.header  = 'Channel Info'
    object_container.message = 'Channel version: {0}'.format(SharedCodeService.common.VERSION)
    return object_container
