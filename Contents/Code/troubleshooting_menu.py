################################################################################
import updater

################################################################################
@route(SharedCodeService.common.PREFIX + '/troubleshooting')
def menu(title):
    object_container = ObjectContainer(title2=title)

    # Channel Version
    version_result, version_result_str, version_result_summary = test_version()
    object_container.add(DirectoryObject(key=Callback(empty_menu if version_result == True else updater.update), title='Channel version: {0}'.format(version_result_str), summary=version_result_summary, thumb=get_test_thumb(version_result)))

    # Popcorn API
    popcorn_result, popcorn_result_str, popcorn_result_summary = test_popcorn()
    object_container.add(DirectoryObject(key=Callback(empty_menu), title='Popcorn API: {0}'.format(popcorn_result_str), summary=popcorn_result_summary, thumb=get_test_thumb(popcorn_result)))

    # Scrapmagnet
    scrapmagnet_result, scrapmagnet_result_str, scrapmagnet_result_summary = test_scrapmagnet()
    object_container.add(DirectoryObject(key=Callback(empty_menu), title='Scrapmagnet: {0}'.format(scrapmagnet_result_str), summary=scrapmagnet_result_summary, thumb=get_test_thumb(scrapmagnet_result)))

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

    result, _, _ = test_popcorn()
    if result != True:
        return get_test_thumb(result)

    result, _, _ = test_scrapmagnet()
    if result != True:
        return get_test_thumb(result)

    return get_test_thumb(True)

################################################################################
def get_test_thumb(result):
    if result == True:
        return R('ok.png')
    elif result == 'Update':
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
def test_popcorn():
    result         = True
    result_str     = 'Available'
    result_summary =  'Popcorn API is available.'

    try:
        JSON.ObjectFromURL(SharedCodeService.common.POPCORN_API + "/status", timeout=5)
    except:
        result         = False
        result_str     = 'Unavailable'
        result_summary = 'Popcorn API is unavailable.'

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

    return (result, result_str, result_summary)
