from vkapi.vkapi import vkapi
from image_processing.impros import ImageProcessor as imp
import urllib.request as url
import os.path
import time
import threading as thr

class PhotoDownloader(object):
	def __init__(self, account_file='account', ids_file='ids'):
		self.account_data 	= None
		self.ids 		 	= []


		self.updateAccountData(account_file)
		self.user_id = int(self.account_data['id'])
		self.api = vkapi(	self.account_data['app_id'],
							self.account_data['app_secure'],
							'5.52', 
							perms=['friends', 'photos'])
		# self.updateIds(ids_file)

	def updateIds(self, file_name='ids'):
		"""
			gets a list of ids from the given file
			@args
				file_name – (str). Name of file to get ids from
		"""
		if os.path.isfile(file_name):
			f = open(file_name, 'r')
			self.ids = [int(i) for i in f.read().strip('}{').split(',')]
			f.close()
		# else:
			# print(self.user_id)
			# self.api.findFriends(self.user_id, file_name=file_name)

	def updateAccountData(self, file_name):
		"""
			gets an account data from the given file and forms it as a dictionary
			@args
				file_name – (str). Name of file to get account data from
		"""
		f = open(file_name, 'r')
		data = f.read()
		f.close()
		# parse account data to dictionary
		self.account_data = dict([field.split(':') for field in data.split(',')])

	def downloadWithFaces(	self, photo_count=10, thread_count=10, show_thread_count=False,
							path='photos', file_format='.jpg', photo_type='m'):
		if self.ids is None or self.ids is []:
			print('please, update ids')
			return

		# make dir if it doesn't exist
		if not os.path.exists(path):
			os.makedirs(path)

		for id in self.ids:
			ipath = path + '/' + str(id)

			# if file with this name already exists skip it
			if not os.path.exists(ipath):
				os.makedirs(ipath)
			else: continue
			
			payload = {
				'owner_id':				id,
				'no_service_albums':	0,
				'offset':				0,
				'count':				photo_count,
				'photo_sizes':			1
			}

			request = self.api.getRequest('photos.getAll', payload)

			if 'error' in request: continue
			photos = request['response'][1:]
			all_sizes = [photo['sizes'] for photo in photos]
			links = {}
			for sizes in all_sizes:
				for size in sizes:
					if size['type'] is photo_type:
						links[size['src']] = photo_type + '{0}x{1}'.format(size['width'], size['height'])
			for index, (link, size) in enumerate(links.items()):
				photo_name = ipath + '/' + str(index) + size + file_format
				self.download(link, photo_name, thread_count, check_face=True, show_thread_count=show_thread_count)
		print('\ndone :)')

	def downloadAll(self, photo_count=10, thread_count=10, show_thread_count=False,
					path='photos', file_format='.jpg', photo_type='m',
					no_service_albums=0, need_hidden=0, skip_hidden=0):
		"""
			downloads photo_count photos for each id in self.ids and stores them in path directory.
			Photos for each id will be in separate package with name id
			Note: it skips if a directory with same name already exists (that means this program already worked here)

			@args
				thread_count – (uint). Max number of threads to use
				photo_count – (uint). Max number of photos of each user to download
				path – (str). Path to directory for photos to store
				file_format – (str). Format of image file
				photo_type – (str). One of ['s','m','x','y','z','w','o','p','q'] (see description at the end of file)
		"""

		# make dir if it doesn't exist
		if not os.path.exists(path):
			os.makedirs(path)

		if self.ids is None:
			raise Exception('self.ids is None')

		for id in self.ids:
			ipath = path + '/%d' % id

			# if file with this name already exists skip it
			if not os.path.exists(ipath):
				os.makedirs(ipath)
			else: continue
			# prepare payload for request
			payload = {
				'owner_id':				id, 
				'offset':				0,
				'count':				photo_count,
				'photo_sizes':			1,
				'no_service_albums':	no_service_albums,
				'need_hidden':			need_hidden,
				'skip_hidden':			skip_hidden
			}
			# send GET request
			request = self.api.getRequest('photos.getAll', payload)
			# skip request error
			if 'error' in request: continue
			response = request['response']
			# create and start threads for downloading photos
			all_photos = response[1:]
			# find first photo of size 'photo_type' into photos
			photos = [next(s for s in p['sizes'] if s['type'] is photo_type) for p in all_photos]
			for index, item in enumerate(photos):
				size = '{0}x{1}'.format(item['width'], item['height'])
				photo_name = ipath + '/' + str(index) + photo_type + size + file_format
				if os.path.isfile(photo_name): continue
				self.download(item['src'], photo_name, thread_count, show_thread_count=show_thread_count)
		print('\ndone :)')

	def download(self, link, name, thread_count, check_face=False, show_thread_count=False):
		# wait for available threads
		while thr.active_count() >= thread_count:
			time.sleep(0.01) # sleep for 10 millis

		new_thread = thr.Thread(target=download, args=(link, name, check_face))
		try: new_thread.start()
		except: print('\rcouldn\'t start a new thread')
		if show_thread_count:
			print('\rthread count: %3d' % thr.active_count(), end='')

	def findFriends(self, id=None, depth=3, file_name='ids', algorithm='bfs'):
		if id is None: id = self.account_data['id']
		self.api.findFriends(id=id, depth=depth, file_name=file_name, algorithm=algorithm)


def download(link, name, check_face):
	"""
		downloads a file at link into name
		@args
			link – (str). Link to a file that needs to be downloaded
			name – (str). Name to give to the downloaded file
		@return
			True if download was ok
			False if not
	"""
	try:
		url.urlretrieve(link, name)
	except:
		return False
	if check_face:
		face = imp.detect_face_ext(path=name, visualize=True)
		if len(face) is 0:
			os.remove(name)
			return False
	return True

"""
	Available values of field 'photo_type'
		s — proportional copy with 75px max width;
		m — proportional copy with 130px max width;
		x — proportional copy with 604px max width;
		o — if original image's "width/height" ratio is less or equal to 3:2, then proportional copy with 130px max width. If original image's "width/height" ratio is more than 3:2, then copy of cropped by left side image with 130px max width and 3:2 sides ratio.
		p — еif original image's "width/height" ratio is less or equal to 3:2, then proportional copy with 200px max width. If original image's "width/height" ratio is more than 3:2, then copy of cropped by left side image with 200px max width and 3:2 sides ratio.
		q — if original image's "width/height" ratio is less or equal to 3:2, then proportional copy with 320px max width. If original image's "width/height" ratio is more than 3:2, then copy of cropped by left side image with 320px max width and 3:2 sides ratio.
		y — proportional copy with 807px max width;
		z — proportional copy with 1280x1024px max size;
		w — proportional copy with 2560x2048px max size.
"""

