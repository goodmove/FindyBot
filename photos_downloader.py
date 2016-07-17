import vkapi
import urllib.request as url
import os.path
import time
import threading as thr

class PhotoDownloader(object):
	def __init__(self, account_file = 'account', ids_file = 'ids'):
		self.account_data 	= None
		self.ids 		 	= []

		self.updateIds(ids_file)

		self.updateAccountData(account_file)

		self.api = vkapi.vkapi(	self.account_data['app_id'],
								self.account_data['app_secure'],
								'5.52', 
								perms = ['friends', 'photos'])

	def updateIds(self, file_name):
	"""
		gets a list of ids from the given file
		@args
			file_name – (str). Name of file to get ids from
	"""
		f = open(file_name, 'r')
		self.ids = f.read().strip('[]').split(', ')
		f.close()

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

	def downloadAll(self, thread_count = 10, photo_count = 10,
					path = 'photos', file_format = '.jpg', photo_type = 'm',
					no_service_albums = 1, need_hidden = 0, skip_hidden = 0):
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
			path = path + '/' + id
			# if file with this name already exists skip it
			if not os.path.exists(path):
				os.makedirs(path)
			else: continue
			# prepare payload for request
			payload = {
				'owner_id':				id, 
				'extended':				0,
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
			response = request.get('response')
			# create and start threads for downloading photos
			for index, item in enumerate(response['items']):
				size = str(item['width']) + 'x' + str(item['height'])
				photo_name = path + '/' + str(index) + photo_type + size + file_format
				if os.path.isfile(photo_name): continue

				# wait for available threads
				while thr.active_count() >= thread_count:
					time.sleep(0.01) # sleep for 10 millis

				new_thread = thr.Thread(target = download, args = (item['src'], photo_name))
				try: new_thread.start()
				except: print('couldn\'t start a new thread')
				# print('\rthread count: {0}'.format(thr.active_count()), end='')

def download(link, name):
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
		return True
	except:
		return False

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

