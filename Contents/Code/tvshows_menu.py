################################################################################
import tracking

################################################################################
SUBPREFIX = 'tvshows'

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
    object_container = ObjectContainer(title2='TV Shows')
    object_container.add(DirectoryObject(key=Callback(shows_menu, title='Trending', page='/api/shows/trending', page_index=1, per_page=31), title='Trending', summary='Browse TV shows currently being watched.'))
    object_container.add(DirectoryObject(key=Callback(shows_menu, title='Popular', page='/api/shows/popular', page_index=1, per_page=31), title='Popular', summary='Browse most popular TV shows.'))
    #object_container.add(DirectoryObject(key=Callback(favorites_menu, title='Favorites'), title='Favorites', summary='Browse your favorite TV shows', thumb=R('favorites.png')))
    object_container.add(InputDirectoryObject(key=Callback(search_menu, title='Search'), title='Search', summary='Search TV shows', thumb=R('search.png'), prompt='Search for TV shows'))    
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/shows', page_index=int, per_page=int)
def shows_menu(title, page, page_index, per_page):
    object_container = ObjectContainer(title2=title)

    json_url  = Prefs['SCRAPYARD_URL'] + page + '?page={0}&limit={1}'.format(page_index, per_page)
    json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

    if json_data and 'shows' in json_data:
        for json_item in json_data['shows']:
            show_object = TVShowObject()
            SharedCodeService.common.fill_show_object(show_object, json_item)
            show_object.rating_key = json_item['trakt_slug']
            show_object.key        = Callback(show_menu, title=show_object.title, trakt_slug=json_item['trakt_slug'])
            object_container.add(show_object)

    object_container.add(NextPageObject(key=Callback(shows_menu, title=title, page=page, page_index=page_index + 1, per_page=per_page), title="More..."))

    return object_container

################################################################################
# @route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/favorites')
# def favorites_menu(title):
#     ids = Dict['tvshows_favorites'] if 'tvshows_favorites' in Dict else []

#     object_container = ObjectContainer(title2=title)
#     fill_object_container(object_container, ids)
#     object_container.objects.sort(key=lambda tvshow_object: tvshow_object.title)
#     return object_container

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
# @route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/add_to_favorites')
# def add_to_favorites(title, show_title, tvshow_id):
#     if 'tvshows_favorites' not in Dict:
#         Dict['tvshows_favorites'] = []

#     if tvshow_id not in Dict['tvshows_favorites']:
#         Dict['tvshows_favorites'].append(tvshow_id)
#         Dict.Save()

#     object_container = ObjectContainer(title2=title)
#     object_container.header  = 'Add to Favorites'
#     object_container.message = '{0} added to Favorites'.format(show_title)
#     return object_container

# ################################################################################
# @route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/remove_from_favorites')
# def remove_from_favorites(title, show_title, tvshow_id):
#     if 'tvshows_favorites' in Dict and tvshow_id in Dict['tvshows_favorites']:
#         Dict['tvshows_favorites'].remove(tvshow_id)
#         Dict.Save()

#     object_container = ObjectContainer(title2=title)
#     object_container.header  = 'Remove from Favorites'
#     object_container.message = '{0} removed from Favorites'.format(show_title)
#     return object_container

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
    tracking.track('/TV Shows/Episode', { 'Title': show_title, 'Season': season_index, 'Episode': episode_index })

    object_container = ObjectContainer()

    json_url  = Prefs['SCRAPYARD_URL'] + '/api/show/' + trakt_slug + '/season/' + str(season_index) + '/episode/' + str(episode_index)
    json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

    if json_data and 'magnets' in json_data:
        for json_item in json_data['magnets']:
            episode_object = EpisodeObject()
            SharedCodeService.common.fill_episode_object(episode_object, json_data)
            episode_object.title   = json_item['title']
            episode_object.summary = 'Seeds: {0}, Peers: {1}\n\n{2}'.format(json_item['seeds'], json_item['peers'], episode_object.summary)
            episode_object.url     = json_url + '?magnet=' + String.Quote(json_item['link'])
            object_container.add(episode_object)

    return object_container
