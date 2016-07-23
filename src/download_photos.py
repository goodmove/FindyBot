from src.vkapi import photo_downloader as pd

p = pd.PhotoDownloader()
# p.api.findFriends(p.user_id, depth=2, file_name='ids')
p.updateIds()
p.downloadAll(photo_count=10, thread_count=10, no_service_albums=0, check_face=True)