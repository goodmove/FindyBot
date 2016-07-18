from vkapi import photo_downloader as pd

p = pd.PhotoDownloader()
p.downloadAll(photo_count=10, thread_count=10, no_service_albums=0)