import os

def createLockFile(file):
	if os.path.exists(file):
		return False
	else:
		os.makedirs(file)
		return True

def deleteLockFile(file):
	if os.path.exists(file):
		os.rmdir(file)
