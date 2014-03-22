################################################################################
SUBPREFIX = 'tvshows'

################################################################################
ALLOW_UNRECOGNIZED = False

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
    object_container = ObjectContainer(title2='TV Shows')
    object_container.add(DirectoryObject(key=Callback(popular, per_page=31), title='Popular'))
    object_container.add(InputDirectoryObject(key=Callback(search, per_page=31), title='Search', thumb=R('search.png')))
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/popular', per_page=int, movie_count=int)
def popular(per_page, movie_count=0):
    torrent_infos = []

    torrent_provider = SharedCodeService.metaprovider.MetaProvider()
    torrent_provider.tvshows_get_popular_torrents(torrent_infos)

    torrent_infos.sort(key=lambda torrent_info: torrent_info.seeders, reverse=True)

    object_container = ObjectContainer(title2='Popular')

    for torrent_info in torrent_infos:
        seeders_leechers_line = 'Seeders: {0}, Leechers: {1}'.format(torrent_info.seeders, torrent_info.leechers)

        videoclip_object         = VideoClipObject()
        videoclip_object.title   = torrent_info.title
        videoclip_object.summary = seeders_leechers_line
        videoclip_object.url     = torrent_info.url

        object_container.add(videoclip_object)

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search(query, per_page, movie_count=0):
    torrent_infos = []

    torrent_provider = SharedCodeService.metaprovider.MetaProvider()
    torrent_provider.tvshows_search(query, torrent_infos)

    torrent_infos.sort(key=lambda torrent_info: torrent_info.seeders, reverse=True)

    object_container = ObjectContainer(title2='Popular')

    for torrent_info in torrent_infos:
        seeders_leechers_line = 'Seeders: {0}, Leechers: {1}'.format(torrent_info.seeders, torrent_info.leechers)

        videoclip_object         = VideoClipObject()
        videoclip_object.title   = torrent_info.title
        videoclip_object.summary = seeders_leechers_line
        videoclip_object.url     = torrent_info.url

        object_container.add(videoclip_object)

    return object_container
