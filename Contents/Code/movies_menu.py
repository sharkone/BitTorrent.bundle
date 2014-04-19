################################################################################
import multiprocessing
import tracking

from multiprocessing.pool import ThreadPool

################################################################################
SUBPREFIX = 'movies'

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
    tracking.track('Entered Movies')

    object_container = ObjectContainer(title2='Movies')
    object_container.add(DirectoryObject(key=Callback(list_menu, title='Popular', page='/movies/trending', per_page=31), title='Popular'))
    object_container.add(DirectoryObject(key=Callback(list_menu, title='Rating', page='/movies/popular', per_page=31), title='Rating'))
    object_container.add(DirectoryObject(key=Callback(genres_menu, title='Genres'), title='Genres'))
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
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/genres_menu')
def genres_menu(title):
    tracking.track('Entered Movies/' + title)

    genres = SharedCodeService.trakt.movies_genres()

    object_container = ObjectContainer(title2=title)
    for genre in genres:
        object_container.add(DirectoryObject(key=Callback(list_menu, title=genre[0], page='/movies/popular/' + genre[1], per_page=31), title=genre[0]))
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
def movie(title, imdb_id):
    tracking.track('Entered Movies/Movie', { 'Title': title})

    torrent_infos = []
    
    torrent_provider = SharedCodeService.metaprovider.MetaProvider()
    torrent_provider.movies_get_specific_torrents(imdb_id, torrent_infos)

    torrent_infos.sort(key=lambda torrent_info: torrent_info.seeders, reverse=True)

    object_container = ObjectContainer(title2=title)
    
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
    def worker_task(id):
        directory_object = DirectoryObject()
        imdb_id = SharedCodeService.trakt.movies_fill_movie_object(directory_object, id)
        if imdb_id:
            directory_object.key = Callback(movie, title=directory_object.title, imdb_id=imdb_id)
            return directory_object
        return -1

    if Platform.OS != 'Linux':
        thread_pool = ThreadPool(10)
        map_results = thread_pool.map(worker_task, ids)

        thread_pool.terminate()
        thread_pool.join()
    else:
        map_results = []
        for id in ids:
            map_results.append(worker_task(id))

    for map_result in map_results:
        if map_result and map_result != -1:
            object_container.add(map_result)
