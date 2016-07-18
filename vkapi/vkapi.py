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
		graph = {}
		self._count = 0
		self.build_friends_graph(id, graph, depth)
		print(graph)
		return
		visited = set()
		if algorithm.lower() is 'bfs':
			queue = [id]
			while queue:
				vertex = queue.pop()
				if vertex not in visited:
					visited.add(vertex)
					queue.extend(graph[vertex] - visited)
		elif algorithm.lower() is 'dfs':
			stack = [id]
			while stack:
				vertex = stack.pop(0)
				if vertex not in visited:
					visited.add(vertex)
					stack.extend(graph[vertex] - visited)

		else:
			print('error: {0} bad name of algorithm'.format(algorithm))
		print('\ndone')
		f = open(file_name, 'w')
		f.write(str(visited).strip('[]'))
		f.close()

	def build_friends_graph(self, id, graph, depth):
		if depth <= 0: return
		request = self.getRequest('friends.get', {'user_id':id})
		if 'error' in request: return
		friends = request['response']
		graph[id] = set(friends)
		for friend in friends:
			self._count += 1
			print('\rfrinds found: {0}'.format(self._count), end='')
			self.build_friends_graph(friend, graph, depth-1)

	def updateToken(self):
		if os.path.isfile('token'):
			f = open('token', 'r')
			self.token = f.read()
		else:
			print('the "token" file is missing')

	def clearToken():
		self.token = None
		os.remove('token')