################################################################################
import multiprocessing
import tracking

from multiprocessing.pool import ThreadPool

################################################################################
SUBPREFIX = 'movies'

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
    object_container = ObjectContainer(title2='Movies')
    object_container.add(DirectoryObject(key=Callback(movies_menu, title='Trending', page='/movies/trending', page_index=1, per_page=31), title='Trending', summary='Browse movies currently being watched.'))
    object_container.add(DirectoryObject(key=Callback(movies_menu, title='Popular', page='/movies/popular', page_index=1, per_page=31), title='Popular', summary='Browse most popular movies.'))
    object_container.add(InputDirectoryObject(key=Callback(search_menu, title='Search'), title='Search', summary='Search movies', thumb=R('search.png'), prompt='Search for movies'))
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/movies', page_index=int, per_page=int)
def movies_menu(title, page, page_index, per_page):
    ids = SharedCodeService.trakt.movies_list(page, page_index, per_page)

    object_container = ObjectContainer(title2=title)
    fill_object_container(object_container, ids)
    object_container.add(NextPageObject(key=Callback(movies_menu, title=title, page=page, page_index=page_index + 1, per_page=per_page), title="More..."))
    
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search_menu(title, query):
    ids = SharedCodeService.trakt.movies_search(query)

    object_container = ObjectContainer(title2=title)
    fill_object_container(object_container, ids)

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/movie')
def movie_menu(title, imdb_id):
    tracking.track('/Movies/Movie', { 'Title': title })

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
            directory_object.key = Callback(movie_menu, title=directory_object.title, imdb_id=imdb_id)
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
