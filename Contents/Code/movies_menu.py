################################################################################
SUBPREFIX = 'movies'

################################################################################
ALLOW_UNRECOGNIZED = False

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
    object_container = ObjectContainer(title2='Movies')
    object_container.add(DirectoryObject(key=Callback(popular, per_page=31), title='Popular'))
    object_container.add(InputDirectoryObject(key=Callback(search, per_page=31), title='Search', thumb=R('search.png')))
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/popular', per_page=int, movie_count=int)
def popular(per_page, movie_count=0):
    torrent_infos = []

    torrent_provider = SharedCodeService.metaprovider.MetaProvider()
    torrent_provider.movies_get_popular_torrents(torrent_infos)

    movie_infos = []
    movie_count = fill_movie_list(torrent_infos, movie_count, per_page, movie_infos)

    object_container = ObjectContainer(title2='Popular')
    parse_movie_infos(object_container, movie_infos)
    object_container.add(NextPageObject(key=Callback(popular, per_page=per_page, movie_count=movie_count), title="More..."))
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search(query, per_page, movie_count=0):
    torrent_infos = []

    torrent_provider = SharedCodeService.metaprovider.MetaProvider()
    torrent_provider.movies_search(query, torrent_infos)

    movie_infos = []
    movie_count = fill_movie_list(torrent_infos, movie_count, per_page, movie_infos)

    object_container = ObjectContainer(title2='Search')
    parse_movie_infos(object_container, movie_infos)
    #object_container.add(NextPageObject(key=Callback(search, per_page=per_page, movie_count=movie_count), title="More..."))
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/movie', movie_info=dict)
def movie(movie_info):
    movie_info    = SharedCodeService.movies.MovieInfo.from_dict(movie_info)
    torrent_infos = []
    
    torrent_provider = SharedCodeService.metaprovider.MetaProvider()
    torrent_provider.movies_get_specific_torrents(movie_info, torrent_infos)

    torrent_infos.sort(key=lambda torrent_info: torrent_info.seeders, reverse=True)

    object_container = ObjectContainer(title2=movie_info.title)
    for torrent_info in torrent_infos:
        seeders_leechers_line = '{0}\nSeeders: {1}, Leechers: {2}'.format(torrent_info.size, torrent_info.seeders, torrent_info.leechers)

        movie_object         = MovieObject()
        movie_object.title   = movie_info.title
        movie_object.summary = seeders_leechers_line

        if movie_info.tmdb_id:
            SharedCodeService.tmdb.fill_metadata_object(movie_object, movie_info.tmdb_id)
            movie_object.title = torrent_info.release

            if seeders_leechers_line != movie_object.summary:
                movie_object.summary = '{0}\n\n{1}'.format(seeders_leechers_line, movie_object.summary) 
                #movie_object.summary = '{3}\n{2}\n{0}\n\n{1}'.format(seeders_leechers_line, movie_object.summary, torrent_info['info_hash'], torrent_info['title'])

        movie_object.url = torrent_info.url

        object_container.add(movie_object)

    return object_container

################################################################################
def fill_movie_list(torrent_infos, cur_movie_count, max_movie_count, movie_infos):
    torrent_infos.sort(key=lambda torrent_info: torrent_info.seeders, reverse=True)

    movie_infos_keys      = set()
    movie_infos_skip_keys = set()

    for torrent_info in torrent_infos:
        movie_info = SharedCodeService.movies.MovieInfo(torrent_info.title)
        
        if movie_info.tmdb_id or ALLOW_UNRECOGNIZED:
            if len(movie_infos_skip_keys) < cur_movie_count:
                movie_infos_skip_keys.add(movie_info.key)
            else:
                if not movie_info.key in movie_infos_skip_keys and not movie_info.key in movie_infos_keys:
                    movie_infos_keys.add(movie_info.key)
                    movie_infos.append(movie_info)
                    if len(movie_infos) == max_movie_count:
                        break

    return len(movie_infos_skip_keys) + len(movie_infos_keys)

################################################################################
def parse_movie_infos(object_container, movie_infos):
    for movie_info in movie_infos:
        directory_object         = DirectoryObject()
        directory_object.title   = movie_info.title

        if movie_info.tmdb_id:
            SharedCodeService.tmdb.fill_metadata_object(directory_object, movie_info.tmdb_id)

        directory_object.key = Callback(movie, movie_info=movie_info.to_dict())
        object_container.add(directory_object)

