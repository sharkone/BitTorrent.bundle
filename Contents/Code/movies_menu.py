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
    object_container.add(DirectoryObject(key=Callback(popular, per_page=31), title='Popular'))
    object_container.add(InputDirectoryObject(key=Callback(search), title='Search', thumb=R('search.png')))
    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/popular', per_page=int, movie_count=int)
def popular(per_page, movie_count=0):
    torrent_infos = []

    # KAT
    # kat_rss_url  = 'http://kickass.to/movies/?field=seeders&sorder=desc&rss=1'
    # kat_rss_data = RSS.FeedFromURL(kat_rss_url, cacheTime=CACHE_1HOUR)

    # for kat_rss_entry in kat_rss_data.entries:
    #     torrent_info = SharedCodeService.movies.TorrentInfo(kat_rss_entry.torrent_magneturi,
    #                                                         kat_rss_entry.title, 
    #                                                         int(kat_rss_entry.torrent_seeds),
    #                                                         int(kat_rss_entry.torrent_peers),
    #                                                         kat_rss_entry.link)
        
    #     if not [t for t in torrent_infos if torrent_info.info_hash == t.info_hash]:
    #         torrent_infos.append(torrent_info)

    # TPB
    # tpb_html_url  = 'http://thepiratebay.se/top/201'
    # tpb_html_data = HTML.ElementFromURL(tpb_html_url, cacheTime=CACHE_1HOUR)

    # for tpb_html_item in tpb_html_data.xpath('//*[@id="searchResult"]/tr'):
    #     torrent_info = SharedCodeService.movies.TorrentInfo(tpb_html_item.xpath('./td[2]/a[1]/@href')[0],
    #                                                         tpb_html_item.xpath('./td[2]/div/a/text()')[0],
    #                                                         int(tpb_html_item.xpath('./td[3]/text()')[0]),
    #                                                         int(tpb_html_item.xpath('./td[4]/text()')[0]),
    #                                                         'http://thepiratebay.se' + tpb_html_item.xpath('./td[2]/div/a/@href')[0])

    #     if not [t for t in torrent_infos if torrent_info.info_hash == t.info_hash]:
    #         torrent_infos.append(torrent_info)

    tpb_hd_html_url  = 'http://thepiratebay.se/top/207'
    tpb_hd_html_data = HTML.ElementFromURL(tpb_hd_html_url, cacheTime=CACHE_1HOUR)

    for tpb_hd_html_item in tpb_hd_html_data.xpath('//*[@id="searchResult"]/tr'):
        torrent_info = SharedCodeService.movies.TorrentInfo(tpb_hd_html_item.xpath('./td[2]/a[1]/@href')[0],
                                                            tpb_hd_html_item.xpath('./td[2]/div/a/text()')[0],
                                                            int(tpb_hd_html_item.xpath('./td[3]/text()')[0]),
                                                            int(tpb_hd_html_item.xpath('./td[4]/text()')[0]),
                                                            'http://thepiratebay.se' + tpb_hd_html_item.xpath('./td[2]/div/a/@href')[0])

        if not [t for t in torrent_infos if torrent_info.info_hash == t.info_hash]:
            torrent_infos.append(torrent_info)

    #torrent_infos.sort(key=lambda torrent_info: torrent_info.seeders, reverse=True)

    movie_infos      = set()
    movie_infos_list = []
    movie_infos_skip = set()

    for torrent_info in torrent_infos:
        movie_info = SharedCodeService.movies.MovieInfo(torrent_info.title)
        
        if len(movie_infos_skip) < movie_count:
            movie_infos_skip.add(movie_info.key)
        else:
            if not movie_info.key in movie_infos_skip and not movie_info.key in movie_infos:
                movie_infos.add(movie_info.key)
                movie_infos_list.append(movie_info)
                if len(movie_infos_list) == per_page:
                    break

    object_container = ObjectContainer(title2='Popular')
    parse_movie_infos(object_container, movie_infos_list)
    object_container.add(NextPageObject(key=Callback(popular, per_page=per_page, movie_count=len(movie_infos_skip) + len(movie_infos)), title="More..."))

    return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search(query):
    movie_infos      = set()
    movie_infos_list = []

    # KAT
    rss_url  = 'http://kickass.to/usearch/category%3Amovies%20{0}/?field=seeders&sorder=desc&rss=1'.format(String.Quote(query))
    rss_data = RSS.FeedFromURL(rss_url, cacheTime=CACHE_1HOUR)

    for rss_entry in rss_data.entries:
        movie_info = SharedCodeService.movies.MovieInfo(rss_entry.title)
        if not movie_info.key in movie_infos:
            movie_infos.add(movie_info.key)
            movie_infos_list.append(movie_info)

    # TPB
    html_url  = 'http://thepiratebay.se/search/{0}/0/7/200'.format(String.Quote(query))
    html_data = HTML.ElementFromURL(html_url, cacheTime=CACHE_1HOUR)

    for html_item in html_data.xpath('//*[@id="searchResult"]/tr'):
        movie_info = SharedCodeService.movies.MovieInfo(html_item.xpath('./td[2]/div/a/text()')[0])
        if not movie_info.key in movie_infos:
            movie_infos.add(movie_info.key)
            movie_infos_list.append(movie_info)

    object_container = ObjectContainer(title2='Search')
    parse_movie_infos(object_container, movie_infos_list)
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
            torrent_info = SharedCodeService.movies.TorrentInfo(rss_entry.torrent_magneturi,
                                                                rss_entry.title,
                                                                int(rss_entry.torrent_seeds),
                                                                int(rss_entry.torrent_peers),
                                                                rss_entry.link)
    
            if SharedCodeService.movies.MovieInfo(torrent_info.title).key != movie_info.key:
                continue
    
            if not [t for t in torrent_infos if torrent_info.info_hash == t.info_hash]:
                torrent_infos.append(torrent_info)

    except Exception as exception:
        Log.Error('[Bittorrent][movies] Unhandled exception: {0}'.format(exception))

    # TPB
    try:
        html_url  = 'http://thepiratebay.se/search/{0}/0/7/200'.format(SharedCodeService.tmdb.get_imdb_id_from_title(movie_info.title, movie_info.year))
        html_data = HTML.ElementFromURL(html_url, cacheTime=CACHE_1HOUR)

        for html_item in html_data.xpath('//*[@id="searchResult"]/tr'):
            torrent_info = SharedCodeService.movies.TorrentInfo(html_item.xpath('./td[2]/a[1]/@href')[0],
                                                                html_item.xpath('./td[2]/div/a/text()')[0],
                                                                int(html_item.xpath('./td[3]/text()')[0]),
                                                                int(html_item.xpath('./td[4]/text()')[0]),
                                                                'http://thepiratebay.se' + html_item.xpath('./td[2]/div/a/@href')[0])

            if SharedCodeService.movies.MovieInfo(torrent_info.title).key != movie_info.key:
                continue

            if not [t for t in torrent_infos if torrent_info.info_hash == t.info_hash]:
                torrent_infos.append(torrent_info)

    except Exception as exception:
        Log.Error('[Bittorrent][movies] Unhandled exception: {0}'.format(exception))

    torrent_infos.sort(key=lambda torrent_info: torrent_info.seeders, reverse=True)

    object_container = ObjectContainer(title2=movie_info.title)
    parse_torrent_infos(object_container, movie_info, torrent_infos)
    return object_container

