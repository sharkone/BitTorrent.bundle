################################################################################
import updater

################################################################################
@route(SharedCodeService.common.PREFIX + '/about')
def menu(title):
    object_container = ObjectContainer(title2=title)

    # Channel Version
    version_result, version_result_str, version_result_summary = test_version()
    object_container.add(DirectoryObject(key=Callback(updater.update), title='Channel version: {0}'.format(version_result_str), summary=version_result_summary, thumb=get_test_thumb(version_result)))

    # Scrapyard
    scrapyard_result, scrapyard_result_str, scrapyard_result_summary = test_scrapyard()
    object_container.add(DirectoryObject(key=Callback(empty_menu), title='Scrapyard server: {0}'.format(scrapyard_result_str), summary=scrapyard_result_summary, thumb=get_test_thumb(scrapyard_result)))

    # Scrapmagnet
    scrapmagnet_result, scrapmagnet_result_str, scrapmagnet_result_summary = test_scrapmagnet()
    object_container.add(DirectoryObject(key=Callback(empty_menu), title='Scrapmagnet: {0}'.format(scrapmagnet_result_str), summary=scrapmagnet_result_summary, thumb=get_test_thumb(scrapmagnet_result)))

    # Local IP
    local_ip_result, local_ip_result_str, local_ip_result_summary = test_local_ip()
    object_container.add(DirectoryObject(key=Callback(empty_menu), title='Local IP: {0}'.format(local_ip_result_str), summary=local_ip_result_summary, thumb=get_test_thumb(local_ip_result)))

    # Public IP
    public_ip_result, public_ip_result_str, public_ip_result_summary = test_public_ip()
    object_container.add(DirectoryObject(key=Callback(empty_menu), title='Public IP: {0}'.format(public_ip_result_str), summary=public_ip_result_summary, thumb=get_test_thumb(public_ip_result)))

    # Torrent Proxy
    torrent_proxy_result, torrent_proxy_result_str, torrent_proxy_result_summary = test_torrent_proxy()
    object_container.add(DirectoryObject(key=Callback(empty_menu), title='Torrent Proxy: {0}'.format(torrent_proxy_result_str), summary=torrent_proxy_result_summary, thumb=get_test_thumb(torrent_proxy_result)))

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/empty')
def empty_menu():
    object_container = ObjectContainer(title2='Empty')
    return object_container

################################################################################
def get_menu_thumb():
    result, _, _ = test_version()
    if result != True:
        return get_test_thumb(result)

    result, _, _ = test_scrapyard()
    if result != True:
        return get_test_thumb(result)

    result, _, _ = test_scrapmagnet()
    if result != True:
        return get_test_thumb(result)

    result, _, _ = test_local_ip()
    if result != True:
        return get_test_thumb(result)

    result, _, _ = test_public_ip()
    if result != True:
        return get_test_thumb(result)

    result, _, _ = test_torrent_proxy()
    if result != True:
        return get_test_thumb(result)

    return get_test_thumb(True)

################################################################################
def get_test_thumb(result):
    if result == True:
        return R('ok.png')
    elif result == 'Warning':
        return R('warning.png')
    elif result == 'Update`':
        return R('update.png')
    elif result == False:
        return R('error.png')

################################################################################
def test_version():
    update_available, latest_version = updater.update_available()
    if not update_available:
        result         = True
        result_str     = SharedCodeService.common.VERSION
        result_summary = 'Running latest version.'
    else:
        result         = 'Update'
        result_str     = SharedCodeService.common.VERSION + ' ({0} available)'.format(latest_version)
        result_summary = 'Click to update to latest version.'
    return (result, result_str, result_summary)

################################################################################
def test_scrapyard():
    result         = True
    result_str     = 'Available'
    result_summary =  Prefs['SCRAPYARD_URL'] + ' is available.'

    try:
        HTML.ElementFromURL(Prefs['SCRAPYARD_URL'] + '/api/movies/trending?page=1', timeout=5)
    except:
        result         = True
        result_str     = 'Unavailable'
        result_summary =  Prefs['SCRAPYARD_URL'] + ' is unavailable, check URL the in Preferences.'

    return (result, result_str, result_summary)

################################################################################
def test_scrapmagnet():
    result         = True
    result_str     = 'Running'
    result_summary = 'Scrapmagnet is running correctly.'

    if not SharedCodeService.scrapmagnet.is_running():
        result         = False
        result_str     = 'ERROR'
        result_summary = 'Scrapmagnet is not running.'
    elif not SharedCodeService.scrapmagnet.is_incoming_port_open():
        result         = 'Warning'
        result_str     = 'WARNING'
        result_summary = 'Scrapmagnet incoming port ({0}) is not visible from the Internet. Transfer speeds won\'t be optimal.'.format(Prefs['INCOMING_PORT'])

    return (result, result_str, result_summary)

################################################################################
def test_local_ip():
    local_ip = SharedCodeService.utils.get_local_host()
    if local_ip:
        result         = True
        result_str     = local_ip
        result_summary = 'Local IP is properly determined.'
    else:
        result         = False
        result_str     = 'ERROR'
        result_summary = 'Unable to determine local IP.'

    return (result, result_str, result_summary)

################################################################################
def test_public_ip():
    public_ip = Network.PublicAddress
    if public_ip:
        result         = True
        result_str     = public_ip
        result_summary = 'Public IP is properly determined.'
    else:
        result         = False
        result_str     = 'ERROR'
        result_summary = 'Unable to determine public IP.'

    return (result, result_str, result_summary)

################################################################################
def test_torrent_proxy():
    if Prefs['TORRENT_PROXY_TYPE'] == 'None':
        result         = True
        result_str     = 'Unused'
        result_summary = 'No torrent proxy set.'
    else:
        result         = True
        result_str     = '{0}:{1}'.format(Prefs['TORRENT_PROXY_HOST'], Prefs['TORRENT_PROXY_PORT'])
        result_summary = 'Torrent proxy is working properly.'

        try:
            SharedCodeService.utils.try_connection()
        except Exception as exception:
            result         = False
            result_str     = 'ERROR'
            result_summary = 'Torrent proxy is not working properly: {0}'.format(exception)

    return (result, result_str, result_summary)
