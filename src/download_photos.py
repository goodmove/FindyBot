from src.vkapi import vkapi
from src.vkapi.downloader import Downloader
from src.vkapi.photo_downloader import PhotoDownloader as pd
from ids import IDS as ids
import os
import os.path
import requests

p = pd()
p.downloadWithFaces(photo_count=200, photo_type='x')

# vkapi.findFriends()

def downloadAllPhotos(filter=Downloader.ONE_FACE, size='x', count=200, no_service_albums=0, offset=0, path='photos'):
	downloader = Downloader()
	if not os.path.exists(path):
		os.makedirs(path)
	for uid in ids:
		upath = '{}/{}'.format(path, uid)
		if not os.path.exists(upath):
			os.makedirs(upath)
		r = vkapi.getRequest('photos.getAll',
			count=count,
			owner_id=uid,
			photo_sizes=1,
			no_service_albums=no_service_albums,
			offset=offset
			)
		if 'error' in r: continue
		photos = r['response']
		for photo in photos[1:]:
			photo_path = '{}/{}.jpg'.format(upath, photo['pid'])
			sizes = photo['sizes']
			for s in sizes:
				if s['type'] is size:
					downloader.push_download(s['src'], photo_path, filter=Downloader.ONE_FACE)
					break


# downloadAllPhotos()