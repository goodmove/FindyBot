import photos_downloader as pd

p = pd.PhotoDownloader()
p.downloadAll(photo_count=10, thread_count=10)