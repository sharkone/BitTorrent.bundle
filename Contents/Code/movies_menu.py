################################################################################
import re

################################################################################
SUBPREFIX = 'movies'

################################################################################
ALLOW_UNRECOGNIZED = False

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
    object_container = ObjectContainer(title2='Movies')
    object_container.add(DirectoryObject(key=Callback(popular), title='Popular'))
    object_container.add(InputDirectoryObject(key=Callback(search), title='Search', thumb=R('search.png')))
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/popular', page_index=int)
def popular(page_index=1):
    movie_infos = {}

    # KAT
    rss_url  = 'http://kickass.to/movies/{0}?field=seeders&sorder=desc&rss=1'.format(page_index)
    rss_data = RSS.FeedFromURL(rss_url, cacheTime=CACHE_1HOUR)

    for rss_entry in rss_data.entries:
        movie_info = SharedCodeService.movies.MovieInfo(rss_entry.title)
        if not movie_info.key in movie_infos:
            movie_infos[movie_info.key] = movie_info
        movie_infos[movie_info.key].seeders  = movie_infos[movie_info.key].seeders  + int(rss_entry.torrent_seeds)
        movie_infos[movie_info.key].leechers = movie_infos[movie_info.key].leechers + int(rss_entry.torrent_peers)

    # TPB
    html_url  = 'http://thepiratebay.se/top/201'
    html_data = HTML.ElementFromURL(html_url, cacheTime=CACHE_1HOUR)

    for html_item in html_data.xpath('//*[@id="searchResult"]/tr'):
        movie_info = SharedCodeService.movies.MovieInfo(html_item.xpath('./td[2]/div/a/text()')[0])
        if not movie_info.key in movie_infos:
            movie_infos[movie_info.key] = movie_info
        movie_infos[movie_info.key].seeders  = movie_infos[movie_info.key].seeders  + int(html_item.xpath('./td[3]/text()')[0])
        movie_infos[movie_info.key].leechers = movie_infos[movie_info.key].leechers + int(html_item.xpath('./td[4]/text()')[0])

    html_url  = 'http://thepiratebay.se/top/207'
    html_data = HTML.ElementFromURL(html_url, cacheTime=CACHE_1HOUR)

    for html_item in html_data.xpath('//*[@id="searchResult"]/tr'):
        movie_info = SharedCodeService.movies.MovieInfo(html_item.xpath('./td[2]/div/a/text()')[0])
        if not movie_info.key in movie_infos:
            movie_infos[movie_info.key] = movie_info
        movie_infos[movie_info.key].seeders  = movie_infos[movie_info.key].seeders  + int(html_item.xpath('./td[3]/text()')[0])
        movie_infos[movie_info.key].leechers = movie_infos[movie_info.key].leechers + int(html_item.xpath('./td[4]/text()')[0])

    object_container = ObjectContainer(title2='Popular')
    parse_movie_infos(object_container, movie_infos)
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search(query):
    movie_infos = {}

    # KAT
    rss_url  = 'http://kickass.to/usearch/category%3Amovies%20{0}/?field=seeders&sorder=desc&rss=1'.format(String.Quote(query))
    rss_data = RSS.FeedFromURL(rss_url, cacheTime=CACHE_1HOUR)

    for rss_entry in rss_data.entries:
        movie_info = SharedCodeService.movies.MovieInfo(rss_entry.title)
        movie_infos[movie_info.key] = movie_info

    # TPB
    html_url  = 'http://thepiratebay.se/search/{0}/0/7/200'.format(String.Quote(query))
    html_data = HTML.ElementFromURL(html_url, cacheTime=CACHE_1HOUR)

    for html_item in html_data.xpath('//*[@id="searchResult"]/tr'):
        movie_info = SharedCodeService.movies.MovieInfo(html_item.xpath('./td[2]/div/a/text()')[0])
        movie_infos[movie_info.key] = movie_info

    object_container = ObjectContainer(title2='Popular')
    parse_movie_infos(object_container, movie_infos)
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/movie', movie_info=dict)
def movie(movie_info):
    movie_info    = SharedCodeService.movies.MovieInfo.from_dict(movie_info)
    torrent_infos = []
    
    # KAT
    try:
        rss_url  = 'http://kickass.to/usearch/imdb%3A{0}/?field=seeders&sorder=desc&rss=1'.format(movie_info.imdb_id[2:])
        rss_data = RSS.FeedFromURL(rss_url, cacheTime=CACHE_1HOUR)

        for rss_entry in rss_data.entries:
            SharedCodeService.movies.add_torrent_to_torrent_infos(torrent_infos,
                                                                  rss_entry.title,
                                                                  rss_entry.link,
                                                                  rss_entry.torrent_magneturi,
                                                                  int(rss_entry.torrent_seeds),
                                                                  int(rss_entry.torrent_peers))
    except Exception as exception:
        Log.Error('[Bittorrent][movies] Unhandled exception: {0}'.format(exception))

    # TPB
    try:
        html_url  = 'http://thepiratebay.se/search/{0}/0/7/200'.format(SharedCodeService.tmdb.get_imdb_id_from_title(movie_info.title, movie_info.year))
        html_data = HTML.ElementFromURL(html_url, cacheTime=CACHE_1HOUR)

        for html_item in html_data.xpath('//*[@id="searchResult"]/tr'):
            SharedCodeService.movies.add_torrent_to_torrent_infos(torrent_infos,
                                                                  html_item.xpath('./td[2]/div/a/text()')[0],
                                                                  'http://thepiratebay.se' + html_item.xpath('./td[2]/div/a/@href')[0],
                                                                  html_item.xpath('./td[2]/a[1]/@href')[0],
                                                                  int(html_item.xpath('./td[3]/text()')[0]),
                                                                  int(html_item.xpath('./td[4]/text()')[0]))
    except Exception as exception:
        Log.Error('[Bittorrent][movies] Unhandled exception: {0}'.format(exception))

    torrent_infos.sort(key=lambda torrent_info: torrent_info['seeders'], reverse=True)

    object_container = ObjectContainer(title2=movie_info.title)
    parse_torrent_infos(object_container, movie_info, torrent_infos)
    return object_container

