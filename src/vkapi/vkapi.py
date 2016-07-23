from src.vkapi.vkauth import VKAuth
import requests
import os
import os.path
import time

class vkapi(object):
	def __init__(self, app_id, app_secure, api_v=5.52, perms=['friends']):
		self.app_id 	= app_id
		self.app_secure = app_secure
		self.api_v 		= api_v
		self.token 		= None
		self.sess		= None
		self.perms 		= perms
		self.updateToken()

	def auth(self):
		self.sess = VKAuth(self.perms, self.app_id, self.api_v)
		self.sess.auth()
		self.token = self.sess.get_token()
		f = open('token', 'w')
		f.write(self.token)
		f.close()

	def getRequest(self, method, params):
		if self.token is None:
			self.auth()

		params['access_token'] = self.token
		r = requests.get('https://api.vk.com/method/'+method+'?', params=params)
		j = r.json()
		if 'error' in j:
			msg = j['error']['error_msg']
			print('\rerror: ' + msg)
			if 'User authorization failed' in msg:
				self.auth()
				return self.getRequest(method, params)
			elif 'Too many requests per second' in msg:
				time.sleep(0.1)
				return self.getRequest(method, params)
		return j

	def findFriends(self, id, depth=3, file_name='ids', algorithm='bfs'):
		"""
			finds friends using depth-first or breadth-first algorithm
			@args
				id – (int). id of user whose friends to search
				depth – (int). How deep in friends to search (e.g. for friends of friends depth = 2)
				file_name – (str). Name of a file to write found ids in
				algorithm – (str). 'bfs' or 'dfs'
		"""
		if os.path.isfile(file_name):
			f = open(file_name, 'r')
			friends = {int(friend) for friend in f.read().strip('}{][').split(',') if friend is not ''}
			f.close()
			friends = self.bfs(id, depth=depth, found=friends)
		else:
			friends = self.bfs(id, depth=depth)
		f = open(file_name, 'w')
		f.write(','.join([str(f) for f in friends]))
		f.close()

	def bfs(self, start, depth=3, found=set()):
		if depth <= 0: return found
		time.sleep(0.01)
		request = self.getRequest('friends.get', {'user_id':start, 'fields':'deactivated'})
		if 'error' in request: return found
		friends = request['response']
		ids = {friend['uid'] for friend in friends if 'deactivated' not in friend}
		new_found = ids - found
		found |= new_found
		print('\rfound: {0}'.format(len(found)), end='')
		if depth > 1:
			for i in new_found:
				found = self.bfs(i, depth-1, found)
		return found

	def updateToken(self):
		if os.path.isfile('token'):
			f = open('token', 'r')
			self.token = f.read()
		else:
			print('the "token" file is missing')

	def clearToken():
		self.token = None
		os.remove('token')