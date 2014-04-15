################################################################################
import tracking

################################################################################
SUBPREFIX = 'movies'

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
    tracking.track('Entered Movies')

    object_container = ObjectContainer(title2='Movies')
    object_container.add(DirectoryObject(key=Callback(list_menu, title='Popular', page='/movies/trending', per_page=31), title='Popular'))
    object_container.add(DirectoryObject(key=Callback(list_menu, title='Rating', page='/movies/popular', per_page=31), title='Rating'))
    object_container.add(InputDirectoryObject(key=Callback(search, title='Search', per_page=31), title='Search', thumb=R('search.png')))
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/list_menu', per_page=int, count=int)
def list_menu(title, page, per_page, count=0):
    tracking.track('Entered Movies/' + title)

    ids   = []
    count = SharedCodeService.trakt.get_ids_from_page(page, ids, count, per_page)

    object_container = ObjectContainer(title2=title)
    fill_object_container(object_container, ids)
    object_container.add(NextPageObject(key=Callback(list_menu, title=title, page=page, per_page=per_page, count=count), title="More..."))
    
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search(title, query, per_page, count=0):
    tracking.track('Entered Movies/' + title)

    ids   = []
    count = SharedCodeService.trakt.movies_search(query, ids)

    object_container = ObjectContainer(title2=title)
    fill_object_container(object_container, ids)
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/movie')
def movie(imdb_id):
    torrent_infos = []
    
    torrent_provider = SharedCodeService.metaprovider.MetaProvider()
    torrent_provider.movies_get_specific_torrents(imdb_id, torrent_infos)

    torrent_infos.sort(key=lambda torrent_info: torrent_info.seeders, reverse=True)

    object_container = ObjectContainer()
    
    for torrent_info in torrent_infos:
        seeders_leechers_line = '{0}\nSeeders: {1}, Leechers: {2}'.format(torrent_info.size, torrent_info.seeders, torrent_info.leechers)

        movie_object = MovieObject()

        SharedCodeService.trakt.movies_fill_movie_object(movie_object, imdb_id)
        object_container.title2 = movie_object.title

        movie_object.title    = torrent_info.release
        movie_object.summary  = '{0}\n\n{1}'.format(seeders_leechers_line, movie_object.summary) 
        movie_object.url      = torrent_info.url

        object_container.add(movie_object)

    return object_container

################################################################################
def fill_object_container(object_container, ids):
    for id in ids:
        directory_object = DirectoryObject()
        imdb_id = SharedCodeService.trakt.movies_fill_movie_object(directory_object, id)
        if imdb_id:
            directory_object.key = Callback(movie, imdb_id=imdb_id)
            object_container.add(directory_object)
