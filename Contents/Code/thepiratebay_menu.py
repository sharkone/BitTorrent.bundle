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
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search', page_index=int)
def search(title, query, page_index=0):
	url  = SharedCodeService.thepiratebay.THEPIRATEBAY_SEARCH.format(String.Quote(query), page_index)
	html = HTML.ElementFromURL(url, cacheTime=0)
	
	object_container = get_page_object_container(title, html)
	object_container.add(NextPageObject(key=Callback(search, title=title, query=query, page_index=page_index + 1), title="More..."))

	return object_container

################################################################################
def get_page_object_container(title, html):
	object_container = ObjectContainer(title2=title)
	for item in html.xpath('//*[@id="searchResult"]/tr'):
		item_seeders  = item.xpath('./td[3]/text()')[0]
		item_leechers = item.xpath('./td[4]/text()')[0]

		movie_object         = MovieObject()
		movie_object.title   = item.xpath('./td[2]/div/a/text()')[0]

		movie_title_result = SharedCodeService.common.RE_MOVIE_TITLE.search(SharedCodeService.common.get_clean_title(movie_object.title))
		movie_title        = movie_title_result.group(1) if movie_title_result else movie_object.title
		movie_year         = movie_title_result.group(3) if movie_title_result else ''
		movie_release      = movie_title_result.group(5) if movie_title_result else ''
		movie_tmdb_id      = SharedCodeService.tmdb.get_tmdb_id_from_title(movie_title, movie_year) if (movie_title and movie_year) else None

		if movie_tmdb_id:
			movie_object = SharedCodeService.tmdb.create_movie_object(movie_tmdb_id)
			
		movie_object.summary = '{0}\nSeeders: {1}, Leechers:{2}\n\n{3}'.format(movie_release, item_seeders, item_leechers, movie_object.summary if movie_object.summary else '')
		movie_object.url     = SharedCodeService.thepiratebay.THEPIRATEBAY + item.xpath('./td[2]/div/a/@href')[0]

		object_container.add(movie_object)
	return object_container
