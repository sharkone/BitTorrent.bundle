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
		movie_title   = '(S{0} | P{1}) {2}'.format(movie_seeders, movie_peers, item.xpath('./td[2]/div/a/text()')[0])
		
		movie_object       = common.create_movie_object(url=movie_url, magnet=movie_magnet)
		movie_object.title = movie_title
		
		object_container.add(movie_object)
	return object_container
