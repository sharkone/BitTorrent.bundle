################################################################################
SUBPREFIX = 'kickasstorrents'

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
	object_container = ObjectContainer(title2='KickassTorrents')
	object_container.add(DirectoryObject(key=Callback(category, title='Anime', category='anime'), title='Anime', thumb=R('kickasstorrents.png')))
	object_container.add(DirectoryObject(key=Callback(category, title='Movies', category='movies'), title='Movies', thumb=R('kickasstorrents.png')))
	object_container.add(DirectoryObject(key=Callback(category, title='TV Shows', category='tv'), title='TV Shows', thumb=R('kickasstorrents.png')))
	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/category')
def category(title, category):
	object_container = ObjectContainer(title2=title)
	object_container.add(DirectoryObject(key=Callback(page, title='Popular', root='/' + category, field='seeders'), title='Popular', thumb=R('kickasstorrents.png')))
	object_container.add(InputDirectoryObject(key=Callback(search, title='Search', category=category), title='Search', thumb=R('search.png')))
	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/page', page_index=int)
def page(title, root, field, page_index=1):
	url = '{0}{1}/{3}/?field={2}&sord=desc&rss=1'.format(SharedCodeService.kickasstorrents.KICKASSTORRENTS, root, field, page_index)
	rss = RSS.FeedFromURL(url, cacheTime=0)

	object_container = ObjectContainer(title2=title)
	for item in rss.entries:
		movie_object         = MovieObject()
		movie_object.title   = item.title

		movie_info = SharedCodeService.common.get_movie_info(movie_object.title)
		if movie_info['tmdb_id']:
			movie_object = SharedCodeService.tmdb.create_movie_object(movie_info['tmdb_id'])
	
		movie_object.summary = '{0}\nSeeders: {1}, Leechers: {2}\n\n{3}'.format(movie_info['release'], item.torrent_seeds, item.torrent_peers, movie_object.summary if movie_object.summary else '')
		movie_object.url     = item.link
		
		object_container.add(movie_object)

	object_container.add(NextPageObject(key=Callback(page, title=title, root=root, field=field, page_index=page_index + 1), title="More..."))

	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search(title, query, category):
	return page(title=title, root=String.Quote('/usearch/{0} category:{1}'.format(query, category)), field='seeders')
