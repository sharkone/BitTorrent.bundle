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
    Log.Info(' - OS:        {0}'.format(Platform.OS))
    Log.Info(' - CPU:       {0}'.format(Platform.CPU))
    Log.Info(' - Local IP:  {0}'.format(SharedCodeService.utils.get_local_host()))
    Log.Info(' - Public IP: {0}'.format(Network.PublicAddress))
    Log.Info('--------------------------------------------')
    Log.Info('Channel:')
    Log.Info(' - Version: {0}'.format(SharedCodeService.common.VERSION))
    Log.Info('--------------------------------------------')
    Log.Info('Preferences:')
    Log.Info(' - Torrent incoming port:   {0}'.format(Prefs['INCOMING_PORT']))
    Log.Info(' - UPnP / NAT-PMP enabled:  {0}'.format(Prefs['UPNP_NATPMP_ENABLED']))
    Log.Info(' - Maximum download rate:   {0}'.format(Prefs['MAX_DOWNLOAD_RATE']))
    Log.Info(' - Maximum upload rate:     {0}'.format(Prefs['MAX_UPLOAD_RATE']))
    Log.Info(' - Keep files:              {0}'.format(Prefs['KEEP_FILES']))
    Log.Info(' - Anime enabled:           {0}'.format(Prefs['ANIME_ENABLED']))
    Log.Info(' - Anime download dir:      {0}'.format(Prefs['ANIME_DOWNLOAD_DIR']))
    Log.Info(' - Movies enabled:          {0}'.format(Prefs['MOVIES_ENABLED']))
    Log.Info(' - Movies download dir:     {0}'.format(Prefs['MOVIES_DOWNLOAD_DIR']))
    Log.Info(' - TV shows enabled:        {0}'.format(Prefs['TVSHOWS_ENABLED']))
    Log.Info(' - TV shows download dir:   {0}'.format(Prefs['TVSHOWS_DOWNLOAD_DIR']))
    Log.Info(' - KickAssTorrents enabled: {0}'.format(Prefs['USE_KICKASSTORRENTS_PROVIDER']))
    Log.Info(' - KickAssTorrents URL:     {0}'.format(Prefs['KICKASSTORRENTS_PROVIDER_URL']))
    Log.Info(' - The Pirate Bay enabled:  {0}'.format(Prefs['USE_THEPIRATEBAY_PROVIDER']))
    Log.Info(' - The Pirate Bay URL:      {0}'.format(Prefs['THEPIRATEBAY_PROVIDER_URL']))
    Log.Info(' - YTS enabled:             {0}'.format(Prefs['USE_YTS_PROVIDER']))
    Log.Info(' - YTS URL:                 {0}'.format(Prefs['YTS_PROVIDER_URL']))
    Log.Info(' - VPN Fix enabled:         {0}'.format(Prefs['VPN_FIX']))
    Log.Info(' - Metadata timeout:        {0}'.format(Prefs['METADATA_TIMEOUT']))
    Log.Info(' - Torrent Proxy type:      {0}'.format(Prefs['TORRENT_PROXY_TYPE']))
    Log.Info(' - Torrent Proxy host:      {0}'.format(Prefs['TORRENT_PROXY_HOST']))
    Log.Info(' - Torrent Proxy port:      {0}'.format(Prefs['TORRENT_PROXY_PORT']))
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

    object_container = ObjectContainer(title2=TITLE)
    
    if Prefs['ANIME_ENABLED']:
        object_container.add(DirectoryObject(key=Callback(anime_menu.menu), title='Anime', summary='Browse anime'))
    
    if Prefs['MOVIES_ENABLED']:
        object_container.add(DirectoryObject(key=Callback(movies_menu.menu), title='Movies', summary='Browse movies'))
    
    if Prefs['TVSHOWS_ENABLED']:
        object_container.add(DirectoryObject(key=Callback(tvshows_menu.menu), title='TV Shows', summary="Browse TV shows"))
    
    object_container.add(PrefsObject(title='Preferences', summary='Preferences for BitTorrent channel'))
    object_container.add(DirectoryObject(key=Callback(about_menu, title='About'), title='About', summary='About BitTorrent channel', thumb=R('about.png')))
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/about')
def about_menu(title):
    object_container = ObjectContainer(title2=title)

    # Channel Version
    object_container.add(DirectoryObject(key=Callback(empty_menu), title='Channel version: {0}'.format(SharedCodeService.common.VERSION), summary='Current version of the BitTorrent channel.'))
    
    # URLService
    url_service_result  = 'Running'
    url_service_summary = 'URLService is running correctly.'
    if not URLService.ServiceIdentifierForURL(Prefs['KICKASSTORRENTS_PROVIDER_URL'] + '/big-buck-bunny-bdrip-xvid-medic-t3434558.html'):
        url_service_result  = 'ERROR'
        url_service_summary = 'URLService is not running correctly, try restarting your server.'
    object_container.add(DirectoryObject(key=Callback(empty_menu), title='URLService: {0}'.format(url_service_result), summary=url_service_summary))

    # KickAssTorrents
    kickasstorrents_result  = 'Available'
    kickasstorrents_summary = Prefs['KICKASSTORRENTS_PROVIDER_URL'] + ' is available.'
    if not Prefs['USE_KICKASSTORRENTS_PROVIDER']:
        kickasstorrents_result  = 'Disabled'
        kickasstorrents_summary = 'KickAssTorrents is disabled in the Preferences.'
    else:
        try:
            HTML.ElementFromURL(Prefs['KICKASSTORRENTS_PROVIDER_URL'], cacheTime=CACHE_1HOUR, timeout=1.0)
        except:
            kickasstorrents_result  = 'Unavailable'
            kickasstorrents_summary = Prefs['KICKASSTORRENTS_PROVIDER_URL'] + ' is unavailable, check URL the in Preferences.'
    object_container.add(DirectoryObject(key=Callback(empty_menu), title='KickAssTorrents Provider: {0}'.format(kickasstorrents_result), summary=kickasstorrents_summary))

    # The Pirate Bay
    thepiratebay_result  = 'Available'
    thepiratebay_summary = Prefs['THEPIRATEBAY_PROVIDER_URL'] + ' is available.'
    if not Prefs['USE_THEPIRATEBAY_PROVIDER']:
        thepiratebay_result  = 'Disabled'
        thepiratebay_summary = 'The Pirate Bay is disabled in the Preferences.'
    else: 
        try:
            HTML.ElementFromURL(Prefs['THEPIRATEBAY_PROVIDER_URL'], cacheTime=CACHE_1HOUR, timeout=1.0)
        except:
            thepiratebay_result  = 'Unavailable'
            thepiratebay_summary = Prefs['THEPIRATEBAY_PROVIDER_URL'] + ' is unavailable, check URL in the Preferences.'
    object_container.add(DirectoryObject(key=Callback(empty_menu), title='The Pirate Bay Provider: {0}'.format(thepiratebay_result), summary=thepiratebay_summary))

    # YTS
    yts_result  = 'Available'
    yts_summary = Prefs['YTS_PROVIDER_URL'] + ' is available.'
    if not Prefs['USE_YTS_PROVIDER']:
        yts_result  = 'Disabled'
        yts_summary = 'YTS is disabled in the Preferences.'
    else: 
        try:
            HTML.ElementFromURL(Prefs['YTS_PROVIDER_URL'], cacheTime=CACHE_1HOUR, timeout=1.0)
        except:
            yts_result  = 'Unavailable'
            yts_summary = Prefs['YTS_PROVIDER_URL'] + ' is unavailable, check URL in the Preferences.'
    object_container.add(DirectoryObject(key=Callback(empty_menu), title='YTS Provider: {0}'.format(yts_result), summary=yts_summary))

    # CherryTorrent
    cherrytorrent_result  = 'Running'
    cherrytorrent_summary = 'CherryTorrent is running correctly.'
    if not SharedCodeService.cherrytorrent.is_running():
        cherrytorrent_result  = 'ERROR'
        cherrytorrent_summary = 'CherryTorrent is not running.'
    object_container.add(DirectoryObject(key=Callback(empty_menu), title='CherryTorrent: {0}'.format(cherrytorrent_result), summary=cherrytorrent_summary))

    # Local IP
    local_ip = SharedCodeService.utils.get_local_host()
    if local_ip:
        local_ip_result  = local_ip
        local_ip_summary = 'Local IP is properly determined.'
    else:
        local_ip_result  = 'ERROR'
        local_ip_summary = 'Unable to determine local IP'
    object_container.add(DirectoryObject(key=Callback(empty_menu), title='Local IP: {0}'.format(local_ip_result), summary=local_ip_summary))

    # Public IP
    public_ip = Network.PublicAddress
    if public_ip:
        public_ip_result  = public_ip
        public_ip_summary = 'Public IP is properly determined.'
    else:
        public_ip_result  = 'ERROR'
        public_ip_summary = 'Unable to determine public IP'
    object_container.add(DirectoryObject(key=Callback(empty_menu), title='Public IP: {0}'.format(public_ip_result), summary=public_ip_summary))
    
    # Torrent Proxy
    if Prefs['TORRENT_PROXY_TYPE'] == 'None':
        torrent_proxy_result  = 'Unused'
        torrent_proxy_summary = 'No torrent proxy set.'
    else:
        torrent_proxy_result  = '{0}:{1}'.format(Prefs['TORRENT_PROXY_HOST'], Prefs['TORRENT_PROXY_PORT'])
        torrent_proxy_summary = 'Torrent proxy is working properly.'

        try:
            SharedCodeService.utils.try_connection()
        except Exception as exception:
            torrent_proxy_result  = 'ERROR'
            torrent_proxy_summary = 'Torrent proxy is not working properly: {0}'.format(exception)
            Log.Error(torrent_proxy_summary)
    object_container.add(DirectoryObject(key=Callback(empty_menu), title='Torrent Proxy: {0}'.format(torrent_proxy_result), summary=torrent_proxy_summary))

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/empty')
def empty_menu():
    object_container = ObjectContainer(title2='Empty')
    return object_container
