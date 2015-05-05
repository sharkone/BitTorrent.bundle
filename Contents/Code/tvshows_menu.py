################################################################################
SUBPREFIX = 'tvshows'

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
    object_container = ObjectContainer(title2='TV Shows')
    object_container.add(DirectoryObject(key=Callback(shows_menu, title='Trending', page='/api/shows/trending', page_index=1), title='Trending', summary='Browse TV shows currently being watched.'))
    object_container.add(DirectoryObject(key=Callback(shows_menu, title='Popular', page='/api/shows/popular', page_index=1), title='Popular', summary='Browse most popular TV shows.'))
    object_container.add(DirectoryObject(key=Callback(favorites_menu, title='Favorites'), title='Favorites', summary='Browse your favorite TV shows', thumb=R('favorites.png')))
    object_container.add(InputDirectoryObject(key=Callback(search_menu, title='Search'), title='Search', summary='Search TV shows', thumb=R('search.png'), prompt='Search for TV shows'))    
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/shows', page_index=int)
def shows_menu(title, page, page_index):
    object_container = ObjectContainer(title2=title)

    json_url  = Prefs['SCRAPYARD_URL'] + page + '?page={0}'.format(page_index)
    json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

    if json_data and 'shows' in json_data:
        for json_item in json_data['shows']:
            show_object = TVShowObject()
            SharedCodeService.common.fill_show_object(show_object, json_item)
            show_object.rating_key = json_item['trakt_slug']
            show_object.key        = Callback(show_menu, title=show_object.title, trakt_slug=json_item['trakt_slug'])
            object_container.add(show_object)

    if (page_index + 1) <= 10:
        object_container.add(NextPageObject(key=Callback(shows_menu, title=title, page=page, page_index=page_index + 1), title="More..."))

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/favorites')
def favorites_menu(title):
    trakt_slugs = Dict['shows_favorites'] if 'shows_favorites' in Dict else []

    object_container = ObjectContainer(title2=title)
    
    json_url = Prefs['SCRAPYARD_URL'] + '/api/shows/favorites?'
    json_post = { 'shows_favorites': JSON.StringFromObject(trakt_slugs) }
    json_data = JSON.ObjectFromURL(json_url, values=json_post, cacheTime=CACHE_1HOUR)

    if json_data and 'shows' in json_data:
        for json_item in json_data['shows']:
            show_object = TVShowObject()
            SharedCodeService.common.fill_show_object(show_object, json_item)
            show_object.rating_key = json_item['trakt_slug']
            show_object.key        = Callback(show_menu, title=show_object.title, trakt_slug=json_item['trakt_slug'])
            object_container.add(show_object)
    
    object_container.objects.sort(key=lambda tvshow_object: show_object.title)
    
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search_menu(title, query):
    object_container = ObjectContainer(title2=title)

    json_url  = Prefs['SCRAPYARD_URL'] + '/api/shows/search?query=' + String.Quote(query)
    json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

    if json_data and 'shows' in json_data:
        for json_item in json_data['shows']:
            show_object = TVShowObject()
            SharedCodeService.common.fill_show_object(show_object, json_item)
            show_object.rating_key = json_item['trakt_slug']
            show_object.key        = Callback(show_menu, title=show_object.title, trakt_slug=json_item['trakt_slug'])
            object_container.add(show_object)

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/tvshow')
def show_menu(title, trakt_slug):
    object_container = ObjectContainer(title2=title)

    if 'shows_favorites' in Dict and trakt_slug in Dict['shows_favorites']:
        object_container.add(DirectoryObject(key=Callback(remove_from_favorites, title='Remove from Favorites', show_title=title, trakt_slug=trakt_slug), title='Remove from Favorites', summary='Remove TV show from Favorites', thumb=R('favorites.png')))
    else:
        object_container.add(DirectoryObject(key=Callback(add_to_favorites, title='Add to Favorites', show_title=title, trakt_slug=trakt_slug), title='Add to Favorites', summary='Add TV show to Favorites', thumb=R('favorites.png')))

    json_url  = Prefs['SCRAPYARD_URL'] + '/api/show/' + trakt_slug
    json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

    if json_data and 'seasons' in json_data:
        for json_item in json_data['seasons']:
            season_object = SeasonObject()
            SharedCodeService.common.fill_season_object(season_object, json_item)
            season_object.rating_key    = '{0}-{1}'.format(trakt_slug, season_object.index)
            season_object.key           = Callback(season_menu, title=season_object.title, show_title=title, trakt_slug=trakt_slug, season_index=season_object.index)
            object_container.add(season_object)

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/add_to_favorites')
def add_to_favorites(title, show_title, trakt_slug):
    if 'shows_favorites' not in Dict:
        Dict['shows_favorites'] = []

    if trakt_slug not in Dict['shows_favorites']:
        Dict['shows_favorites'].append(trakt_slug)
        Dict.Save()

    object_container = ObjectContainer(title2=title)
    object_container.header  = 'Add to Favorites'
    object_container.message = '{0} added to Favorites'.format(show_title)
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/remove_from_favorites')
def remove_from_favorites(title, show_title, trakt_slug):
    if 'shows_favorites' in Dict and trakt_slug in Dict['shows_favorites']:
        Dict['shows_favorites'].remove(trakt_slug)
        Dict.Save()

    object_container = ObjectContainer(title2=title)
    object_container.header  = 'Remove from Favorites'
    object_container.message = '{0} removed from Favorites'.format(show_title)
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/season', season_index=int)
def season_menu(title, show_title, trakt_slug, season_index):
    object_container = ObjectContainer(title2=title)

    json_url  = Prefs['SCRAPYARD_URL'] + '/api/show/' + trakt_slug + '/season/' + str(season_index)
    json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

    if json_data and 'episodes' in json_data:
        for json_item in json_data['episodes']:
            directory_object = DirectoryObject()
            directory_object.title   = '{0}. {1}'.format(json_item['episode_index'], json_item['title'])
            directory_object.summary = json_item['overview']
            directory_object.thumb   = json_item['thumb']
            directory_object.art     = json_item['art']
            directory_object.key     = Callback(episode_menu, show_title=show_title, trakt_slug=trakt_slug, season_index=season_index, episode_index=json_item['episode_index'])
            object_container.add(directory_object)

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/episode', season_index=int, episode_index=int)
def episode_menu(show_title, trakt_slug, season_index, episode_index):
    object_container = ObjectContainer()

    json_url  = Prefs['SCRAPYARD_URL'] + '/api/show/' + trakt_slug + '/season/' + str(season_index) + '/episode/' + str(episode_index)
    json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

    if json_data and 'magnets' in json_data:
        for json_item in json_data['magnets']:
            episode_object = EpisodeObject()
            SharedCodeService.common.fill_episode_object(episode_object, json_data)
            episode_object.title   = json_item['title']
            episode_object.summary = 'Seeds: {0} - Peers: {1}\nSize: {2}\n\n{3}'.format(json_item['seeds'], json_item['peers'], SharedCodeService.utils.get_magnet_size_str(json_item), episode_object.summary)
            episode_object.url     = json_url + '?magnet=' + String.Quote(json_item['link'])
            object_container.add(episode_object)

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/empty')
def empty_menu():
    object_container = ObjectContainer(title2='Empty')
    return object_container
