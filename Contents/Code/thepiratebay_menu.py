################################################################################
SUBPREFIX = 'thepiratebay'

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
	object_container = ObjectContainer(title2='The Pirate Bay')
	object_container.add(DirectoryObject(key=Callback(top, title='Movies', category_id='201'), title='Movies', thumb=R('thepiratebay.png')))
	object_container.add(DirectoryObject(key=Callback(top, title='Movies - HD', category_id='207'), title='Movies - HD', thumb=R('thepiratebay.png')))
	object_container.add(DirectoryObject(key=Callback(top, title='TV Shows', category_id='205'), title='TV Shows', thumb=R('thepiratebay.png')))
	object_container.add(DirectoryObject(key=Callback(top, title='TV Shows - HD', category_id='208'), title='TV Shows - HD', thumb=R('thepiratebay.png')))
	object_container.add(InputDirectoryObject(key=Callback(search, title='Search'), title='Search', thumb=R('search.png')))
	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/category')
def top(title, category_id):
	url  = SharedCodeService.thepiratebay.THEPIRATEBAY_TOP.format(category_id)
	html = HTML.ElementFromURL(url, cacheTime=0)

	return get_page_object_container(title, html)

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search(title, query=''):
	url  = SharedCodeService.thepiratebay.THEPIRATEBAY_SEARCH.format(String.Quote(query))
	html = HTML.ElementFromURL(url, cacheTime=0)
	
	return get_page_object_container(title, html)

################################################################################
def get_page_object_container(title, html):
	object_container = ObjectContainer(title2=title)
	for item in html.xpath('//*[@id="searchResult"]/tr'):
		movie_url          = SharedCodeService.thepiratebay.THEPIRATEBAY + item.xpath('./td[2]/div/a/@href')[0]
		movie_seeders      = item.xpath('./td[3]/text()')[0]
		movie_peers        = item.xpath('./td[4]/text()')[0]
		movie_title        = item.xpath('./td[2]/div/a/text()')[0]
		movie_object       = MovieObject()
		movie_object.url   = movie_url
		movie_object.title = '(S{0}|P{1}) {2}'.format(movie_seeders, movie_peers, movie_title)
		object_container.add(movie_object)
	return object_container
