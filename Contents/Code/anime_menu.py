################################################################################
import tracking

################################################################################
SUBPREFIX = 'anime'

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
    tracking.track('Entered Anime')

    object_container = ObjectContainer(title2='Anime')
    object_container.add(DirectoryObject(key=Callback(popular, title='Popular', per_page=31), title='Popular'))
    object_container.add(InputDirectoryObject(key=Callback(search, title='Search', per_page=31), title='Search', thumb=R('search.png')))
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/popular', per_page=int, movie_count=int)
def popular(title, per_page, movie_count=0):
    tracking.track('Entered Anime/' + title)

    torrent_infos = []

    torrent_provider = SharedCodeService.metaprovider.MetaProvider()
    torrent_provider.anime_get_popular_torrents(torrent_infos)

    torrent_infos.sort(key=lambda torrent_info: torrent_info.seeders, reverse=True)

    object_container = ObjectContainer(title2='Popular')

    for torrent_info in torrent_infos:
        seeders_leechers_line = '{0}\nSeeders: {1}, Leechers: {2}'.format(torrent_info.size, torrent_info.seeders, torrent_info.leechers)

        videoclip_object         = VideoClipObject()
        videoclip_object.title   = torrent_info.title
        videoclip_object.summary = seeders_leechers_line
        videoclip_object.url     = torrent_info.url

        object_container.add(videoclip_object)

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search(title, query, per_page, movie_count=0):
    tracking.track('Entered Anime/' + title)

    torrent_infos = []

    torrent_provider = SharedCodeService.metaprovider.MetaProvider()
    torrent_provider.anime_search(query, torrent_infos)

    torrent_infos.sort(key=lambda torrent_info: torrent_info.seeders, reverse=True)

    object_container = ObjectContainer(title2=title)

    for torrent_info in torrent_infos:
        seeders_leechers_line = '{0}\nSeeders: {1}, Leechers: {2}'.format(torrent_info.size, torrent_info.seeders, torrent_info.leechers)

        videoclip_object         = VideoClipObject()
        videoclip_object.title   = torrent_info.title
        videoclip_object.summary = seeders_leechers_line
        videoclip_object.url     = torrent_info.url

        object_container.add(videoclip_object)

    return object_container
