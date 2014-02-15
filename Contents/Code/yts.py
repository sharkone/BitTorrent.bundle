################################################################################
import common
import tmdb

################################################################################
SUBPREFIX = 'yts'

YTS               = 'http://yts.re'
YTS_LIST          = YTS + '/api/list.json?limit=50&keywords={0}&genre={1}&quality={2}&set={3}'
YTS_LIST_VERSIONS = YTS + '/api/list.json?limit=50&keywords={0}'
YTS_MOVIE         = YTS + '/api/movie.json?id={0}'

################################################################################
@route(common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
	object_container = ObjectContainer(title2='YTS')
	object_container.add(DirectoryObject(key=Callback(search, title='Latest'), title='Latest', thumb=R('yts.png')))
	object_container.add(DirectoryObject(key=Callback(genres, title='Genres'), title='Genres', thumb=R('yts.png')))
	object_container.add(DirectoryObject(key=Callback(search, title='3D', only_3d=True), title='3D', thumb=R('yts.png')))
	object_container.add(InputDirectoryObject(key=Callback(search, title='Search'), title='Search', thumb=R('search.png')))
	return object_container

################################################################################
@route(common.PREFIX + '/' + SUBPREFIX + '/search', only_3d=bool)
def search(title, query='', genre='', only_3d=False):
	return search_internal(title, list(), query, genre, only_3d, 1)

################################################################################
@route(common.PREFIX + '/' + SUBPREFIX + '/search_internal', movie_list=list, only_3d=bool, page=int)
def search_internal(title, movie_list, query='', genre='', only_3d=False, page=1):
	query   = String.Quote(query) if query   else ''
	genre   = String.Quote(genre) if genre   else ''
	quality = String.Quote('3D')  if only_3d else ''

	if query == '__EMPTY__':
		query = ''
	if genre == '__EMPTY__':
		genre = ''

	url  = YTS_LIST.format(query, genre, quality, str(page))
	json = JSON.ObjectFromURL(url, cacheTime=0)

	object_container = ObjectContainer(title2=title)
	for movie in json['MovieList']:
		if movie['Quality'] != '3D' or only_3d:
			if movie['ImdbCode'] not in movie_list:
				movie_list.append(movie['ImdbCode'])
				movie_object = create_movie_object(movie['MovieUrl'], movie['TorrentMagnetUrl'], movie['ImdbCode'])
				object_container.add(movie_object)

	if (page * 50) < int(json['MovieCount']):
		if query == '':
			query = '__EMPTY__'
		if genre == '':
			genre = '__EMPTY__'

		object_container.add(NextPageObject(key=Callback(search_internal, title=title, movie_list=movie_list, query=query, genre=genre, only_3d=only_3d, page=page+1), title="More..."))

	return object_container

################################################################################
@route(common.PREFIX + '/' + SUBPREFIX + '/genres')
def genres(title):
	object_container = ObjectContainer(title2=title)
	genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'Film-Noir', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western']
	for genre in genres:
		object_container.add(DirectoryObject(key=Callback(search, title=genre, genre=genre), title=genre, thumb=R('yts.png')))
	return object_container


################################################################################
@route(common.PREFIX + '/' + SUBPREFIX + '/create_movie_object')
def create_movie_object(url, magnet, imdb_id, include_container=False):
	movie_object            = tmdb.create_movie_object(imdb_id)
	movie_object.key        = Callback(create_movie_object, url=url, magnet=magnet, imdb_id=imdb_id, include_container=True)
	movie_object.rating_key = url

	if include_container:
		movie_object.items = create_media_objects(url, magnet)

		object_container = ObjectContainer()
		object_container.objects.append(movie_object)
		return object_container
	else:
		return movie_object


################################################################################
def create_media_objects(url, magnet):
	media_objects = []

	html     = HTML.ElementFromURL(url, cacheTime=CACHE_1DAY)
	movie_id = html.xpath('//*[@class="magnet torrentDwl"]/@data-movieid')[0]

	movie_data_url = YTS_MOVIE.format(movie_id)
	movie_data     = JSON.ObjectFromURL(movie_data_url, cacheTime=CACHE_1DAY)

	if movie_data['Quality'] == '3D':
			media_object = MediaObject()
			media_object.add(PartObject(key=Callback(common.play_torrent, url=url, magnet=magnet)))
			media_object.video_resolution = get_closest_resolution(int(movie_data['Resolution'].partition('*')[2]))
			media_object.video_frame_rate = movie_data['FrameRate']
			media_objects.append(media_object)
	else:
		version_list_url  = YTS_LIST_VERSIONS.format(movie_data['ImdbCode'])
		version_list_data = JSON.ObjectFromURL(version_list_url, cacheTime=CACHE_1DAY)

		for version in version_list_data['MovieList']:
			if version['Quality'] != '3D':
				version_url  = YTS_MOVIE.format(version['MovieID'])
				version_data = JSON.ObjectFromURL(version_url, cacheTime=CACHE_1DAY)

				media_object = MediaObject()
				media_object.add(PartObject(key=Callback(common.play_torrent, url=version_data['MovieUrl'], magnet=version_data['TorrentMagnetUrl'])))
				media_object.video_resolution = get_closest_resolution(int(version_data['Resolution'].partition('*')[2]))
				media_object.video_frame_rate = version_data['FrameRate']
				media_objects.append(media_object)

	media_objects.sort(cmp=media_object_compare)
	return media_objects

################################################################################
def media_object_compare(a, b):
	return b.video_resolution - a.video_resolution

################################################################################
def get_closest_resolution(height):
	if height <= 240:
		return 240
	elif height <= 320:
		return 320
	elif height <= 480:
		return 480
	elif height <= 720:
		return 720
	else:
		return 1080