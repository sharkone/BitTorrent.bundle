################################################################################
SUBPREFIX = 'kickasstorrents'

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/menu')
def menu():
	object_container = ObjectContainer(title2='KickassTorrents')
	object_container.add(InputDirectoryObject(key=Callback(search, title='Search'), title='Search', thumb=R('search.png')))
	return object_container

################################################################################
################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search(title, query=''):
	url = SharedCodeService.kickasstorrents.KICKASSTORRENTS_SEARCH.format(String.Quote(query))
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
	return object_container
