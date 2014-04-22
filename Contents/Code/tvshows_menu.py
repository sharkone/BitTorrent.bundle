################################################################################
import multiprocessing
import tracking

from multiprocessing.pool import ThreadPool

################################################################################
SUBPREFIX = 'tvshows'

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
    tracking.track('/TV Shows')

    object_container = ObjectContainer(title2='TV Shows')
    object_container.add(DirectoryObject(key=Callback(shows_menu, title='Popular', page='/shows/trending', per_page=31), title='Popular', summary='Browse popular TV shows'))
    object_container.add(DirectoryObject(key=Callback(shows_menu, title='Rating', page='/shows/popular', per_page=31), title='Rating', summary='Browse highly-rated TV shows'))
    object_container.add(DirectoryObject(key=Callback(genres_menu, title='Genres'), title='Genres', summary='Browse TV shows by genre'))
    object_container.add(InputDirectoryObject(key=Callback(search_menu, title='Search', per_page=31), title='Search', summary='Search TV shows', thumb=R('search.png'), prompt='Search for TV shows'))    
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/shows', per_page=int, count=int)
def shows_menu(title, page, per_page, count=0):
    tracking.track('/TV Shows/' + title)

    ids   = []
    count = SharedCodeService.trakt.get_ids_from_page(page, ids, count, per_page)

    object_container = ObjectContainer(title2=title)
    fill_object_container(object_container, ids)
    object_container.add(NextPageObject(key=Callback(shows_menu, title=title, page=page, per_page=per_page, count=count), title="More..."))
    
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/genres')
def genres_menu(title):
    tracking.track('/TV Shows/' + title)

    genres = SharedCodeService.trakt.tvshows_genres()

    object_container = ObjectContainer(title2=title)
    for genre in genres:
        object_container.add(DirectoryObject(key=Callback(genre_menu, title=genre[0], genre=genre[1], per_page=31), title=genre[0]))
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/genre', per_page=int, count=int)
def genre_menu(title, genre, per_page, count=0):
    tracking.track('/TV Shows/Genre', { 'Genre': title })

    ids   = []
    count = SharedCodeService.trakt.get_ids_from_page('/shows/popular/' + genre, ids, count, per_page)

    object_container = ObjectContainer(title2=title)
    fill_object_container(object_container, ids)
    object_container.add(NextPageObject(key=Callback(genre_menu, title=title, genre=genre, per_page=per_page, count=count), title="More..."))
    
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search_menu(title, query, per_page, count=0):
    tracking.track('/TV Shows/' + title, { 'Query': query })

    ids   = []
    count = SharedCodeService.trakt.tvshows_search(query, ids)

    object_container = ObjectContainer(title2=title)
    fill_object_container(object_container, ids)
    return object_container

################################################################################
def fill_object_container(object_container, tvshow_ids):
    def worker_task(tvshow_id):
        tvshow_object = TVShowObject()
        tvdb_id = SharedCodeService.trakt.tvshows_fill_tvshow_object(tvshow_object, tvshow_id)
        if tvdb_id:
            tvshow_object.key        = Callback(tvshow_menu, title=tvshow_object.title, tvdb_id=tvdb_id)
            tvshow_object.rating_key = '{0}-{1}'.format(tvshow_object.title, tvdb_id)
            return tvshow_object
        return -1

    if Platform.OS != 'Linux':
        thread_pool = ThreadPool(10)
        map_results = thread_pool.map(worker_task, tvshow_ids)

        thread_pool.terminate()
        thread_pool.join()
    else:
        map_results = []
        for id in tvshow_ids:
            map_results.append(worker_task(id))

    for map_result in map_results:
        if map_result and map_result != -1:
            object_container.add(map_result)

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/tvshow')
def tvshow_menu(title, tvdb_id):
    tracking.track('/TV Shows/TV Show', { 'Title': title })

    object_container = ObjectContainer(title2=title)
    for season_index in SharedCodeService.trakt.tvshows_get_season_index_list(tvdb_id):
        season_object = SeasonObject()
        SharedCodeService.trakt.tvshows_fill_season_object(season_object, tvdb_id, season_index)
        season_object.key = Callback(season_menu, title=season_object.title, show_title=title, tvdb_id=tvdb_id, season_index=season_object.index)
        season_object.rating_key = '{0}-{1}-{2}'.format(title, tvdb_id, season_index)
        object_container.add(season_object)

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/season', season_index=int)
def season_menu(title, show_title, tvdb_id, season_index):
    tracking.track('/TV Shows/Season', { 'Title': show_title, 'Season': season_index })

    object_container = ObjectContainer(title2=title)
    for episode_index in SharedCodeService.trakt.tvshows_get_season_episode_index_list(tvdb_id, season_index):
        directory_object = DirectoryObject()
        SharedCodeService.trakt.tvshows_fill_episode_object(directory_object, tvdb_id, season_index, episode_index)
        directory_object.title = str(episode_index) + '. ' + directory_object.title
        directory_object.key  = Callback(episode_menu, show_title=show_title, tvdb_id=tvdb_id, season_index=season_index, episode_index=episode_index)
        object_container.add(directory_object)

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/episode', season_index=int, episode_index=int)
def episode_menu(show_title, tvdb_id, season_index, episode_index):
    tracking.track('/TV Shows/Episode', { 'Title': show_title, 'Season': season_index, 'Episode': episode_index })

    torrent_provider = SharedCodeService.metaprovider.MetaProvider()
    torrent_infos    = []
    torrent_provider.tvshows_get_specific_torrents(tvdb_id, season_index, episode_index, torrent_infos)

    torrent_infos.sort(key=lambda torrent_info: torrent_info.seeders, reverse=True)

    object_container = ObjectContainer()
    
    for torrent_info in torrent_infos:
        seeders_leechers_line = '{0}\nSeeders: {1}, Leechers: {2}'.format(torrent_info.size, torrent_info.seeders, torrent_info.leechers)

        episode_object = EpisodeObject()

        SharedCodeService.trakt.tvshows_fill_episode_object(episode_object, tvdb_id, season_index, episode_index)
        object_container.title2 = episode_object.title

        episode_object.title    = torrent_info.release
        episode_object.summary  = '{0}\n\n{1}'.format(seeders_leechers_line, episode_object.summary)
        episode_object.url      = torrent_info.url

        object_container.add(episode_object)

    return object_container
