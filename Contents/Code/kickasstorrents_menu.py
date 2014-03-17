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

		movie_title_result = SharedCodeService.common.RE_MOVIE_TITLE.search(SharedCodeService.common.get_clean_title(movie_object.title))
		movie_title        = movie_title_result.group(1) if movie_title_result else movie_object.title
		movie_year         = movie_title_result.group(3) if movie_title_result else ''
		movie_release      = movie_title_result.group(5) if movie_title_result else ''
		movie_tmdb_id      = SharedCodeService.tmdb.get_tmdb_id_from_title(movie_title, movie_year) if (movie_title and movie_year) else None

		if movie_tmdb_id:
			movie_object = SharedCodeService.tmdb.create_movie_object(movie_tmdb_id)
	
		movie_object.summary = '{0}\nSeeders: {1}, Leechers:{2}\n\n{3}'.format(movie_release, item.torrent_seeds, item.torrent_peers, movie_object.summary if movie_object.summary else '')
		movie_object.url     = item.link
		
		object_container.add(movie_object)

	object_container.add(NextPageObject(key=Callback(page, title=title, root=root, field=field, page_index=page_index + 1), title="More..."))

	return object_container

################################################################################
@route(SharedCodeService.common.PREFIX + '/' + SUBPREFIX + '/search')
def search(title, query, category):
	return page(title=title, root=String.Quote('/usearch/{0} category:{1}'.format(query, category)), field='seeders')
