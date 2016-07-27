import threading
from urllib.request import urlretrieve as retrieve
import os

NO_FILTER = 0
ONE_FACE = 1
ANY = 2

class Downloader(object):
	def __init__(self, max_threads=10):
		self.nthreads = 0
		self.max_threads = max_threads
		self.queue = [] # list of *args tuples for __download

	def push_download(self, *args):
		queue.append(args)
		self.update()

	def _finish_download(self):
		self.nthreads -= 1
		self.update()

	def update(self):
		while self.nthreads < self.max_threads:
			self._download(queue.pop(0))

	def _download(self, *args, **kwargs):
		t = threading.Thread(	target=self.__download, 
								name='download-%d' % self.nthreads,
								args=(self,)+args,
								kwargs=kwargs)
		self.nthreads += 1
		t.start()

	def __download(self, link, path, filter=ONE_FACE):
		retrieve(link, path)
		if filter is not NO_FILTER:
			faces = detect_faces(path)
			if filter is ONE_FACE:
				if len(faces) != 1:
					os.remove(path)
			elif filter is ANY:
				if len(faces) == 0:
					os.remove(path)
			else:
				raise RuntimeError('There is no such filter ' + str(filter))
		self._finish_download()
