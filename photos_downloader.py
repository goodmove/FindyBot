import vkapi
import urllib.request as url
import os.path
import time
import threading as thr

class PhotoDownloader(object):
	def __init__(self, account_file = 'account', ids_file = None):
		self.account_data 	= None
		self.ids 		 	= []

		if not ids_file is None:
			self.updateIds(ids_file)

		self.updateAccountData(account_file)
		
		self.api = vkapi.vkapi(	self.account_data['app_id'], 
								self.account_data['app_secret'], '5.52', 
								perms = ['friends', 'photos'])

	def updateIds(self, file_name):
		f = open(file_name, 'r')
		self.ids = f.read().strip('[]').split(', ')
		f.close()

	def updateAccountData(self, file_name):
		f = open(file_name, 'r')
		data = f.read()
		f.close()
		# parse account data to dictionary
		self.account_data = dict([field.split(':') for field in data.split(',')])

	def downloadAll(self, count = 5, thread_count = 10, 
					path = 'photos/', file_format = '.jpg'):
		id_batch = []
		for id in self.ids:
			photo_path = path + id + file_format
			# if file with this name already exists skip it
			if os.path.isfile(photo_path): continue
			# update batch of ids
			if len(id_batch) < count:
				id_batch.append(id)
				continue
			# prepare payload for request
			payload = {
				'user_ids':str([int(i) for i in id_batch]).strip('[]'), 
				'fields':'photo_50'
			}
			# don't need ids in id_batch anymore
			id_batch.clear()
			# send GET request
			response = self.api.getRequest('users.get', payload)
			# skip request error
			if response is None: continue
			response = response.get('response')
			self._fast_download(response, path, file_format, count)

		# if some ids left download them
		if id_batch:
			self.downloadAll(self.api, id_batch, count=len(id_batch))

	def _fast_download(self, response, path, file_format, count):
		for r in response:
			photo_name = path + str(r['uid']) + file_format

			while thr.active_count() >= count:
				time.sleep(0.01) # sleep for 10 millis

			new_thread = thr.Thread(target = download, args = (r['photo_50'], photo_name))
			try: new_thread.start()
			except: print('Runtime Error')
			print('\rthread count: {0}'.format(thr.active_count()), end='')



def download(link, name):
	try:
		url.urlretrieve(link, name)
		return True
	except:
		return False

