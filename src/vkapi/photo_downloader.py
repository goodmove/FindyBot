from src.vkapi.vkapi import vkapi
from src.image_processing.impros import ImageProcessor as imp
from src.image_processing.clf_constants import CONSTANTS
import urllib.request as url
import os.path
import time
import threading as thr
import requests
from cv2 import imread, imwrite
from skimage.transform import resize

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

	def findFriends(self, id=None, depth=3, file_name='ids', algorithm='bfs'):
		if id is None: id = self.account_data['id']
		self.api.findFriends(id=id, depth=depth, file_name=file_name, algorithm=algorithm)

	def downloadAll(self, photo_count=10, thread_count=10, show_thread_count=False, check_face=False,
					path='photos', face_landmarks='landmarks.txt', file_format='.jpg', photo_type='m', 
					no_service_albums=0, create_id_folders=False, keep_old=False, displacement=None):
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
		if self.ids is None or self.ids is []:
			print('please, update ids')
			return

		# make dir if it doesn't exist
		if not os.path.exists(path):
			os.makedirs(path)

		face_landmarks = '{}/{}'.format(path, face_landmarks)

		for uid in self.ids:
			ipath = path + '/%d' % uid if create_id_folders else path
			
			if not os.path.exists(ipath):
				os.makedirs(ipath)

			payload = {
				'owner_id':				uid,
				'no_service_albums':	no_service_albums,
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
						links[size['src']] = '{0}{1}x{2}'.format(photo_type, size['width'], size['height'])
			for pid, (link, size) in enumerate(links.items()):
				self.download(	thread_count, show_thread_count, link, ipath, uid, pid, size, 
								file_format, check_face, face_landmarks, keep_old, displacement)
		print('\ndone :)')

	def download(self, thread_count, show_thread_count, *args):
		# wait for available threads
		while thr.active_count() >= thread_count:
			time.sleep(0.01) # sleep for 10 millis

		new_thread = thr.Thread(target=download, args=args)
		try: new_thread.start()
		except: print('\rcouldn\'t start a new thread')
		if show_thread_count:
			print('\rthread count: %3d' % thr.active_count(), end='')

def extend(imw, imh, facex, facey, facew, faceh, displacement=None):
	x, y, w, h = face
	dx, dy = (int(0.3*w), int(0.3*h)) if displacement is None else displacement

	dx1 = dx if x-2*dx > 0 else x/2
	dx2 = dx if imw  > (x+w) + 2*dx else (imw - (x+w))/2
	dx = int(min(dx1, dx2))

	dy1 = dy if y-2*dy >= 0 else y/2
	dy2 = dy if imh  >= (y+h) + 2*dy else (imh - (y+h))/2
	dy = int(min(dy1, dy2))

	# exception handling. a weird case.
	if dx < 0 or dy < 0:
		return None

	# return dimensions of extended face frame and axis shifts
	return (x-dx, y-dy, w+2*dx, h+2*dy, dx, dy)

def crop(img, x, y, w, h):
	return img[x:x+w][y:y+h]


def download(link, path, uid, pid, size, fmt, check_face, face_landmarks, keep_old=False, displacement=None):
	"""
		downloads a file at link into name
		@args
			link – (str). Link to a file that needs to be downloaded
			name – (str). Name to give to the downloaded file
		@return
			True if download was ok
			False if not
	"""
	name = '{0}/{1}original{2}{3}{4}'.format(path, uid, pid, size, fmt)
	if check_face:
		faces = imp.get_faces(link=link)
		if faces:
			try:
				url.urlretrieve(link, name)
			except:
				print('problem at downloading '.format(name))
				return
			img = imread(name)
			imw, imh, imd = img.shape
			f = open(face_landmarks, 'a')
			for fid, face in enumerate(faces):
				x, y, w, h = face['x'], face['y'], face['width'], face['height']
				x, y, w, h, dx, dy = extend(imw, imh, x, y, w, h, displacement=displacement)
				cropped = crop(img, x, y, w, h)
				resized = resize(cropped, CONSTANTS['resize_values'], preserve_range=True)
				kx = w / CONSTANTS['resize_values'][0]
				ky = h / CONSTANTS['resize_values'][1]
				fim_name = '{}/{}photo{}face{}{}'.formate(path, uid, pid, fid, fmt)
				imwrite(fim_name, resized)
				face_info = {
					'user_id':	uid,
					'photo_id':	pid,
					'face_id':	fid,
					'x':		dx*kx,
					'y':		dy*ky,
					'width':	(w-2*dx)*kx,
					'height':	(h-2*dx)*ky,
					'features': face['features']
				}
				f.write('{}\n'.format(face_info))
			f.close()
		if not keep_old and os.path.isfile(name):
			os.remove(name)
	else:
		try:
			url.urlretrieve(link, name)
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

