from src.vkapi import photo_downloader as pd

p = pd.PhotoDownloader()
# p.api.findFriends(p.user_id, depth=1, file_name='ids')
p.updateIds()
p.downloadAll(
	photo_count=80, 
	thread_count=10, 
	show_thread_count=True, 
	check_face=True,
	path='photos', 
	face_landmarks='landmarks.txt', 
	file_format='.jpg', 
	photo_type='x', 
	no_service_albums=0, 
	create_id_folders=False, 
	keep_old=False, 
	displacement=None, 
	extend=False, 
	crop=False, 
	resize=False
)