################################################################################
def parse_movie_infos(object_container, movie_infos):
    movie_infos_list = list(movie_infos.values())
    movie_infos_list.sort(key=lambda movie_info: movie_info.seeders, reverse=True)

    for movie_info in movie_infos_list:
        seeders_leechers_line = 'Seeders: {0}, Leechers: {1}'.format(movie_info.seeders, movie_info.leechers)

        directory_object         = DirectoryObject()
        directory_object.title   = movie_info.title
        directory_object.summary = seeders_leechers_line

        if movie_info.tmdb_id:
            SharedCodeService.tmdb.fill_metadata_object(directory_object, movie_info.tmdb_id)
        elif not ALLOW_UNRECOGNIZED:
            continue

        directory_object.summary = '{0}\n\n{1}'.format(seeders_leechers_line, directory_object.summary)

        directory_object.key = Callback(movie, movie_info=movie_info.to_dict())
        object_container.add(directory_object)

################################################################################
def parse_torrent_infos(object_container, movie_info, torrent_infos):
    torrent_infos.sort(key=lambda torrent_info: torrent_info['seeders'], reverse=True)

    for torrent_info in torrent_infos:
        seeders_leechers_line = 'Seeders: {0}, Leechers: {1}'.format(torrent_info['seeders'], torrent_info['leechers'])

        movie_object         = MovieObject()
        movie_object.title   = movie_info.title
        movie_object.summary = seeders_leechers_line

        if movie_info.tmdb_id:
            SharedCodeService.tmdb.fill_metadata_object(movie_object, movie_info.tmdb_id)
            movie_object.title = torrent_info['release']

        movie_object.url     = torrent_info['url']
        movie_object.summary = '{0}\n\n{1}'.format(seeders_leechers_line, movie_object.summary)

        object_container.add(movie_object)
