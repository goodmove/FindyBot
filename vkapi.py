from third_party.VKAuth import vkauth
import requests
import os
import os.path

class vkapi(object):
	def __init__(self, app_id, app_secure, api_v = 5.52, perms = ['friends']):
		self.app_id 	= app_id
		self.app_secure = app_secure
		self.api_v 		= api_v
		self.token 		= None
		self.sess		= None
		self.perms 		= perms
		self.updateToken()

	def auth(self):
		self.sess = vkauth.VKAuth(self.perms, self.app_id, self.api_v)
		self.sess.auth()
		self.token = self.sess.get_token()
		f = open('token', 'w')
		f.write(self.token)
		f.close()

	def getRequest(self, method, params):
		if self.token is None:
			self.auth()

		params['access_token'] = self.token
		r = requests.get('https://api.vk.com/method/'+method+'?', params = params)
		j = r.json()
		if 'error' in j:
			print('error: ' + j['error']['error_msg'])
			if 'User authorization failed' in j['error']['error_msg']:
				self.auth()
				return self.getRequest(method, params)
		return j

	def DFSFriends(self, id, ids=[], depth=3, file_name=None):
		"""
			finds recursively friends using depth-first algorithm
			@args
				id – (int). id of user whose friends to search
				ids – ([int]). found friends' ids
				depth – (int). How deep in friends to search (e.g. for friends of friends depth = 2)
		"""
		count = 0
		_DFSFriends(id, ids, depth)
		print('\n')
		if not file_name is None:
			f = open(file_name, 'w')
			f.write(str(ids).strip('[]'))
			f.close()

	def _DFSFriends(self, id, ids, depth):
		if depth <= 0: return
		global count
		ids.append(id)
		payload = {'user_id':id}
		request = api.getRequest('friends.get', payload)
		if 'error' in request: return
		friends = request['response']
		for friend in friends: 
			if not friend in ids:
				count += 1
				# uncomment to see how many friends found
				# print('\rfound friends: {0}'.format(count), end='')
				get_friend_ids(api, friend, ids, depth-1)

	def updateToken(self):
		if os.path.isfile('token'):
			f = open('token', 'r')
			self.token = f.read()
		else:
			print('the "token" file is missing')

	def clearToken():
		self.token = None
		os.remove('token')