################################################################################
SUBPREFIX = 'tvshows'

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
    object_container = ObjectContainer(title2='TV Shows')
    object_container.add(DirectoryObject(key=Callback(list_menu, title='Popular', page='/shows/trending', per_page=31), title='Popular'))
    object_container.add(DirectoryObject(key=Callback(list_menu, title='Rating', page='/shows/popular', per_page=31), title='Rating'))
    object_container.add(InputDirectoryObject(key=Callback(search, per_page=31), title='Search', thumb=R('search.png')))
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/list_menu', per_page=int, count=int)
def list_menu(title, page, per_page, count=0):
    ids   = []
    count = SharedCodeService.trakt.get_ids_from_page(page, ids, count, per_page)

    object_container = ObjectContainer(title2=title)
    fill_object_container(object_container, ids)
    object_container.add(NextPageObject(key=Callback(list_menu, title=title, page=page, per_page=per_page, count=count), title="More..."))
    
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search(query, per_page, count=0):
    ids   = []
    count = SharedCodeService.trakt.tvshows_search(query, ids)

    object_container = ObjectContainer(title2='Search')
    fill_object_container(object_container, ids)
    return object_container

################################################################################
def fill_object_container(object_container, tvshow_ids):
    for tvshow_id in tvshow_ids:
        tvshow_object = TVShowObject()
        tvdb_id = SharedCodeService.trakt.tvshows_fill_tvshow_object(tvshow_object, tvshow_id)
        if tvdb_id:
            tvshow_object.key        = Callback(tvshow, title=tvshow_object.title, tvdb_id=tvdb_id)
            tvshow_object.rating_key = '{0}-{1}'.format(tvshow_object.title, tvdb_id)
            object_container.add(tvshow_object)

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/tvshow')
def tvshow(title, tvdb_id):
    object_container = ObjectContainer(title2=title)
    for season_index in SharedCodeService.trakt.tvshows_get_season_index_list(tvdb_id):
        if season_index == 0:
            continue
        season_object = SeasonObject()
        SharedCodeService.trakt.tvshows_fill_season_object(season_object, tvdb_id, season_index)
        season_object.key = Callback(season, title=season_object.title, tvdb_id=tvdb_id, season_index=season_object.index)
        season_object.rating_key = '{0}-{1}-{2}'.format(title, tvdb_id, season_index)
        object_container.add(season_object)

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/season', season_index=int)
def season(title, tvdb_id, season_index):
    object_container = ObjectContainer(title2=title)
    for episode_index in range(0, SharedCodeService.trakt.tvshows_get_season_episode_count(tvdb_id, season_index)):
        if not SharedCodeService.trakt.tvshows_is_future_episode(tvdb_id, season_index, episode_index + 1):
            directory_object = DirectoryObject()
            SharedCodeService.trakt.tvshows_fill_episode_object(directory_object, tvdb_id, season_index, episode_index + 1)
            directory_object.title = str(episode_index + 1) + '. ' + directory_object.title
            directory_object.key  = Callback(episode, tvdb_id=tvdb_id, season_index=season_index, episode_index=episode_index + 1)
            object_container.add(directory_object)

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/episode', season_index=int, episode_index=int)
def episode(tvdb_id, season_index, episode_index):
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
