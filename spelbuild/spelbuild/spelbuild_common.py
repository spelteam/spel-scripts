import re
import subprocess
import os

def runProcess(command):
	process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	output, err = process.communicate()
	retcode = process.returncode
	return (retcode, output, err)

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
	f.write(message + "\n")
	f.close()

def sendMail(to, subject, body, files):
	command = 'mutt -a ' + files + ' -s "' + subject + '" -- ' + to + ' < ' + body
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
	return pwd.strip("\n")

def insertTestIntoDb(test, dbPwd):
	pwd = getDbPwd(dbPwd)
	sql = "insert into pose_mediawiki.unittests (testname) select * from (select '" + test + "') as t where not exists (select 1 from pose_mediawiki.unittests where testname = '" + test + "');"
	runProcess(["mysql", "-u", "root", "-p" + pwd, "-e", sql]);
	return

def updateTestInDb(test, os, status, dbPwd):
	pwd = getDbPwd(dbPwd)
	sql = "update pose_mediawiki.unittests set " + os + "=" + str(status) + " where testname = '" + test + "';"
	runProcess(["mysql", "-u", "root", "-p" + pwd, "-e", sql]);
	return

def getTestList(strings):
	partOneExp = re.compile(r"(\w+[/]\d+[.]|\w+[.])")
	partTwoExp = re.compile(r"\s+(.*)")
	partOne = ""
	partTwo = ""
	tests = []
	strings = strings.decode('utf-8')
	for string in strings.splitlines():
		partTwo = ""
		partOneRes = partOneExp.search(string)
		if partOneRes is not None:
			partOne = partOneRes.groups()[0]
		else:
			partTwoRes = partTwoExp.search(string)
			if partTwoRes is not None:
				partTwo = partTwoRes.groups()[0]
				if partOne != "" and partTwo != "":
					tests.append(partOne + partTwo)
	tests.sort()
	return tests

def parseTestResults(text, file):
	runExp = re.compile(r"(\[.*RUN.*\].*)")
	okExp = re.compile(r"(\[.*OK.*\].*)")
	failedExp = re.compile(r"(\[.*FAILED.*\].*)")
	for line in text.splitlines():
		runRes = runExp.search(line)
		if runRes is not None:
			writeLog(runRes.groups()[0], file)
			continue
		okRes = okExp.search(line)
		if okRes is not None:
			writeLog(okRes.groups()[0], file)
			return 1
			break
		failedRes = failedExp.search(line)
		if failedRes is not None:
			writeLog(failedRes.groups()[0], file)
			return 0
			break
	return 0

def runTest(test, app, testsFile, logFile, os, dbPwd):
	if os == "linux":
		insertTestIntoDb(test, dbPwd)
	retcode, output, err = runProcess([app, "--gtest_filter=" + test])
	output = output.decode('utf-8')
	writeLog(output, testsFile)
	status = parseTestResults(output, logFile)
	if os == "linux":
		updateTestInDb(test, os, status, dbPwd)
	return status

def runTests(app, logFile, testsFile, os, dbPwd, resultsFile):
	retcode, output, err = runProcess([app, "--gtest_list_tests"])
	tests = getTestList(output)
	writeLog("\nTests Summary:\n", logFile)
	writeLog("", testsFile)
	failedList = []
	failed = 0;
	success = 0;
	for test in tests:
		if test.find("DISABLED_") == -1:
			status = runTest(test, app, testsFile, logFile, os, dbPwd)
			if status == 1:
				success += 1
			else:
				failed += 1
				failedList.append(test)
			if os == "windows":
				writeLog(str(status) + " " + test, resultsFile)
	writeLog("\nFailed Tests:\n", logFile)
	failedList.sort()
	for test in failedList:
		writeLog(test, logFile)
	writeLog("\nOK: " + str(success), logFile)
	writeLog("Failed: " + str(failed), logFile)
	writeLog("Total: " + str(success + failed), logFile)
	return
