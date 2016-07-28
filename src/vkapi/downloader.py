from src.image_processing import impros
from urllib.request import urlretrieve as retrieve
import threading
import os


class Downloader(object):
	NO_FILTER = 0
	ONE_FACE = 1
	ANY = 2
	def __init__(self, max_threads=10, finish=None):
		self.nthreads = 0
		self.max_threads = max_threads
		self.queue = [] # list of *args tuples for __download
		self.finish = finish

	def push_download(self, *args, **kwargs):
		self.queue.append((args, kwargs))
		self.update()

	def _finish_download(self):
		self.nthreads -= 1
		self.update()

	def update(self):
		while self.nthreads < self.max_threads and len(self.queue) > 0:
			args, kwargs = self.queue.pop(0)
			self._download(*args, **kwargs)
		if self.nthreads is 0 and len(self.queue) is 0:
			if self.finish:
				self.finish()

	def _download(self, *args, **kwargs):
		t = threading.Thread(	target=self.__download, 
								name='download-%d' % self.nthreads,
								args=args,
								kwargs=kwargs)
		self.nthreads += 1
		t.start()

	def __download(self, link, path, filter=ONE_FACE):
		retrieve(link, path)
		if filter is not self.NO_FILTER:
			faces = impros.detect_faces(path=path)
			if filter is self.ONE_FACE:
				if len(faces) != 1:
					os.remove(path)
			elif filter is self.ANY:
				if len(faces) == 0:
					os.remove(path)
			else:
				raise RuntimeError('There is no such filter ' + str(filter))
		self._finish_download()
