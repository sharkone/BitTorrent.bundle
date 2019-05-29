################################################################################
GITHUB_REPOSITORY = 'sharkone/BitTorrent.bundle'

################################################################################
def get_latest_version():
    try:
        release_feed_url = 'https://github.com/{0}/releases.atom'.format(GITHUB_REPOSITORY)
        release_feed_data = RSS.FeedFromURL(release_feed_url, cacheTime=0, timeout=5)
        return release_feed_data.entries[0].title
    except Exception as exception:
        Log.Error('Checking for new releases failed: {0}'.format(repr(exception)))

################################################################################
def update_available():
    latest_version_str = get_latest_version()
    if latest_version_str:
        latest_version  = map(int, latest_version_str.split('.'))
        current_version = map(int, SharedCodeService.common.VERSION.split('.'))
        return (latest_version[0] > current_version[0] or latest_version[1] > current_version[1] or latest_version[2] > current_version[2], latest_version_str)
    return (False, None)

################################################################################
@route(SharedCodeService.common.PREFIX + '/update')
def update(**kwargs):
    try:
        latest_version = get_latest_version()
        if latest_version:
            zip_data = Archive.ZipFromURL('https://github.com/{0}/archive/{1}.zip'.format(GITHUB_REPOSITORY, latest_version))

            SharedCodeService.scrapmagnet.stop()

            for name in zip_data.Names():
                data    = zip_data[name]
                parts   = name.split('/')
                shifted = Core.storage.join_path(*parts[1:])
                full    = Core.storage.join_path(Core.bundle_path, shifted)

                if '/.' in name:
                    continue

                if name.endswith('/'):
                    Core.storage.ensure_dirs(full)
                else:
                    Core.storage.save(full, data)
            del zip_data
            return ObjectContainer(header='Update successful', message='Channel updated to version {0}'.format(latest_version))
    except Exception as exception:
        return ObjectContainer(header='Update failed', message=str(exception))
