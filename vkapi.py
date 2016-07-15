from third_party.VKAuth import vkauth
import requests
import os
import os.path

class vkapi(object):
	def __init__(self, app_id, app_secret, api_v, perms = ['friends']):
		self.app_id 	= app_id
		self.app_secret = app_secret
		self.api_v 		= api_v
		self.token 		= None
		self.sess		= None
		self.perms 		= perms
		self.updateToken()

	def auth(self):
		self.sess = vkauth.VKAuth(self.perms, self.app_id, self.api_v)
		self.sess.authorize()
		self.token = self.sess.access_token
		f = open('token', 'w')
		f.write(self.token)
		f.close()
	
	def getRequest(self, method, params):
		if self.token is None:
			self.auth()
			return self.getRequest(method, params)

		params['access_token'] = self.token
		r = requests.get('https://api.vk.com/method/'+method+'?', params = params)
		j = r.json()
		if 'error' in j:
			print('request error')
			return None
		return j

	def updateToken(self):
		if os.path.isfile('token'):
			f = open('token', 'r')
			self.token = f.read()
		else:
			print('the "token" file is missing')

	def clearToken():
		self.token = None
		os.remove('token')
