import photos_downloader as pd

p = pd.PhotoDownloader(account_file='account')
p.downloadAll(batch_size = 50, thread_count = 50, field='photo_200_orig')