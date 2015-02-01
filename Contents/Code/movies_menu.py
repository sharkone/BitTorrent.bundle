################################################################################
import tracking

################################################################################
SUBPREFIX = 'movies'

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
    object_container = ObjectContainer(title2='Movies')
    object_container.add(DirectoryObject(key=Callback(movies_menu, title='Trending', page='/api/movies/trending', page_index=1, per_page=31), title='Trending', summary='Browse movies currently being watched.'))
    object_container.add(DirectoryObject(key=Callback(movies_menu, title='Popular', page='/api/movies/popular', page_index=1, per_page=31), title='Popular', summary='Browse most popular movies.'))
    object_container.add(InputDirectoryObject(key=Callback(search_menu, title='Search'), title='Search', summary='Search movies', thumb=R('search.png'), prompt='Search for movies'))
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/movies', page_index=int, per_page=int)
def movies_menu(title, page, page_index, per_page):
    object_container = ObjectContainer(title2=title)

    json_url  = Prefs['SCRAPYARD_URL'] + page + '?page={0}&limit={1}'.format(page_index, per_page)
    json_data = JSON.ObjectFromURL(json_url, cacheTime=0)

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
    
    object_container.add(NextPageObject(key=Callback(movies_menu, title=title, page=page, page_index=page_index + 1, per_page=per_page), title="More..."))
    
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search_menu(title, query):
    object_container = ObjectContainer(title2=title)

    json_url  = Prefs['SCRAPYARD_URL'] + '/api/movies/search?query=' + String.Quote(query)
    json_data = JSON.ObjectFromURL(json_url, cacheTime=0)

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
    tracking.track('/Movies/Movie', { 'Title': title })

    object_container = ObjectContainer(title2=title)

    json_url  = Prefs['SCRAPYARD_URL'] + '/api/movie/' + trakt_slug
    json_data = JSON.ObjectFromURL(json_url, cacheTime=0)

    if json_data and 'magnets' in json_data:
        for json_item in json_data['magnets']:
            movie_object = MovieObject()
            SharedCodeService.common.fill_movie_object(movie_object, json_data)
            movie_object.title   = json_item['title']
            movie_object.summary = 'Seeds: {0}, Peers: {1}\n\n{2}'.format(json_item['seeds'], json_item['peers'], movie_object.summary)
            movie_object.url     = json_url + '?magnet=' + String.Quote(json_item['link'])
            object_container.add(movie_object)

    return object_container
