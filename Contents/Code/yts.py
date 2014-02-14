################################################################################
import common

################################################################################
SUBPREFIX = 'yts'

YTS      = 'http://yts.re'
YTS_LIST = YTS + '/api/list.json?limit=50&keywords={0}&genre={1}&quality={2}&set={3}'

#MOVIE_SET = set()

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
@route(common.PREFIX + '/' + SUBPREFIX + '/search', only_3d=bool, page=int)
def search(title, query='', genre='', only_3d=False, page=1):
	if page == 1:
		MOVIE_SET = set()

	query   = String.Quote(query) if query   else ''
	genre   = String.Quote(genre) if genre   else ''
	quality = String.Quote('3D')  if only_3d else ''

	url  = YTS_LIST.format(query, genre, quality, str(page))
	json = JSON.ObjectFromURL(url, cacheTime=0)

	object_container = ObjectContainer(title2=title)
	for movie in json['MovieList']:
		if movie['Quality'] != '3D' or only_3d:
			if movie['ImdbCode'] not in MOVIE_SET:
				MOVIE_SET.add(movie['ImdbCode'])
				movie_object = common.create_movie_object(movie['MovieUrl'], movie['TorrentMagnetUrl'], movie['ImdbCode'])
				object_container.add(movie_object)
		
	if (page * 50) < int(json['MovieCount']):
		object_container.add(NextPageObject(key=Callback(search, title=title, query=query, genre=genre, only_3d=only_3d, page=page + 1), title="More..."))

	return object_container

################################################################################
@route(common.PREFIX + '/' + SUBPREFIX + '/genres')
def genres(title):
	object_container = ObjectContainer(title2=title)
	genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'Film-Noir', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western']
	for genre in genres:
		object_container.add(DirectoryObject(key=Callback(search, title=genre, genre=genre), title=genre, thumb=R('yts.png')))
	return object_container