################################################################################
def parse_movie_infos(object_container, movie_infos_list):
    for movie_info in movie_infos_list:
        directory_object         = DirectoryObject()
        directory_object.title   = movie_info.title

        if movie_info.tmdb_id:
            SharedCodeService.tmdb.fill_metadata_object(directory_object, movie_info.tmdb_id)
        elif not ALLOW_UNRECOGNIZED:
            continue

        directory_object.key = Callback(movie, movie_info=movie_info.to_dict())
        object_container.add(directory_object)

################################################################################
def parse_torrent_infos(object_container, movie_info, torrent_infos):
    torrent_infos.sort(key=lambda torrent_info: torrent_info.seeders, reverse=True)

    for torrent_info in torrent_infos:
        seeders_leechers_line = 'Seeders: {0}, Leechers: {1}'.format(torrent_info.seeders, torrent_info.leechers)

        movie_object         = MovieObject()
        movie_object.title   = movie_info.title
        movie_object.summary = seeders_leechers_line

        if movie_info.tmdb_id:
            SharedCodeService.tmdb.fill_metadata_object(movie_object, movie_info.tmdb_id)
            movie_object.title   = torrent_info.title
            movie_object.summary = '{0}\n\n{1}'.format(seeders_leechers_line, movie_object.summary)
            #movie_object.summary = '{3}\n{2}\n{0}\n\n{1}'.format(seeders_leechers_line, movie_object.summary, torrent_info['info_hash'], torrent_info['title'])

        movie_object.url = torrent_info.url

        object_container.add(movie_object)
