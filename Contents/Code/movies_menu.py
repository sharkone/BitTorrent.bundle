################################################################################

from DumbTools import DumbKeyboard

################################################################################
SUBPREFIX = 'movies'

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu(**kwargs):
    object_container = ObjectContainer(title2='Movies')
    object_container.add(DirectoryObject(key=Callback(movies_menu, title='Recent', page='/movies', sort='last%20added', page_index=1), title='Recent', summary='Browse recent movies.'))
    object_container.add(DirectoryObject(key=Callback(movies_menu, title='Trending', page='/movies', sort='trending', page_index=1), title='Trending', summary='Browse trending movies.'))
    object_container.add(DirectoryObject(key=Callback(movies_menu, title='Popular', page='/movies', sort='', page_index=1), title='Popular', summary='Browse popular movies.'))
    object_container.add(DirectoryObject(key=Callback(watchlist_menu, title='Watchlist'), title='Watchlist', summary='Browse your watchlist', thumb=R('favorites.png')))

    if Client.Product in DumbKeyboard.clients:
        DumbKeyboard(SharedCodeService.common.PREFIX + '/' + SUBPREFIX, object_container, search_menu, dktitle='Search', dkthumb=R('search.png'), title='Search')
    else:
        object_container.add(InputDirectoryObject(key=Callback(search_menu, title='Search'), title='Search', summary='Search movies', thumb=R('search.png'), prompt='Search for movies'))
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/movies', page_index=int)
def movies_menu(title, page, sort, page_index, **kwargs):
    object_container = ObjectContainer(title2=title)

    json_url  = SharedCodeService.common.POPCORN_API + page + '/{0}?sort={1}'.format(page_index, sort)
    json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR, headers=SharedCodeService.common.HEADERS)

    if json_data:
        for json_item in json_data:
            object_container.add(create_directory_object(json_item))

    if (page_index + 1) <= 10:
        object_container.add(NextPageObject(key=Callback(movies_menu, title=title, page=page, sort=sort, page_index=page_index + 1), title="More..."))

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/watchlist')
def watchlist_menu(title, **kwargs):
    ids = Dict['MOVIES_WATCHLIST'] if 'MOVIES_WATCHLIST' in Dict else []

    object_container = ObjectContainer(title2=title)

    for id in ids:
        json_url  = SharedCodeService.common.POPCORN_API + '/movie/' + id
        json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR, headers=SharedCodeService.common.HEADERS)

        if json_data:
            object_container.add(create_directory_object(json_data))

    object_container.objects.sort(key=lambda directory_object: directory_object.title)
    object_container.add(DirectoryObject(key=Callback(reset_watchlist_menu, title='Reset Watchlist'), title='Reset Watchlist', summary='Reset Watchlist'))
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search_menu(title, query, **kwargs):
    object_container = ObjectContainer(title2=title)

    json_url  = SharedCodeService.common.POPCORN_API + '/movies/1?keywords={0}'.format(String.Quote(query))
    json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR, headers=SharedCodeService.common.HEADERS)

    if json_data:
        for json_item in json_data:
            object_container.add(create_directory_object(json_item))

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/movie')
def movie_menu(title, id, **kwargs):
    object_container = ObjectContainer(title2=title)

    if 'MOVIES_WATCHLIST' in Dict and id in Dict['MOVIES_WATCHLIST']:
        object_container.add(DirectoryObject(key=Callback(remove_from_watchlist, title='Remove from Watchlist', movie_title=title, id=id), title='Remove from Watchlist', summary='Remove movie from Watchlist', thumb=R('favorites.png')))
    else:
        object_container.add(DirectoryObject(key=Callback(add_to_watchlist, title='Add to Watchlist', movie_title=title, id=id), title='Add to Watchlist', summary='Add movie to Watchlist', thumb=R('favorites.png')))

    json_url  = SharedCodeService.common.POPCORN_API + '/movie/' + id
    json_data = JSON.ObjectFromURL(json_url, cacheTime=CACHE_1HOUR, headers=SharedCodeService.common.HEADERS)

    if json_data and 'torrents' in json_data and 'en' in json_data['torrents']:
        for key, json_item in json_data['torrents']['en'].iteritems():
            movie_object = MovieObject()
            SharedCodeService.common.fill_movie_object(movie_object, json_data)
            movie_object.title   = SharedCodeService.common.fix_movie_torrent_title(json_data, key, json_item)
            movie_object.summary = 'Seeds: {0} - Peers: {1}\nSize: {2}\n\n{3}'.format(json_item['seed'], json_item['peer'], json_item['filesize'], movie_object.summary)
            movie_object.url     = json_url + '?magnet=' + String.Quote(json_item['url'])
            object_container.add(movie_object)

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/add_to_watchlist')
def add_to_watchlist(title, movie_title, id, **kwargs):
    if 'MOVIES_WATCHLIST' not in Dict:
        Dict['MOVIES_WATCHLIST'] = []

    if id not in Dict['MOVIES_WATCHLIST']:
        Dict['MOVIES_WATCHLIST'].append(id)
        Dict.Save()

    object_container = ObjectContainer(title2=title)
    object_container.header  = 'Add to Watchlist'
    object_container.message = '{0} added to Watchlist'.format(movie_title)
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/remove_from_watchlist')
def remove_from_watchlist(title, movie_title, id, **kwargs):
    if 'MOVIES_WATCHLIST' in Dict and id in Dict['MOVIES_WATCHLIST']:
        Dict['MOVIES_WATCHLIST'].remove(id)
        Dict.Save()

    object_container = ObjectContainer(title2=title)
    object_container.header  = 'Remove from Watchlist'
    object_container.message = '{0} removed from Watchlist'.format(movie_title)
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/reset_watchlist_menu')
def reset_watchlist_menu(title, **kwargs):
    object_container = ObjectContainer(title2=title)
    object_container.header = 'Reset Watchlist'
    object_container.add(DirectoryObject(key=Callback(reset_watchlist, title='Confirm'), title='Confirm', summary='Reset Watchlist Confirmation'))
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/reset_watchlist')
def reset_watchlist(title, **kwargs):
    if 'MOVIES_WATCHLIST' in Dict:
        Dict['MOVIES_WATCHLIST'] = []
        Dict.Save()

    object_container = ObjectContainer(title2=title)
    object_container.message = 'Watchlist has been reset'
    return object_container

################################################################################
def create_directory_object(json_item):
    directory_object          = DirectoryObject()
    directory_object.title    = json_item['title'] if 'title' in json_item else ''
    directory_object.summary  = json_item['synopsis'] if 'synopsis' in json_item else ''
    directory_object.duration = int(json_item['runtime']) * 60 * 60 * 1000 if 'runtime' in json_item else 0
    if 'images' in json_item:
        directory_object.thumb    = json_item['images']['poster'] if 'poster' in json_item['images'] else ''
        directory_object.art      = json_item['images']['fanart'] if 'fanart' in json_item['images'] else ''
    directory_object.key      = Callback(movie_menu, title=directory_object.title, id=json_item['_id']) if '_id' in json_item else ''
    return directory_object
