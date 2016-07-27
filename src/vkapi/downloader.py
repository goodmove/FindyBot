from src.vkapi import vkapi
import threading
from urllib.request import urlretrieve as retrieve

class Downloader(object):
	def __init__(self, max_threads=10):
		self.nthreads = 0
		self.max_threads = max_threads
		self.queue = [] # list of *args tuples for __download

	def push_download(self, *args):
		queue.append(args)

	def _finish_download(self):
		self.nthreads -= 1
		self.update()

	def update(self):
		while self.nthreads < self.max_threads:
			self._download(queue.pop(0))

	def _download(self, *args):
		t = threading.Thread(	target=self.__download, 
								name='download-%d' % self.nthreads,
								args=(self,)+args)
		self.nthreads += 1
		t.start()

	def __download(self, link, path):
		retrieve(link, path)
		self._finish_download()
