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

def writeLog(message, file, create = False):
	mode = "a"
	if create:
		mode = "w"
	f = open(file, mode)
	f.write(message)
	f.close()

def sendMail(to, subject, body, files):
	command = "mutt -s" + subject + " " + to + " < " + body
	process = subprocess.Popen(command, shell=True)
	process.communicate()

def sendMails(to, subject, body, files):
	f = open(to, 'r')
	lines = f.readlines()
	for line in lines:
		addr = line.rstrip('\n')
		sendMail(addr, subject, body, files)
	f.close()

def getDbPwd(file):
	f = open(file, "r")
	pwd = f.read()
	f.close()
	return pwd

def insertTestIntoDb(test, dbPwd):
	pwd = getDbPwd(dbPwd)
	sql = "insert into pose_mediawiki.unittests (testname) select * from (select '" + test + "') as t where not exists (select 1 from pose_mediawiki.unittests where testname = '" + test + "';"
	runProcess(["mysql", "-u", "root", "-p" + pwd, "-e", sql]);
	return

def updateTestInDb(test, os, status, dbPwd):
	pwd = getDbPwd(dbPwd)
	sql = "update pose_mediawiki.unittests set " + os + "=" + str(status) + "where testname = '" + test + "';"
	runProcess(["mysql", "-u", "root", "-p" + pwd, "-e", sql]);
	return
