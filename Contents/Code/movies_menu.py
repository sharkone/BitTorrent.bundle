################################################################################

from DumbTools import DumbKeyboard

################################################################################
SUBPREFIX = 'movies'

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
    object_container = ObjectContainer(title2='Movies')
    object_container.add(DirectoryObject(key=Callback(movies_menu, title='Trending', page='/api/movies/trending', page_index=1), title='Trending', summary='Browse movies currently being watched.'))
    object_container.add(DirectoryObject(key=Callback(movies_menu, title='Popular', page='/api/movies/popular', page_index=1), title='Popular', summary='Browse most popular movies.'))
    object_container.add(DirectoryObject(key=Callback(watchlist_menu, title='Watchlist'), title='Watchlist', summary='Browse your watchlist', thumb=R('favorites.png')))

    if Client.Product in DumbKeyboard.clients:
        DumbKeyboard(SharedCodeService.common.PREFIX + '/' + SUBPREFIX, object_container, search_menu, dktitle='Search', dkthumb=R('search.png'), title='Search')
    else:
        object_container.add(InputDirectoryObject(key=Callback(search_menu, title='Search'), title='Search', summary='Search movies', thumb=R('search.png'), prompt='Search for movies'))
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/movies', page_index=int)
def movies_menu(title, page, page_index):
    object_container = ObjectContainer(title2=title)

    json_url  = Prefs['SCRAPYARD_URL'] + page + '?page={0}'.format(page_index)
    json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

    if json_data and 'movies' in json_data:
        for json_item in json_data['movies']:
            directory_object          = DirectoryObject()
            directory_object.title    = json_item['title']
            directory_object.summary  = json_item['overview']
            directory_object.tagline  = json_item['tagline']
            directory_object.duration = json_item['runtime']
            directory_object.thumb    = json_item['thumb']
            directory_object.art      = json_item['art']
            directory_object.key      = Callback(movie_menu, title=directory_object.title, trakt_slug=json_item['trakt_slug'])
            object_container.add(directory_object)

    if (page_index + 1) <= 10:
        object_container.add(NextPageObject(key=Callback(movies_menu, title=title, page=page, page_index=page_index + 1), title="More..."))

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/watchlist')
def watchlist_menu(title):
    trakt_slugs = Dict['movies_watchlist'] if 'movies_watchlist' in Dict else []

    object_container = ObjectContainer(title2=title)

    json_url  = Prefs['SCRAPYARD_URL'] + '/api/movies/watchlist?'
    json_post = { 'movies_watchlist': JSON.StringFromObject(trakt_slugs) }
    json_data = JSON.ObjectFromURL(json_url, values=json_post, cacheTime=CACHE_1HOUR)

    if json_data and 'movies' in json_data:
        for json_item in json_data['movies']:
            directory_object          = DirectoryObject()
            directory_object.title    = json_item['title']
            directory_object.summary  = json_item['overview']
            directory_object.tagline  = json_item['tagline']
            directory_object.duration = json_item['runtime']
            directory_object.thumb    = json_item['thumb']
            directory_object.art      = json_item['art']
            directory_object.key      = Callback(movie_menu, title=directory_object.title, trakt_slug=json_item['trakt_slug'])
            object_container.add(directory_object)

    object_container.objects.sort(key=lambda directory_object: directory_object.title)

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search_menu(title, query):
    object_container = ObjectContainer(title2=title)

    json_url  = Prefs['SCRAPYARD_URL'] + '/api/movies/search?query=' + String.Quote(query)
    json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

    if json_data and 'movies' in json_data:
        for json_item in json_data['movies']:
            directory_object          = DirectoryObject()
            directory_object.title    = json_item['title']
            directory_object.summary  = json_item['overview']
            directory_object.tagline  = json_item['tagline']
            directory_object.duration = json_item['runtime']
            directory_object.thumb    = json_item['thumb']
            directory_object.art      = json_item['art']
            directory_object.key      = Callback(movie_menu, title=directory_object.title, trakt_slug=json_item['trakt_slug'])
            object_container.add(directory_object)

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/movie')
def movie_menu(title, trakt_slug):
    object_container = ObjectContainer(title2=title)

    if 'movies_watchlist' in Dict and trakt_slug in Dict['movies_watchlist']:
        object_container.add(DirectoryObject(key=Callback(remove_from_watchlist, title='Remove from Watchlist', movie_title=title, trakt_slug=trakt_slug), title='Remove from Watchlist', summary='Remove movie from Watchlist', thumb=R('favorites.png')))
    else:
        object_container.add(DirectoryObject(key=Callback(add_to_watchlist, title='Add to Watchlist', movie_title=title, trakt_slug=trakt_slug), title='Add to Watchlist', summary='Add movie to Watchlist', thumb=R('favorites.png')))

    json_url  = Prefs['SCRAPYARD_URL'] + '/api/movie/' + trakt_slug
    json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR)

    if json_data and 'magnets' in json_data:
        for json_item in json_data['magnets']:
            movie_object = MovieObject()
            SharedCodeService.common.fill_movie_object(movie_object, json_data)
            movie_object.title   = json_item['title']
            movie_object.summary = 'Seeds: {0} - Peers: {1}\nSize: {2}\nSource: {3}\n\n{4}'.format(json_item['seeds'], json_item['peers'], SharedCodeService.utils.get_magnet_size_str(json_item), json_item['source'], movie_object.summary)
            movie_object.url     = json_url + '?magnet=' + String.Quote(json_item['link'])
            object_container.add(movie_object)

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/add_to_watchlist')
def add_to_watchlist(title, movie_title, trakt_slug):
    if 'movies_watchlist' not in Dict:
        Dict['movies_watchlist'] = []

    if trakt_slug not in Dict['movies_watchlist']:
        Dict['movies_watchlist'].append(trakt_slug)
        Dict.Save()

    object_container = ObjectContainer(title2=title)
    object_container.header  = 'Add to Watchlist'
    object_container.message = '{0} added to Watchlist'.format(movie_title)
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/remove_from_watchlist')
def remove_from_watchlist(title, movie_title, trakt_slug):
    if 'movies_watchlist' in Dict and trakt_slug in Dict['movies_watchlist']:
        Dict['movies_watchlist'].remove(trakt_slug)
        Dict.Save()

    object_container = ObjectContainer(title2=title)
    object_container.header  = 'Remove from Watchlist'
    object_container.message = '{0} removed from Watchlist'.format(movie_title)
    return object_container
