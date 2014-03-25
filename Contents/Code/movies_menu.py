################################################################################
SUBPREFIX = 'movies'

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

    object_container = ObjectContainer(title2='Popular')
    movie_count      = fill_object_container(object_container, torrent_infos, movie_count, per_page)
    
    object_container.add(NextPageObject(key=Callback(popular, per_page=per_page, movie_count=movie_count), title="More..."))
    
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search(query, per_page, movie_count=0):
    torrent_infos = []

    torrent_provider = SharedCodeService.metaprovider.MetaProvider()
    torrent_provider.movies_search(query, torrent_infos)

    object_container = ObjectContainer(title2='Search')
    movie_count      = fill_object_container(object_container, torrent_infos, movie_count, per_page)

    object_container.add(NextPageObject(key=Callback(search, per_page=per_page, movie_count=movie_count), title="More..."))

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/movie')
def movie(imdb_id):
    torrent_infos = []
    
    torrent_provider = SharedCodeService.metaprovider.MetaProvider()
    torrent_provider.movies_get_specific_torrents(imdb_id, torrent_infos)

    torrent_infos.sort(key=lambda torrent_info: torrent_info.seeders, reverse=True)

    object_container = ObjectContainer()
    
    for torrent_info in torrent_infos:
        seeders_leechers_line = '{0}\nSeeders: {1}, Leechers: {2}'.format(torrent_info.size, torrent_info.seeders, torrent_info.leechers)

        movie_object = MovieObject()

        SharedCodeService.tmdb.fill_metadata_object(movie_object, imdb_id)
        object_container.title2 = movie_object.title

        movie_object.title    = torrent_info.release
        movie_object.summary  = '{0}\n\n{1}'.format(seeders_leechers_line, movie_object.summary) 
        movie_object.url      = torrent_info.url

        object_container.add(movie_object)

    return object_container

################################################################################
def fill_object_container(object_container, torrent_infos, cur_movie_count, max_movie_count):
    torrent_infos.sort(key=lambda torrent_info: torrent_info.seeders, reverse=True)

    imdb_ids      = []
    imdb_ids_skip = set()

    for torrent_info in torrent_infos:
        if torrent_info.category == 'movies':
            imdb_id = torrent_info.key

            if len(imdb_ids_skip) < cur_movie_count:
                imdb_ids_skip.add(imdb_id)
            else:
                if imdb_id not in imdb_ids and imdb_id not in imdb_ids_skip:
                    imdb_ids.append(imdb_id)
                    if len(imdb_ids) == max_movie_count:
                        break

    for imdb_id in imdb_ids:
        directory_object = DirectoryObject()

        SharedCodeService.tmdb.fill_metadata_object(directory_object, imdb_id)
        if not directory_object.title:
            continue

        directory_object.key = Callback(movie, imdb_id=imdb_id)
        object_container.add(directory_object)

    return len(imdb_ids_skip) + len(imdb_ids)
