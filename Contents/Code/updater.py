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
    latest_version = get_latest_version()
    if latest_version:
        return latest_version > SharedCodeService.common.VERSION

################################################################################
def create_button():
    latest_version = get_latest_version()
    if latest_version:
        return DirectoryObject(key=Callback(update), title='Update available: {0}'.format(latest_version), summary='Install latest version of the BitTorrent channel.', thumb=R('update.png'))

################################################################################
@route(SharedCodeService.common.PREFIX + '/update')
def update():
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
