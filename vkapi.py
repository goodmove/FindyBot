from third_party.VKAuth import vk_auth as vkauth
import requests

class vkapi(object):
	def __init__(self, app_id, app_secret, api_v):
		self.app_id 	= app_id
		self.app_secret = app_secret
		self.api_v 		= api_v
		self.token 		= None
		self.sess		= None

	def auth(self):
		self.sess = vkauth.VKAuth(['friends', 'images'], self.app_id, self.api_v)
		self.sess.authorize()
		self.token = self.sess.access_token
		# print(self.token)

	def getFriends(self, id):
		payload = {
			'user_id' : id,
			'access_token' : self.token
		}
		r = requests.get('https://api.vk.com/method/friends.get?', params = payload)
		response = r.json()
		if 'response' in response:
			return response['response']
		else:
			return []

	def getAllPhotos(self, id):
		payload = {
			'user_id' : id,
			'access_token' : self.token
		}
		r = requests.get('https://api.vk.com/method/photos.getAll?', params = payload)
		return r.json()

	def getPhotos(self, id, album_id=0):
		payload = {
			'album_id' : album_id,
			'user_id' : id,
			'access_token' : self.token
		}
		r = requests.get('https://api.vk.com/method/photos.get?', params = payload)
		return r.json()

	def getAlbums(self, id):
		payload = {
			'user_id' : id,
			'access_token' : self.token
		}
		r = requests.get('https://api.vk.com/method/photos.getAlbums?', params = payload)
		return r.json()		

	def close(self):
		self.sess.close()
