from src.vkapi.vkauth import VKAuth
import requests
import os.path
import time

try:
	from account import ACCOUNT
	account = ACCOUNT
except:
	print('failed to get account information from "account.py"')
	account = {}

def getAccountInfo(*args):
	"""
		@return
			if 0 args returns account
			if 1 arg returns account[arg]
			otherways returns list of account[arg] for each arg in args
	"""
	l = []
	if len(args) == 0:
		return account
	if len(args) == 1:
		return account[args[0]] if args[0] in account else None
	for i in args:
		l.append(account[i] if i in account else None)
	return l

def updateAccountInfo():
	global account
	try:
		from account import ACCOUNT
		account = ACCOUNT
	except:	raise RuntimeError('failed to get account information from "account.py"')

def updateAccountFile():
	f = open('account.py', 'w')
	f.write('ACCOUNT = ' + str(account))
	f.close()

def checkAccount(*args):
	"""
		Checks specified in args account fields for existence and asks user for nonexistent
	"""
	global account
	modified = False
	for a in args:
		if not a in account:
			modified = True
			if a is 'permissions':
				account[a] = input('please give me your {}:'.format(a)).split(',')
			else:
				account[a] = input('please give me your {}:'.format(a))
	if modified:
		updateAccountFile()

def checkToken(token=None):
	"""
		Checks the user authentification in IFrame and Flash apps using the access_token parameter.
		Token defaults to field 'token' in account
		@return
			True if authentification is ok
			False if there are some problems
	"""
	if token is None:
		if 'token' in account:
			token = account['token']
		else: return False

	r = requests.get('https://api.vk.com/method/secure.checkToken', params={'access_token': token})
	if 'error' in r:
		print(r['error']['error_msg'])
		return False
	return True

def auth(f=False):
	"""
		Authorizes using the file 'account.py'. Asks user for account info if it's not enough
	"""
	checkAccount('permissions', 'app_id', 'api_v')
	if checkToken() and not f:
		print('Your token is still working, no need to authorize.')
		print('Pass f=True argument if you want to force authorization')
		return

	sess = VKAuth(account['permissions'], account['app_id'], account['api_v'])
	sess.auth()
	account['token'] = sess.get_token()
	updateAccountFile()

def getRequest(method, **params):
	"""
		Sends GET request to api.vk.com with specified method and params.
		Access token is added to params automatically
		@args
			method - (str). Name of the method (i.e. 'users.get')
		@return
			None if user doesn't have token and rejects to authorize
			Dictionary with response
	"""
	if not 'token' in account:
		print('Seems that your access token is missing.')
		answer = input('Authorize to get it?(Y/n) ').lower()
		while answer not in ['y', 'n', 'yes', 'no']:
			answer = input("Please type 'y' or 'n': ").lower()
		if answer in ['y', 'yes']:
			auth()
		else:
			return None

	params['access_token'] = account['token']
	r = requests.get('https://api.vk.com/method/'+method+'?', params=params)
	j = r.json()
	if 'error' in j:
		msg = j['error']['error_msg']
		print('\rerror: ' + msg)
		if 'User authorization failed' in msg:
			auth()
			return getRequest(method, **params)
		elif 'Too many requests per second' in msg:
			time.sleep(0.1)
			return getRequest(method, **params)
	return j

def findFriends(id=None, depth=1, file_name='ids.py', keep_old=False):
	"""
		finds friends using breadth-first algorithm
		@args
			id – (int). id of user whose friends to search
			depth – (int). How deep in friends to search (e.g. for friends of friends depth = 2)
			file_name – (str). Name of a file to write found ids in
	"""
	if id is None:
		if 'id' in account:
			id = account['id']
		else:
			id = int(input('id = '))
	if keep_old and os.path.isfile(file_name):
		from ids import IDS
		friends = IDS
		friends = bfs(id, depth=depth, found=friends)
		if IDS == friends:
			return
	else:
		friends = bfs(id, depth=depth)
	f = open(file_name, 'w')
	f.write('IDS=' + str(friends))
	f.close()
	print('\ndone')

def bfs(start, depth=1, found=None):
	if depth <= 0: return found
	if found is None:
		found = set([start])
	request = getRequest('friends.get', user_id = start, fields = 'deactivated')
	if 'error' in request: return found
	friends = request['response']
	ids = {friend['uid'] for friend in friends if 'deactivated' not in friend}
	new_found = ids - found
	found |= new_found
	print('\rfound: {0}'.format(len(found)), end='')
	if depth > 1:
		for i in new_found:
			found = bfs(i, depth-1, found)
	return found