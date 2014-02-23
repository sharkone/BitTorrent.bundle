################################################################################
SUBPREFIX = 'yts'

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
	object_container = genre('All', False)
	object_container.add(DirectoryObject(key=Callback(genres, title='Genres'), title='Genres', thumb=R('yts.png')))
	object_container.add(InputDirectoryObject(key=Callback(search, title='Search', genre='All'), title='Search', thumb=R('search.png')))
	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/genres')
def genres(title):
	object_container = ObjectContainer(title2=title)
	genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'Film-Noir', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western']
	for g in genres:
		object_container.add(DirectoryObject(key=Callback(genre, genre=g), title=g, thumb=R('yts.png')))
	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/genre', allow_search=bool)
def genre(genre, allow_search=True):
	object_container = ObjectContainer(title2=genre)
	object_container.add(DirectoryObject(key=Callback(search, title='Latest', genre=genre), title='Latest', thumb=R('yts.png')))
	object_container.add(DirectoryObject(key=Callback(search, title='Popular', genre=genre, sort='peers'), title='Popular', thumb=R('yts.png')))
	object_container.add(DirectoryObject(key=Callback(search, title='Rating', genre=genre, sort='rating'), title='Rating', thumb=R('yts.png')))
	object_container.add(DirectoryObject(key=Callback(search, title='3D', genre=genre, only_3d=True), title='3D', thumb=R('yts.png')))
	
	if allow_search:
		object_container.add(InputDirectoryObject(key=Callback(search, title='Search', genre=genre), title='Search', thumb=R('search.png')))
	
	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search', only_3d=bool)
def search(title, query='', genre='ALL', sort='date', only_3d=False):
	return search_internal(title, list(), query, genre, sort, only_3d, 1)

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search_internal', movie_list=list, only_3d=bool, page=int)
def search_internal(title, movie_list, query, genre, sort, only_3d, page):
	query   = String.Quote(query) if query   else ''
	genre   = String.Quote(genre) if genre   else ''
	quality = String.Quote('3D')  if only_3d else ''

	if query == '__EMPTY__':
		query = ''

	url  = SharedCodeService.yts.YTS_LIST.format(query, genre, quality, sort, str(page))
	json = JSON.ObjectFromURL(url, cacheTime=CACHE_1HOUR)

	object_container = ObjectContainer(title2=title)
	for movie in json['MovieList']:
		if movie['Quality'] != '3D' or only_3d:
			if movie['ImdbCode'] not in movie_list:
				movie_object = SharedCodeService.tmdb.create_movie_object(movie['ImdbCode'])
				if movie_object:
					movie_object.url = movie['MovieUrl']
					movie_list.append(movie['ImdbCode'])
					object_container.add(movie_object)

	if (page * 50) < int(json['MovieCount']):
		if query == '':
			query = '__EMPTY__'

		object_container.add(NextPageObject(key=Callback(search_internal, title=title, movie_list=movie_list, query=query, genre=genre, sort=sort, only_3d=only_3d, page=page+1), title="More..."))

	return object_container
