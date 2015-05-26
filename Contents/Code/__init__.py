################################################################################
import movies_menu
import tvshows_menu
import updater

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
    Log.Info(' - Scrapyard server URL:    {0}'.format(Prefs['SCRAPYARD_URL']))
    Log.Info(' - Scrapmagnet version:     {0}'.format(Prefs['SCRAPMAGNET_VERSION']))
    Log.Info(' - Torrent incoming port:   {0}'.format(Prefs['INCOMING_PORT']))
    Log.Info(' - UPnP / NAT-PMP enabled:  {0}'.format(Prefs['UPNP_NATPMP_ENABLED']))
    Log.Info(' - Maximum download rate:   {0}'.format(Prefs['MAX_DOWNLOAD_RATE']))
    Log.Info(' - Maximum upload rate:     {0}'.format(Prefs['MAX_UPLOAD_RATE']))
    Log.Info(' - Keep files:              {0}'.format(Prefs['KEEP_FILES']))
    Log.Info(' - Movies download dir:     {0}'.format(Prefs['MOVIES_DOWNLOAD_DIR']))
    Log.Info(' - TV shows download dir:   {0}'.format(Prefs['TVSHOWS_DOWNLOAD_DIR']))
    Log.Info(' - Torrent Proxy type:      {0}'.format(Prefs['TORRENT_PROXY_TYPE']))
    Log.Info(' - Torrent Proxy host:      {0}'.format(Prefs['TORRENT_PROXY_HOST']))
    Log.Info(' - Torrent Proxy port:      {0}'.format(Prefs['TORRENT_PROXY_PORT']))
    Log.Info('============================================')

    SharedCodeService.scrapmagnet.stop()
    Thread.Create(SharedCodeService.scrapmagnet.log_thread_func)
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

    if updater.update_available():
        object_container.add(updater.create_button())

    object_container.add(DirectoryObject(key=Callback(movies_menu.menu), title='Movies', summary='Browse movies.'))
    object_container.add(DirectoryObject(key=Callback(tvshows_menu.menu), title='TV Shows', summary="Browse TV shows."))
    object_container.add(PrefsObject(title='Preferences', summary='Preferences for BitTorrent channel.'))
    object_container.add(DirectoryObject(key=Callback(about_menu, title='About'), title='About', summary='About BitTorrent channel.', thumb=R('about.png')))

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/about')
def about_menu(title):
    object_container = ObjectContainer(title2=title)

    # Channel Version
    object_container.add(DirectoryObject(key=Callback(empty_menu), title='Channel version: {0}'.format(SharedCodeService.common.VERSION), summary='Current version of the BitTorrent channel.'))

    # Scrapyard server
    scrapyard_server_result  = 'Available'
    scrapyard_server_summary = Prefs['SCRAPYARD_URL'] + ' is available.'
    try:
        HTML.ElementFromURL(Prefs['SCRAPYARD_URL'], timeout=5)
    except:
        scrapyard_server_result  = 'Unavailable'
        scrapyard_server_summary = Prefs['SCRAPYARD_URL'] + ' is unavailable, check URL the in Preferences.'
    object_container.add(DirectoryObject(key=Callback(empty_menu), title='Scrapyard server: {0}'.format(scrapyard_server_result), summary=scrapyard_server_summary))

    # Scrapmagnet
    scrapmagnet_result  = 'Running'
    scrapmagnet_summary = 'Scrapmagnet is running correctly.'
    if not SharedCodeService.scrapmagnet.is_running():
        scrapmagnet_result  = 'ERROR'
        scrapmagnet_summary = 'Scrapmagnet is not running.'
    elif not SharedCodeService.scrapmagnet.is_incoming_port_open():
        scrapmagnet_result  = 'WARNING'
        scrapmagnet_summary = 'Scrapmagnet incoming port ({0}) is not visible from the Internet. Transfer speeds won\'t be optimal.'.format(Prefs['INCOMING_PORT'])
    object_container.add(DirectoryObject(key=Callback(empty_menu), title='Scrapmagnet: {0}'.format(scrapmagnet_result), summary=scrapmagnet_summary))

    # Local IP
    local_ip = SharedCodeService.utils.get_local_host()
    if local_ip:
        local_ip_result  = local_ip
        local_ip_summary = 'Local IP is properly determined.'
    else:
        local_ip_result  = 'ERROR'
        local_ip_summary = 'Unable to determine local IP.'
    object_container.add(DirectoryObject(key=Callback(empty_menu), title='Local IP: {0}'.format(local_ip_result), summary=local_ip_summary))

    # Public IP
    public_ip = Network.PublicAddress
    if public_ip:
        public_ip_result  = public_ip
        public_ip_summary = 'Public IP is properly determined.'
    else:
        public_ip_result  = 'ERROR'
        public_ip_summary = 'Unable to determine public IP.'
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
    object_container.add(DirectoryObject(key=Callback(empty_menu), title='Torrent Proxy: {0}'.format(torrent_proxy_result), summary=torrent_proxy_summary))

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/empty')
def empty_menu():
    object_container = ObjectContainer(title2='Empty')
    return object_container
