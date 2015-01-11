################################################################################
import multiprocessing
import tracking

from multiprocessing.pool import ThreadPool

################################################################################
SUBPREFIX = 'tvshows'

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
    object_container = ObjectContainer(title2='TV Shows')
    object_container.add(DirectoryObject(key=Callback(shows_menu, title='Trending', page='/shows/trending', page_index=0, per_page=31), title='Trending', summary='Browse TV shows currently being watched.'))
    object_container.add(DirectoryObject(key=Callback(shows_menu, title='Popular', page='/shows/popular', page_index=0, per_page=31), title='Popular', summary='Browse most popular TV shows.'))
    object_container.add(DirectoryObject(key=Callback(favorites_menu, title='Favorites'), title='Favorites', summary='Browse your favorite TV shows', thumb=R('favorites.png')))
    object_container.add(InputDirectoryObject(key=Callback(search_menu, title='Search'), title='Search', summary='Search TV shows', thumb=R('search.png'), prompt='Search for TV shows'))    
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/shows', page_index=int, per_page=int)
def shows_menu(title, page, page_index, per_page):
    ids = SharedCodeService.trakt.tvshows_list(page, page_index, per_page)

    object_container = ObjectContainer(title2=title)
    fill_object_container(object_container, ids)
    object_container.add(NextPageObject(key=Callback(shows_menu, title=title, page=page, page_index=page_index + 1, per_page=per_page), title="More..."))

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/favorites')
def favorites_menu(title):
    ids = Dict['tvshows_favorites'] if 'tvshows_favorites' in Dict else []

    object_container = ObjectContainer(title2=title)
    fill_object_container(object_container, ids)
    object_container.objects.sort(key=lambda tvshow_object: tvshow_object.title)
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search_menu(title, query):
    ids = SharedCodeService.trakt.tvshows_search(query)

    object_container = ObjectContainer(title2=title)
    fill_object_container(object_container, ids)

    return object_container

################################################################################
def fill_object_container(object_container, tvshow_ids):
    def worker_task(tvshow_id):
        tvshow_object = TVShowObject()
        tvshow_id = SharedCodeService.trakt.tvshows_fill_tvshow_object(tvshow_object, tvshow_id)
        if tvshow_id:
            tvshow_object.key        = Callback(tvshow_menu, title=tvshow_object.title, tvshow_id=tvshow_id)
            tvshow_object.rating_key = tvshow_id
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
def tvshow_menu(title, tvshow_id):
    object_container = ObjectContainer(title2=title)
    if 'tvshows_favorites' in Dict and tvshow_id in Dict['tvshows_favorites']:
        object_container.add(DirectoryObject(key=Callback(remove_from_favorites, title='Remove from Favorites', show_title=title, tvshow_id=tvshow_id), title='Remove from Favorites', summary='Remove TV show from Favorites', thumb=R('favorites.png')))
    else:
        object_container.add(DirectoryObject(key=Callback(add_to_favorites, title='Add to Favorites', show_title=title, tvshow_id=tvshow_id), title='Add to Favorites', summary='Add TV show to Favorites', thumb=R('favorites.png')))

    for season_index in SharedCodeService.trakt.tvshows_get_season_index_list(tvshow_id):
        season_object = SeasonObject()
        SharedCodeService.trakt.tvshows_fill_season_object(season_object, tvshow_id, season_index)
        season_object.key = Callback(season_menu, title=season_object.title, show_title=title, tvshow_id=tvshow_id, season_index=season_object.index)
        season_object.rating_key = '{0}-{1}'.format(tvshow_id, season_index)
        object_container.add(season_object)

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/add_to_favorites')
def add_to_favorites(title, show_title, tvshow_id):
    if 'tvshows_favorites' not in Dict:
        Dict['tvshows_favorites'] = []

    if tvshow_id not in Dict['tvshows_favorites']:
        Dict['tvshows_favorites'].append(tvshow_id)
        Dict.Save()

    object_container = ObjectContainer(title2=title)
    object_container.header  = 'Add to Favorites'
    object_container.message = '{0} added to Favorites'.format(show_title)
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/remove_from_favorites')
def remove_from_favorites(title, show_title, tvshow_id):
    if 'tvshows_favorites' in Dict and tvshow_id in Dict['tvshows_favorites']:
        Dict['tvshows_favorites'].remove(tvshow_id)
        Dict.Save()

    object_container = ObjectContainer(title2=title)
    object_container.header  = 'Remove from Favorites'
    object_container.message = '{0} removed from Favorites'.format(show_title)
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/season', season_index=int)
def season_menu(title, show_title, tvshow_id, season_index):
    object_container = ObjectContainer(title2=title)
    for episode_index in SharedCodeService.trakt.tvshows_get_season_episode_index_list(tvshow_id, season_index):
        directory_object = DirectoryObject()
        episode_data = SharedCodeService.trakt.tvshows_fill_episode_object(directory_object, tvshow_id, season_index, episode_index)
        directory_object.title = str(episode_index) + '. ' + directory_object.title
        directory_object.key  = Callback(episode_menu, show_title=show_title, tvshow_id=tvshow_id, season_index=season_index, episode_index=episode_index, first_aired_iso=episode_data['first_aired'])
        object_container.add(directory_object)

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/episode', season_index=int, episode_index=int)
def episode_menu(show_title, tvshow_id, season_index, episode_index, first_aired_iso):
    tracking.track('/TV Shows/Episode', { 'Title': show_title, 'Season': season_index, 'Episode': episode_index })

    torrent_provider = SharedCodeService.metaprovider.MetaProvider()
    torrent_infos    = []
    torrent_provider.tvshows_get_specific_torrents(tvshow_id, season_index, episode_index, first_aired_iso, torrent_infos)

    torrent_infos.sort(key=lambda torrent_info: torrent_info.seeders, reverse=True)

    object_container = ObjectContainer()
    
    for torrent_info in torrent_infos:
        seeders_leechers_line = '{0}\nSeeders: {1}, Leechers: {2}'.format(torrent_info.size, torrent_info.seeders, torrent_info.leechers)

        episode_object = EpisodeObject()

        SharedCodeService.trakt.tvshows_fill_episode_object(episode_object, tvshow_id, season_index, episode_index)
        object_container.title2 = episode_object.title

        episode_object.title    = torrent_info.release
        episode_object.summary  = '{0}\n\n{1}'.format(seeders_leechers_line, episode_object.summary)
        episode_object.url      = torrent_info.url

        object_container.add(episode_object)

    return object_container
