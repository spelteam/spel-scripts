from spelbuild_common import *

unitTests = "D:/posebuild/tests/Debug"
logFile = "D:/speltests.exe.log"
testsFile = "D:/tests.log"
resultsFile = "D:/tests.results"
archFile = "D:/windowslogs.7z"
SevenZip = "C:/Program Files/7-Zip/7z.exe"
lockFile = "D:/windows.lock"
uploadFile = "D:/upload.script"
psftp = "C:/Program Files (x86)/PuTTY/psftp.exe"

def run():
	runTests("speltests.exe", logFile, testsFile, "windows", None, resultsFile)
	return

def clean():
	if os.path.exists(logFile):
		os.remove(logFile)
	if os.path.exists(testsFile):
		os.remove(testsFile)
	if os.path.exists(resultsFile):
		os.remove(resultsFile)
	if os.path.exists(archFile):
		os.remove(archFile)
	if os.path.exists(lockFile):
		os.remove(lockFile)
	if os.path.exists(uploadFile):
		os.remove(uploadFile)

def start():
	cwd = os.getcwd()
	os.chdir(unitTests)

	run()
	runProcess([SevenZip, "a", archFile, logFile, testsFile, resultsFile])

	f = open(lockFile, "w")
	f.write("LOCK")
	f.close()

	f = open(uploadFile, "w")
	f.write('put ' + archFile + '\n')
	f.write('put ' + resultsFile + '\n')
	f.write('put ' + lockFile + '\n')
	f.write('exit\n')
	f.close()

	runProcess([psftp, "-b", uploadFile])

	clean()

	os.chdir(cwd)
	return

start()