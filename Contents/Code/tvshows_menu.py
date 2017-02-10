################################################################################

from DumbTools import DumbKeyboard

################################################################################
SUBPREFIX = 'tvshows'

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
    object_container = ObjectContainer(title2='TV Shows')
    object_container.add(DirectoryObject(key=Callback(shows_menu, title='Recent', page='/shows', sort='updated', page_index=1), title='Recent', summary='Browse recently updated TV shows.'))
    object_container.add(DirectoryObject(key=Callback(shows_menu, title='Trending', page='/shows', sort='trending', page_index=1), title='Trending', summary='Browse trending TV shows.'))
    object_container.add(DirectoryObject(key=Callback(shows_menu, title='Popular', page='/shows', sort='', page_index=1), title='Popular', summary='Browse popular TV shows.'))
    object_container.add(DirectoryObject(key=Callback(favorites_menu, title='Favorites'), title='Favorites', summary='Browse your favorite TV shows', thumb=R('favorites.png')))

    if Client.Product in DumbKeyboard.clients:
        DumbKeyboard(SharedCodeService.common.PREFIX + '/' + SUBPREFIX, object_container, search_menu, dktitle='Search', dkthumb=R('search.png'), title='Search')
    else:
        object_container.add(InputDirectoryObject(key=Callback(search_menu, title='Search'), title='Search', summary='Search TV shows', thumb=R('search.png'), prompt='Search for TV shows'))
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/shows', page_index=int)
def shows_menu(title, page, sort, page_index):
    object_container = ObjectContainer(title2=title)

    json_url  = SharedCodeService.common.POPCORN_API + page + '/{0}?sort={1}'.format(page_index, sort)
    json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

    if json_data:
        for json_item in json_data:
            object_container.add(create_tvshow_object(json_item))

    if (page_index + 1) <= 10:
        object_container.add(NextPageObject(key=Callback(shows_menu, title=title, page=page, sort=sort, page_index=page_index + 1), title="More..."))

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/favorites')
def favorites_menu(title):
    ids = Dict['SHOWS_FAVORITES'] if 'SHOWS_FAVORITES' in Dict else []

    object_container = ObjectContainer(title2=title)

    for id in ids:
        json_url  = SharedCodeService.common.POPCORN_API + '/show/' + id
        json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

        if json_data:
            object_container.add(create_tvshow_object(json_data))

    object_container.objects.sort(key=lambda show_object: show_object.title)

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search_menu(title, query):
    object_container = ObjectContainer(title2=title)

    json_url  = SharedCodeService.common.POPCORN_API + '/shows/1?keywords={0}'.format(String.Quote(query))
    json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

    if json_data:
        for json_item in json_data:
            object_container.add(create_tvshow_object(json_item))

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/tvshow')
def show_menu(title, id):
    object_container = ObjectContainer(title2=title)

    json_url  = SharedCodeService.common.POPCORN_API + '/show/' + id
    json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

    if json_data:
        seasons = []

        for json_item in json_data['episodes']:
            if json_item['season'] not in seasons:
                seasons.append(json_item['season'])

                season_object            = SeasonObject()
                season_object.title      = 'Season {0}'.format(json_item['season'])
                season_object.index      = json_item['season']
                season_object.show       = title
                season_object.rating_key = '{0}-{1}'.format(id, season_object.index)
                season_object.key        = Callback(season_menu, title=season_object.title, show_title=season_object.show, id=id, season_index=season_object.index)
                object_container.add(season_object)

    object_container.objects.sort(key=lambda season_object: season_object.index)

    if 'SHOWS_FAVORITES' in Dict and id in Dict['SHOWS_FAVORITES']:
        object_container.add(DirectoryObject(key=Callback(remove_from_favorites, title='Remove from Favorites', show_title=title, id=id), title='Remove from Favorites', summary='Remove TV show from Favorites', thumb=R('favorites.png')))
    else:
        object_container.add(DirectoryObject(key=Callback(add_to_favorites, title='Add to Favorites', show_title=title, id=id), title='Add to Favorites', summary='Add TV show to Favorites', thumb=R('favorites.png')))

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/season', season_index=int)
def season_menu(title, show_title, id, season_index):
    object_container = ObjectContainer(title2=title)

    json_url  = SharedCodeService.common.POPCORN_API + '/show/' + id
    json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

    if json_data and 'episodes' in json_data:
        episodes = []

        for json_item in json_data['episodes']:
            if json_item['season'] == season_index:
                episode            = {}
                episode['title']   = u'{0}. {1}'.format(json_item['episode'], json_item['title'])
                episode['summary'] = json_item['overview']
                episode['index']   = json_item['episode']
                episodes.append(episode)

        episodes.sort(key=lambda episode: episode['index'])

        for episode in episodes:
            directory_object = DirectoryObject()
            directory_object.title   = episode['title']
            directory_object.summary = episode['summary']
            directory_object.thumb   = json_data['images']['poster']
            directory_object.art     = json_data['images']['fanart']
            directory_object.key     = Callback(episode_menu, show_title=show_title, id=id, season_index=season_index, episode_index=episode['index'])
            object_container.add(directory_object)

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/episode', season_index=int, episode_index=int)
def episode_menu(show_title, id, season_index, episode_index):
    object_container = ObjectContainer()

    json_url  = SharedCodeService.common.POPCORN_API + '/show/' + id
    json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

    if json_data and 'episodes' in json_data:
        for json_item in json_data['episodes']:
            if json_item['season'] == season_index and json_item['episode'] == episode_index:
                if 'torrents' in json_item:
                    for key, magnet_data in json_item['torrents'].iteritems():
                        episode_object = EpisodeObject()
                        SharedCodeService.common.fill_episode_object(episode_object, json_item, json_data)
                        episode_object.title   = SharedCodeService.common.fix_episode_torrent_title(json_data, json_item, key, magnet_data)
                        episode_object.summary = 'Seeds: {0} - Peers: {1}\n\n{2}'.format(magnet_data['seeds'], magnet_data['peers'], episode_object.summary)
                        episode_object.url     = json_url + '?magnet=' + String.Quote(magnet_data['url'])
                        object_container.add(episode_object)

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/add_to_favorites')
def add_to_favorites(title, show_title, id):
    if 'SHOWS_FAVORITES' not in Dict:
        Dict['SHOWS_FAVORITES'] = []

    if id not in Dict['SHOWS_FAVORITES']:
        Dict['SHOWS_FAVORITES'].append(id)
        Dict.Save()

    object_container = ObjectContainer(title2=title)
    object_container.header  = 'Add to Favorites'
    object_container.message = '{0} added to Favorites'.format(show_title)
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/remove_from_favorites')
def remove_from_favorites(title, show_title, id):
    if 'SHOWS_FAVORITES' in Dict and id in Dict['SHOWS_FAVORITES']:
        Dict['SHOWS_FAVORITES'].remove(id)
        Dict.Save()

    object_container = ObjectContainer(title2=title)
    object_container.header  = 'Remove from Favorites'
    object_container.message = '{0} removed from Favorites'.format(show_title)
    return object_container

################################################################################
def create_tvshow_object(json_item):
    show_object = TVShowObject()
    SharedCodeService.common.fill_show_object(show_object, json_item)
    show_object.rating_key = json_item['_id']
    show_object.key        = Callback(show_menu, title=show_object.title, id=json_item['_id'])
    return show_object
