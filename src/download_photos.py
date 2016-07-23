from vkapi import photo_downloader as pd

p = pd.PhotoDownloader()
p.api.findFriends(p.user_id, depth=1, file_name='ids')
p.updateIds()
p.downloadWithFaces(photo_count=25, thread_count=10, photo_type='x')