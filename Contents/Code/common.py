################################################################################
PREFIX = '/video/bittorrent'

################################################################################
import tmdb
import torrent2http

################################################################################
@route(PREFIX + '/create_movie_object', include_container=bool)
def create_movie_object(url, magnet, imdb_id='', include_container=False):
	media_object = MediaObject()
	media_object.parts.append(PartObject(key=Callback(play_torrent, url=url, magnet=magnet)))

	movie_object            = tmdb.create_movie_object(imdb_id) if imdb_id != '' else MovieObject()
	movie_object.key        = Callback(create_movie_object, url=url, magnet=magnet, imdb_id=imdb_id, include_container=True)
	movie_object.rating_key = url
	movie_object.items.append(media_object)

	if include_container:
		object_container = ObjectContainer()
		object_container.objects.append(movie_object)
		return object_container
	else:
		return movie_object

################################################################################
@route(PREFIX + '/play_video')
@indirect
def play_torrent(url, magnet):
	return torrent2http.start_torrent(url, magnet)
