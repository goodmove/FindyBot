import vkapi

def get_friend_ids(api, id, ids, depth):
	global count
	if depth <= 0: return
	payload = {'user_id':id}
	request = api.getRequest('friends.get', payload)
	if request is None: return
	friends = request['response']
	for friend in friends:
		if not friend in ids:
			ids.append(friend)
			count += 1
			print('\rfound friends: {0}'.format(count), end='')
			get_friend_ids(api, friend, ids, depth-1)

account = open('account', 'r')
acc_data = dict([field.split(':') for field in account.read().split(',')])

api = vkapi.vkapi(	app_id = acc_data['app_id'],
					app_secure = acc_data['app_secure'])

print(acc_data)

ids = []
count = 0

get_friend_ids(api, acc_data['id'], ids, 1)
print('\ndone')
print('ids found: ', len(ids))

f = open('ids', 'w')
f.write(str(ids))
f.close()