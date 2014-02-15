################################################################################
import common

################################################################################
SUBPREFIX = 'thepiratebay'

################################################################################
@route(common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
	object_container = ObjectContainer(title2='The Pirate Bay')
	object_container.add(InputDirectoryObject(key=Callback(search, title='Search'), title='Search', thumb=R('search.png')))
	return object_container

################################################################################
@route(common.PREFIX + '/' + SUBPREFIX + '/search')
def search(title, query=''):
	THEPIRATEBAY        = 'http://thepiratebay.se'
	THEPIRATEBAY_SEARCH = THEPIRATEBAY + '/search/{0}/0/7/200'

	url  = THEPIRATEBAY_SEARCH.format(String.Quote(query))
	html = HTML.ElementFromURL(url, cacheTime=0)
	
	object_container = ObjectContainer(title2=title)
	for item in html.xpath('//*[@id="searchResult"]/tr'):
		movie_url     = THEPIRATEBAY + item.xpath('./td[2]/div/a/@href')[0]
		movie_magnet  = item.xpath('./td[2]/a[1]/@href')[0]
		movie_seeders = item.xpath('./td[3]/text()')[0]
		movie_peers   = item.xpath('./td[4]/text()')[0]
		movie_title   = item.xpath('./td[2]/div/a/text()')[0]
		Log.Info(movie_url)
		Log.Info(movie_magnet)
		movie_object       = create_movie_object(url=movie_url, magnet=movie_magnet, title=movie_title)
		movie_object.title = '(S{0} | P{1}) {2}'.format(movie_seeders, movie_peers, movie_title)
		
		object_container.add(movie_object)
	return object_container

################################################################################
@route(common.PREFIX + '/' + SUBPREFIX + '/create_movie_object')
def create_movie_object(url, magnet, title, include_container=False):
	movie_object            = MovieObject()
	movie_object.title      = title
	movie_object.key        = Callback(create_movie_object, url=url, magnet=magnet, title=title, include_container=True)
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

	media_object = MediaObject()
	media_object.parts.append(PartObject(key=Callback(common.play_torrent, url=url, magnet=magnet)))
	media_objects.append(media_object)

	return media_objects
