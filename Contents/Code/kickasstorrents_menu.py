################################################################################
SUBPREFIX = 'kickasstorrents'

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
	object_container = ObjectContainer(title2='KickassTorrents')
	object_container.add(DirectoryObject(key=Callback(movies, title='Movies'), title='Movies', thumb=R('kickasstorrents.png')))
	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/movies')
def movies(title):
	object_container = ObjectContainer(title2=title)
	object_container.add(DirectoryObject(key=Callback(page, title='Popular', root='/movies', field='leechers'), title='Popular', thumb=R('kickasstorrents.png')))
	object_container.add(InputDirectoryObject(key=Callback(search, title='Search', category='movies'), title='Search', thumb=R('search.png')))
	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/page', page_index=int)
def page(title, root, field, page_index=1):
	url = '{0}{1}/?field={2}&sord=desc&rss=1'.format(SharedCodeService.kickasstorrents.KICKASSTORRENTS, root, field)
	rss = RSS.FeedFromURL(url, cacheTime=0)

	object_container = ObjectContainer(title2=title)
	for item in rss.entries:
		movie_seeders = item.torrent_seeds
		movie_peers   = item.torrent_peers
		movie_title   = item.title

		movie_object       = MovieObject()
		movie_object.url   = item.link
		movie_object.title = '(S{0}|P{1}) {2}'.format(movie_seeders, movie_peers, movie_title)
		object_container.add(movie_object)

	object_container.add(NextPageObject(key=Callback(page, title=title, root=root, field=field, page_index=page_index + 1), title="More..."))

	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search(title, query, category):
	return page(title=title, root=String.Quote('/usearch/{0} category:{1}'.format(query, category)), field='seeders')
