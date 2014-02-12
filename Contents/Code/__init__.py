################################################################################
import os
import watcher

################################################################################
PREFIX = '/video/bittorrent'
TITLE  = 'BitTorrent'
ART    = 'art-default.jpg'
ICON   = 'icon-default.png'

################################################################################
def Start():
	HTTP.CacheTime         = CACHE_1DAY
	ObjectContainer.art    = R(ART)
	ObjectContainer.title1 = TITLE
	VideoClipObject.art    = R(ART)
	VideoClipObject.thumb  = R(ICON)
	Thread.Create(watcher.thread_proc, watch_directory=SharedCodeService.torrent2http.get_bin_dir(), timeout=Datetime.Delta(seconds=30))

################################################################################
@handler(PREFIX, TITLE)
def Main():
	object_container = ObjectContainer(title2=TITLE)
	object_container.add(DirectoryObject(key=Callback(ThePirateBay), title='The Pirate Bay', thumb=R('thepiratebay.png')))
	object_container.add(DirectoryObject(key=Callback(YTS), title="YTS", thumb=R('yts.png')))
	return object_container

################################################################################
@route(PREFIX + '/thepiratebay')
def ThePirateBay():
	object_container = ObjectContainer(title2='The Pirate Bay')
	object_container.add(InputDirectoryObject(key=Callback(ThePirateBay_Search, title='Search'), title='Search', thumb=R('search.png')))
	return object_container

################################################################################
@route(PREFIX + '/thepiratebay_search')
def ThePirateBay_Search(title, query=''):
	THEPIRATEBAY        = 'http://thepiratebay.se'
	THEPIRATEBAY_SEARCH = THEPIRATEBAY + '/search/{0}/0/7/200'

	url  = THEPIRATEBAY_SEARCH.format(String.Quote(query))
	html = HTML.ElementFromURL(url, cacheTime=0)
	
	object_container = ObjectContainer(title2=title)
	for item in html.xpath('//*[@id="searchResult"]/tr'):
		movie_url     = THEPIRATEBAY + item.xpath('./td[2]/div/a/@href')[0]
		movie_seeders = item.xpath('./td[3]/text()')[0]
		movie_peers   = item.xpath('./td[4]/text()')[0]
		movie_title   = '(S{0} | P{1}) {2}'.format(movie_seeders, movie_peers, item.xpath('./td[2]/div/a/text()')[0])
		movie_object  = MovieObject(url=movie_url, title=movie_title)
		object_container.add(movie_object)
	return object_container

################################################################################
@route(PREFIX + '/yts')
def YTS():
	object_container = ObjectContainer(title2='YTS')
	object_container.add(DirectoryObject(key=Callback(YTS_Search, title='Latest'), title='Latest', thumb=R('yts.png')))
	object_container.add(DirectoryObject(key=Callback(YTS_Genres, title='Genres'), title='Genres', thumb=R('yts.png')))
	object_container.add(DirectoryObject(key=Callback(YTS_Search, title='3D', only_3d=True), title='3D', thumb=R('yts.png')))
	object_container.add(InputDirectoryObject(key=Callback(YTS_Search, title='Search'), title='Search', thumb=R('search.png')))
	return object_container

################################################################################
@route(PREFIX + '/yts_search', only_3d=bool, page=int)
def YTS_Search(title, query='', genre='', only_3d=False, page=1):
	return YTS_Search_Internal(title, query, genre, only_3d, page)

################################################################################
@route(PREFIX + '/yts_genres')
def YTS_Genres(title):
	object_container = ObjectContainer(title2=title)
	genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'Film-Noir', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western']
	for genre in genres:
		object_container.add(DirectoryObject(key=Callback(YTS_Search, title=genre, genre=genre), title=genre, thumb=R('yts.png')))
	return object_container

################################################################################
def YTS_Search_Internal(title, query, genre, only_3d, page):
	YTS        = 'http://yts.re'
	YTS_SEARCH = YTS + '/api/list.json?limit=50&keywords={0}&genre={1}&quality={2}&set={3}'

	query   = String.Quote(query) if query   else ''
	genre   = String.Quote(genre) if genre   else ''
	quality = String.Quote('3D')  if only_3d else ''

	url  = YTS_SEARCH.format(query, genre, quality, str(page))
	json = JSON.ObjectFromURL(url, cacheTime=0)

	object_container = ObjectContainer(title2=title)
	for movie in json['MovieList']:
		if movie['Quality'] != '3D' or only_3d:
			movie_object     = SharedCodeService.tmdb.create_movie_object(movie['ImdbCode'], Callback(get_tmdb_art_async, imdb_id=movie['ImdbCode']), Callback(get_tmdb_thumb_async, imdb_id=movie['ImdbCode']))
			movie_object.url = movie['MovieUrl']
			object_container.add(movie_object)

	if (page * 50) < int(json['MovieCount']):
		object_container.add(NextPageObject(key=Callback(YTS_Search_Internal, title=title, query=query, genre=genre, only_3d=only_3d, page=page + 1), title="More..."))

	return object_container

################################################################################
@route(PREFIX + '/tmdb_get_art_async')
def get_tmdb_art_async(imdb_id):
	return SharedCodeService.tmdb.get_art(imdb_id)

################################################################################
@route(PREFIX + '/tmdb_get_thumb_async')
def get_tmdb_thumb_async(imdb_id):
	return SharedCodeService.tmdb.get_thumb(imdb_id)
