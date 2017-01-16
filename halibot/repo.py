import json
import os.path
import base64
import urllib.request
import zipfile
import tarfile

noGit = False
try:
	from git import Repo
except ImportError:
	noGit = True

def isGit(path):
	return path.startswith("git://")

def isZip(path):
	return path.endswith(".zip")

def isTar(path):
	return path.endswith( (
		".tar",
		".tar.gz",
		".tar.bz2",
		".tar.xz",
		".tar.lz",
		".tar.lzma",
		".tgz",
		".tb2",
		".tbz",
		".tbz2",
		".tlz",
		".txz",
		".tZ"
	) )

class Repo():

	def __init__(self, url):

#		cache = "repo-cache/" + base64.urlsafe_b64encode(url)
#
#		if os.path.exits(cache):
#			with open(cache + ".etag") as f:
#				etag = f.read()
#			rqst = urllib.request.Request(url)

		text = urllib.request.urlopen(url).read().decode('utf-8')
		self.packages = json.loads(text)

	def fetch(self, name, dst):
		if not name in self.packages:
			return False

		sources = self.packages[name]['sources']

		for src in sources:
			try:
				if isGit(src):
					if noGit:
						raise Exception("The git module is not installed, I cannot clone git repos.")
					print("Trying to git clone '{}'...".format(src))
					Repo.clone_from(src, dst)
				elif isZip(src):
					print("Trying to extract zip from '{}'...".format(src))
					bio = io.BytesIO(urllib.request.urlopen(src).read())
					z = zipfile.ZipFile(bio)
					os.mkdir(dst)
					z.extractall(dst)
				elif src.isTar(src):
					print("Trying to extract tarball from '{}'...".format(src))
					bio = io.BytesIO(urllib.request.urlopen(src).read())
					tar = tarfile.open(mode="r:*", fileobj=bio)
					os.mkdir(dst)
					tar.extractall(dst)
				else:
					raise Exception("I do not know how to handle the path '{}'".format(src))

				return True
			except Exception as e:
				print(e)

		return False
