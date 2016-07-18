from third_party.VKAuth import vkauth
import requests
import os
import os.path

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

	def findFriends(self, id, depth=3, file_name=None, algorithm='bfs'):
		"""
			finds friends using depth-first or breadth-first algorithm
			@args
				id – (int). id of user whose friends to search
				depth – (int). How deep in friends to search (e.g. for friends of friends depth = 2)
				file_name – (str). Name of a file to write found ids in
				algorithm – (str). 'bfs' or 'dfs'
		"""
		f = open(file_name, 'w')
		if algorithm.lower() == 'bfs':
			self._bdfsr([id], func=lambda x: f.write('{0}, '.format(x)), first_pos=-1)
		elif algorithm.lower() == 'dfs':
			self._bdfsr([id], func=lambda x: f.write('{0}, '.format(x)), first_pos=0)
		else: print('error: {0} bad name of algorithm'.format(algorithm))
		print('\ndone')
		f.close()

	def _bdfsr(self, q, visited=set(), d=3, func=print, first_pos=-1):
		if d <= 0: return visited
		new = []
		while q:
			v = q.pop(first_pos)
			if v in visited: continue
			visited.add(v)
			func(v)
			request = self.getRequest('friends.get', {'user_id':v})
			friends = request.get('response')
			if friends is None: continue
			new.extend(set(friends) - visited)
		return self._bfsr(new, visited, d-1, func, first_pos)

	def updateToken(self):
		if os.path.isfile('token'):
			f = open('token', 'r')
			self.token = f.read()
		else:
			print('the "token" file is missing')

	def clearToken():
		self.token = None
		os.remove('token')