import AO3
import os
import sys
import collections
import json
import time
import datetime
import math
import win32api
import glob
import pyperclip
import getpass

# Slows down the rate of requests sent to AO3 servers (too many requests means you will be blocked from making more requests from their servers and running into an error)
AO3.utils.limit_requests()

# Clears the screen by removing all text
def clearScreen():
	if (os.name == "nt"):
		os.system("cls")
	else:
		os.system("clear")

# Formats text based on alignment and length
def formatText(text, alignment, length):
	text = str(text)

	if (alignment == 0):
		alignment = "<"
	elif (alignment == 1):
		alignment = "^"
	elif (alignment == 2):
		alignment = ">"

	if (len(str(text)) > length):
		text = text[0:(length - 3)] + "..."

	return str("{:" + alignment + str(length) + "}").format(text)

# Starts the app and shows the main menu
def startApp():
	appRunning = True
	filePath = ""
	scoredFolders = []
	markedFolders = []
	recapSettings = {"backlogCounts": True, "readCounts": True, "ratings": 0, "warnings": 0, "categories": 0, "fandoms": 0, "relationships": 5, "characters": 5, "tags": 5, "languages": 0}
	lineLimit = 69

	while (appRunning):
		lineCount = 3

		if (recapSettings["backlogCounts"] and markedFolders.count(0) > 0):
			lineCount += 7 + markedFolders.count(0)
			if (recapSettings["readCounts"] and markedFolders.count(1) > 0):
				lineCount += 3 + markedFolders.count(1)
		elif (recapSettings["readCounts"] and markedFolders.count(1) > 0):
			lineCount += 7 + markedFolders.count(1)

		for currentData in recapSettings:
			if (type(recapSettings[currentData]) == int and recapSettings[currentData] > 0):
				lineCount += 5 + recapSettings[currentData]

		clearScreen()
		print("AO3 Recap")
		print("---------")
		if (len(filePath) == 0):
			print("1. Select Data (None)")
		else:
			currentTimestamp = filePath.split("\\")[-1].rstrip(".json").split("_")
			currentDate = "{0}/{1}/{2}".format(currentTimestamp[0], currentTimestamp[1], currentTimestamp[2])
			if (int(currentTimestamp[3]) > 12):
				currentTime = "{0}:{1} PM".format(int(currentTimestamp[3]) - 12, currentTimestamp[4])
			else:
				currentTime = "{0}:{1} AM".format(int(currentTimestamp[3]), currentTimestamp[4])
			print("1. Select Data (" + currentDate + " " + currentTime + ")")
			print("2. Score Folders")
			print("3. Mark Folders")
			print("4. Recap Settings (!)") if (lineCount > lineLimit) else print("4. Recap Settings")
			print("Q. Create Recap")
		print("`. Quit")

		try:
			userInput = input("> ")
			if (userInput.isdecimal()):
				userInput = int(userInput)
				if (userInput == 1):
					filePath, scoredFolders, markedFolders = selectData(filePath, scoredFolders, markedFolders)
				elif (2 <= userInput <= 4 and len(filePath) > 0):
					if (userInput == 2):
						scoredFolders = scoreFolders(filePath, scoredFolders)
					elif (userInput == 3):
						markedFolders = markFolders(filePath, markedFolders)
					elif (userInput == 4):
						recapSettings = changeRecapSettings(markedFolders, recapSettings)
			elif (userInput.lower() == "q" and lineCount <= lineLimit and len(filePath) > 0):
				createRecap(filePath, scoredFolders, markedFolders, recapSettings)
			elif (userInput == "`"):
				appRunning = False
				clearScreen()
				sys.exit()
		except:
			continue

# Shows the menu that allows the user to pick their data set
def selectData(path, scores, marks):
	selectingData = True
	selectedPath = ""
	selectedScoredFolders = []
	selectedMarkedFolders = []

	while (selectingData):
		allAvailableOptions = []
		for currentJSONFile in glob.glob("saved\\*.json"):
			allAvailableOptions.insert(0, currentJSONFile.split("\\")[-1])

		clearScreen()
		print("AO3 Recap > Select Data")
		print("-----------------------")
		print("* Only 10 data sets are saved at a time.")
		print("Q. Create New Data Set")
		for i in range(min(len(allAvailableOptions), 10)):
			currentTimestamp = allAvailableOptions[i].rstrip(".json").split("_")
			currentDate = "{0}/{1}/{2}".format(currentTimestamp[0], currentTimestamp[1], currentTimestamp[2])
			if (int(currentTimestamp[3]) > 12):
				currentTime = "{0}:{1} PM".format(int(currentTimestamp[3]) - 12, currentTimestamp[4])
			else:
				currentTime = "{0}:{1} AM".format(int(currentTimestamp[3]), currentTimestamp[4])
			print(str(i + 1) + ". " + currentDate + " " + currentTime)
		print("`. Back")

		try:
			userInput = input("> ")
			if (userInput.lower() == "q"):
				createNewDataSet()
			elif (userInput.isdecimal()):
				userInput = int(userInput)
				if (1 <= userInput <= len(allAvailableOptions)):
					selectedPath = "saved\\" + str(allAvailableOptions[userInput - 1])
					with open(selectedPath) as f:
						data = json.load(f)
						for i in range(len(data["folderNames"])):
							selectedScoredFolders.append(1)
							selectedMarkedFolders.append(1)
					selectingData = False
			elif (userInput == "`"):
				selectedPath = path
				selectedScoredFolders = scores
				selectedMarkedFolders = marks
				selectingData = False
		except:
			continue

	return selectedPath, selectedScoredFolders, selectedMarkedFolders

# Shows the menu that allows the user to create a new data set
def createNewDataSet():
	creatingNewDataSet = True
	filePath = ""
	currentSession = AO3.GuestSession()

	while (creatingNewDataSet):
		clearScreen()
		print("AO3 Recap > Select Data > Create New Data Set")
		print("---------------------------------------------")
		if (len(filePath.split("\\")) > 4):
			print("1. Select HTML Bookmark File (" + " > ".join(filePath.split("\\")[:2]) + " > ... > " + " > ".join(filePath.split("\\")[-2:]) + ")")
		elif (1 < len(filePath.split("\\")) <= 4):
			print("1. Select HTML Bookmark File (" + filePath.rstrip("\\").replace("\\", " > ") + ")")
		else:
			print("1. Select HTML Bookmark File")
		print("2. Log In (" + currentSession.username + ")") if (len(currentSession.username) > 0) else print("2. Log In (optional)")
		if (len(filePath) > 0):
			print("Q. Start")
		print("`. Back")

		try:
			userInput = input("> ")
			if (userInput.isdecimal()):
				userInput = int(userInput)
				if (userInput == 1):
					filePath = selectFile()
				elif (userInput == 2):
					currentSession = logIn(currentSession)
			elif (userInput.lower() == "q" and len(filePath) > 0):
				parseData(filePath, currentSession)
				creatingNewDataSet = False
			elif (userInput == "`"):
				creatingNewDataSet = False
		except:
			continue

# Shows the file explorer which allows the user to pick an HTML bookmark file in order to create a new data set 
def selectFile():
	selectingFile = True
	currentPath = ""
	currentPage = 0

	while (selectingFile):
		lastFolder = ""
		userInput = ""

		allAvailableOptions = []
		if (".html" not in currentPath):
			if (len(currentPath) == 0):
				allDrives = win32api.GetLogicalDriveStrings()
				allDrives = allDrives.replace("\\", "").split('\000')[:-1]
				allAvailableOptions = allDrives
			else:
				for currentFolder in glob.glob(currentPath + "*\\"):
					allAvailableOptions.append(currentFolder.split("\\")[-2])
				for currentHTMLFile in glob.glob(currentPath + "*.html"):
					allAvailableOptions.append(currentHTMLFile.split("\\")[-1])

		clearScreen()
		print("AO3 Recap > Select Data > Create New Data Set > Select File")
		print("-----------------------------------------------------------")
		print("Path: This PC > " + currentPath.rstrip("\\").replace("\\", " > "))

		if (".html" in currentPath):
			print("\nConfirm?")
			print("1. Yes")
			print("`. No")
		else:
			for i in range(min(len(allAvailableOptions) - (10 * currentPage), 10)):
				print(str(i + 1)[-1] + ". " + allAvailableOptions[(10 * currentPage) + i])
			print("`. Back")
			if (len(currentPath) > 0):
				print()
				print("Page " + str(currentPage + 1) + "/" + str(math.ceil(len(allAvailableOptions) / 10)))
				if (currentPage > 0):
					print("Q. Last Page")
				if (currentPage < math.ceil(len(allAvailableOptions) / 10) - 1):
					print("W. Next Page")

		try:
			userInput = input("> ")
			if (".html" in currentPath):
				if (userInput.isdecimal() and int(userInput) == 1):
					selectingFile = False
				elif (userInput == "`"):
					currentPath = currentPath.split("\\")
					currentPath = currentPath[:-1]
					currentPath = "\\".join(currentPath)
					currentPath += "\\"
			else:
				if (userInput.isdecimal()):
					userInput = int(userInput)
					if (1 <= userInput <= min(len(allAvailableOptions) - (10 * currentPage), 9) or (userInput == 0 and len(allAvailableOptions) - (10 * currentPage) >= 10)):
						if (userInput == 0 and len(allAvailableOptions) - (10 * currentPage) >= 10):
							userInput = "10"
						currentPath += allAvailableOptions[(10 * currentPage) + int(userInput) - 1]
						if (".html" not in allAvailableOptions[(10 * currentPage) + int(userInput) - 1]):
							currentPath += "\\"
							currentPage = 0
				elif (userInput == "`"):
					if (len(currentPath) > 0):
						currentPath = currentPath.split("\\")
						lastFolder = currentPath[-2]
						currentPath = currentPath[:-2]
						currentPath = "\\".join(currentPath)
						if (len(currentPath) > 0):
							currentPath += "\\"
							try:
								allFolders = []
								for currentFolder in glob.glob(currentPath + "*\\"):
									allFolders.append(currentFolder.split("\\")[-2])
								currentPage = math.floor(allFolders.index(lastFolder) / 10)
							except:
								currentPage = 0
						else:
							currentPage = 0
					else:
						selectingFile = False
				elif (userInput.lower() == "q" and len(currentPath) > 0 and currentPage > 0):
					currentPage -= 1
				elif (userInput.lower() == "w" and len(currentPath) > 0 and currentPage < math.ceil(len(allAvailableOptions) / 10) - 1):
					currentPage += 1
		except:
			continue

	return currentPath

# Shows the menu that allows the user to log into their AO3 account
def logIn(session):
	loggingIn = True
	enteringUsername = False
	enteringPassword = False
	currentUsername = ""
	currentPassword = ""
	newSession = session
	wrongCredentials = False
	
	while (loggingIn):
		clearScreen()
		print("AO3 Recap > Select Data > Create New Data Set > Log In")
		print("------------------------------------------------------")
		if (enteringUsername):
			print("Please enter your AO3 username.")
		elif (enteringPassword):
			print("Please enter your AO3 password.")
		else:
			print("1. Username (" + currentUsername + ")") if (len(currentUsername) > 0) else print("1. Username")
			print("2. Password (" + "*" * len(currentPassword) + ")") if (len(currentPassword) > 0) else print("2. Password")
			if (wrongCredentials):
				print("Q. Log In (Wrong Credentials!)")
				wrongCredentials = False
			else:
				print("Q. Log In")
		print("`. Back")

		try:
			if (enteringPassword):
				userInput = getpass.getpass("> ")
			else:
				userInput = input("> ")
			if (enteringUsername):
				currentUsername = userInput
				enteringUsername = False
			elif (enteringPassword):
				currentPassword = userInput
				enteringPassword = False
			else:
				if (userInput.isdecimal()):
					userInput = int(userInput)
					if (userInput == 1):
						enteringUsername = True
					elif (userInput == 2):
						enteringPassword = True
				elif (userInput.lower() == "q"):
					try:
						clearScreen()
						print("AO3 Recap > Select Data > Create New Data Set > Log In")
						print("------------------------------------------------------")
						print("Logging in...")
						newSession = AO3.Session(currentUsername, currentPassword)
						loggingIn = False
					except AO3.utils.LoginError:
						wrongCredentials = True
				elif (userInput == "`"):
					loggingIn = False
		except:
			continue

	return newSession

# Shows a loading bar while the program gets metadata from AO3 servers
def parseData(path, session):
	with open(path) as f:
		bookmarkFileLines = f.readlines()

	totalEntries = 0
	loadedEntries = 0
	currentCategory = -1
	# Order: title, first author username, ratings, warnings, categories, fandoms, ships, characters, tags, language, published, updated, word count, chapter count, kudos, bookmarks, hits
	folderNames = []
	savedData = []
	lastFolderName = ""

	for currentLine in bookmarkFileLines:
		if ("/works/" in currentLine or "/series/" in currentLine):
			totalEntries += 1

	for currentLine in bookmarkFileLines:
		try:
			if ("</H3>" in currentLine):
				lastFolderName = currentLine.split(">")[-2][:-4]
			elif ("/works/" in currentLine):
				if (len(lastFolderName) > 0 and (len(savedData) == 0 or (len(savedData) > 0 and len(savedData[-1]) > 0))):
					currentCategory += 1
					folderNames.append(lastFolderName)
					savedData.append([])
					lastFolderName = ""

				loadedEntries += 1
				currentURL = currentLine.split()[1][6:-1]
				currentID = AO3.utils.workid_from_url(currentURL)
				currentWork = AO3.Work(currentID, session=session, load_chapters=False)

				clearScreen()
				print("AO3 Recap > Select Data > Create New Data Set")
				print("---------------------------------------------")
				print("|" + "{:<71}".format("=" * round(71 * loadedEntries / totalEntries)) + "|")
				print("{:<59}".format("Loading \"" + str(currentWork.title[0:46]) + "\"") + "{:>14}".format(str(loadedEntries) + "/" + str(totalEntries) + " (" + str(round(loadedEntries / totalEntries * 100)) + "%)"))

				if ("chapters" in currentLine):
					currentWork.load_chapters()
					currentChapterNumber = 0
					currentChapterID = int(currentURL.split("/")[-1])
					for currentChapter in currentWork.chapters:
						currentChapterNumber += 1
						if (currentChapterID == currentChapter.id):
							break

					for i in range(len(currentWork.relationships)):
						currentWork.relationships[i] = currentWork.relationships[i].replace("Jesse McCree", "Cole Cassidy")
					for i in range(len(currentWork.characters)):
						currentWork.characters[i] = currentWork.characters[i].replace("Jesse McCree", "Cole Cassidy")
					savedData[currentCategory].append([currentWork.title, currentWork.authors[0].username, currentWork.rating, currentWork.warnings, currentWork.categories, currentWork.fandoms, currentWork.relationships, currentWork.characters, currentWork.tags, currentWork.language, currentWork.date_published, currentWork.date_updated, currentWork.chapters[currentChapterNumber - 1].words, 1, currentWork.kudos, currentWork.bookmarks, currentWork.hits])
				else:
					for i in range(len(currentWork.relationships)):
						currentWork.relationships[i] = currentWork.relationships[i].replace("Jesse McCree", "Cole Cassidy")
					for i in range(len(currentWork.characters)):
						currentWork.characters[i] = currentWork.characters[i].replace("Jesse McCree", "Cole Cassidy")
					savedData[currentCategory].append([currentWork.title, currentWork.authors[0].username, currentWork.rating, currentWork.warnings, currentWork.categories, currentWork.fandoms, currentWork.relationships, currentWork.characters, currentWork.tags, currentWork.language, currentWork.date_published, currentWork.date_updated, currentWork.words, currentWork.nchapters, currentWork.kudos, currentWork.bookmarks, currentWork.hits])
			elif ("/series/" in currentLine):
				if (len(lastFolderName) > 0 and (len(savedData) == 0 or (len(savedData) > 0 and len(savedData[-1]) > 0))):
					currentCategory += 1
					folderNames.append(lastFolderName)
					savedData.append([])
					lastFolderName = ""

				loadedEntries += 1
				currentURL = currentLine.split()[1][6:-1]
				currentID = currentURL.split("/")[-1]
				currentSeries = AO3.Series(currentID, session=currentSession)

				clearScreen()
				print("AO3 Recap > Select Data > Create New Data Set")
				print("---------------------------------------------")
				print("|" + "{:<71}".format("=" * round(71 * loadedEntries / totalEntries)) + "|")
				print("{:<59}".format("Loading \"" + str(currentSeries.name[0:46]) + "\"") + "{:>14}".format(str(loadedEntries) + "/" + str(totalEntries) + " (" + str(round(loadedEntries / totalEntries * 100)) + "%)"))

				currentWorks = []
				currentThreads = []
				for currentWork in currentSeries.work_list:
					currentWorks.append(currentWork)
					currentThreads.append(currentWork.reload(threaded=True))
				for currentThread in currentThreads:
					currentThread.join()

				for currentWork in currentWorks:
					for i in range(len(currentWork.relationships)):
						currentWork.relationships[i] = currentWork.relationships[i].replace("Jesse McCree", "Cole Cassidy")
					for i in range(len(currentWork.characters)):
						currentWork.characters[i] = currentWork.characters[i].replace("Jesse McCree", "Cole Cassidy")
					savedData[currentCategory].append([currentWork.title, currentWork.authors[0].username, currentWork.rating, currentWork.warnings, currentWork.categories, currentWork.fandoms, currentWork.relationships, currentWork.characters, currentWork.tags, currentWork.language, currentWork.date_published, currentWork.date_updated, currentWork.words, currentWork.nchapters, currentWork.kudos, currentWork.bookmarks, currentWork.hits])
		except:
			continue

	savedDataDict = {
		"folderNames": folderNames,
		"savedData": savedData
	}

	with open(time.strftime("saved\\%Y_%m_%d_%H_%M.json", time.localtime()), "w") as f:
		json.dump(savedDataDict, f, default=str)

	allSavedData = glob.glob("saved\\*.json")
	if (len(allSavedData) > 10):
		oldestFile = min(allSavedData, key=os.path.getctime)
		os.remove(os.path.abspath(oldestFile))

	clearScreen()
	print("AO3 Recap > Select Data > Create New Data Set")
	print("---------------------------------------------")
	print("|" + "{:<71}".format("=" * round(71 * loadedEntries / totalEntries)) + "|")
	print("{:<59}".format("Loading Complete") + "{:>14}".format(str(loadedEntries) + "/" + str(totalEntries) + " (" + str(round(loadedEntries / totalEntries * 100)) + "%)"))
	print("ENTER. Continue")
	input("> ")

# Shows the menu that allows the user to score works within each folder
def scoreFolders(path, scores):
	with open(path) as f:
		data = json.load(f)

	scoringFolders = True
	allFolders = data["folderNames"]
	selectedFolder = -1

	while (scoringFolders):
		userInput = ""

		clearScreen()
		print("AO3 Recap > Score Folders")
		print("-------------------------")
		if (selectedFolder == -1):
			for i in range(len(allFolders)):
				print(str(i + 1) + ". " + allFolders[i] + " (" + str(scores[i]) + " pts.)") if scores[i] != 1 else print(str(i + 1) + ". " + allFolders[i] + " (" + str(scores[i]) + " pt.)")
		else:
			print("Each work in \"" + allFolders[selectedFolder] + "\" is worth _ point(s).")
		print("`. Back")

		try:
			userInput = input("> ")
			if (selectedFolder == -1):
				if (userInput.isdecimal()):
					userInput = int(userInput)
					if (1 <= userInput <= len(allFolders)):
						selectedFolder = userInput - 1
				elif (userInput == "`"):
					scoringFolders = False
			elif (selectedFolder >= 0):
				if (userInput.lstrip("-").isdecimal()):
					userInput = int(userInput)
					scores[selectedFolder] = userInput
					selectedFolder = -1
				elif (userInput == "`"):
					selectedFolder = -1
		except:
			continue

	return scores

# Shows the menu that allows the user to mark specific folders as backlog or read
def markFolders(path, marks):
	with open(path) as f:
		data = json.load(f)

	markingFolders = True
	allFolders = data["folderNames"]

	while (markingFolders):
		userInput = ""

		clearScreen()
		print("AO3 Recap > Mark Folders")
		print("------------------------")
		for i in range(len(allFolders)):
			print(str(i + 1) + ". " + formatText(allFolders[i], 0, 24), end="")
			print("(backlog)", end=" / ") if (marks[i] == 0) else print(" backlog ", end=" / ")
			print("(read)") if (marks[i] == 1) else print(" read ")
		print("`. Back")

		try:
			userInput = input("> ")
			if (userInput.isdecimal()):
				userInput = int(userInput)
				if (1 <= userInput <= len(allFolders)):
					marks[userInput - 1] = 0 if marks[userInput - 1] == 1 else 1
			elif (userInput == "`"):
				markingFolders = False
		except:
			continue

	return marks

# Shows the menu that lets the user change the settings of their AO3 recap
def changeRecapSettings(marks, settings):
	changingSettings = True
	selectedSetting = ""
	lineLimit = 69

	while (changingSettings):
		lineCount = 3

		if (settings["backlogCounts"] and marks.count(0) > 0):
			lineCount += 7 + marks.count(0)
			if (settings["readCounts"] and marks.count(1) > 0):
				lineCount += 3 + marks.count(1)
		elif (settings["readCounts"] and marks.count(1) > 0):
			lineCount += 7 + marks.count(1)

		for currentData in settings:
			if (type(settings[currentData]) == int and settings[currentData] > 0):
				lineCount += 5 + settings[currentData]

		clearScreen()
		print("AO3 Recap > Recap Settings")
		print("--------------------------")

		if (len(selectedSetting) == 0):
			print("Lines available: " + str(lineLimit - lineCount))
			print("1. " + formatText("Backlog Counts", 0, 24) + "Show") if settings["backlogCounts"] else print("1. " + formatText("Backlog Counts", 0, 24) + "Hide")
			print("2. " + formatText("Read Counts", 0, 24) + "Show") if settings["readCounts"] else print("2. " + formatText("Read Counts", 0, 24) + "Hide")
			print("3. " + formatText("Ratings", 0, 24) + "Up to " + str(settings["ratings"])) if settings["ratings"] > 0 else print("3. " + formatText("Ratings", 0, 24) + "Hide")
			print("4. " + formatText("Warnings", 0, 24) + "Up to " + str(settings["warnings"])) if settings["warnings"] > 0 else print("4. " + formatText("Warnings", 0, 24) + "Hide")
			print("5. " + formatText("Categories", 0, 24) + "Up to " + str(settings["categories"])) if settings["categories"] > 0 else print("5. " + formatText("Categories", 0, 24) + "Hide")
			print("6. " + formatText("Fandoms", 0, 24) + "Up to " + str(settings["fandoms"])) if settings["fandoms"] > 0 else print("6. " + formatText("Fandoms", 0, 24) + "Hide")
			print("7. " + formatText("Relationships", 0, 24) + "Up to " + str(settings["relationships"])) if settings["relationships"] > 0 else print("7. " + formatText("Relationships", 0, 24) + "Hide")
			print("8. " + formatText("Characters", 0, 24) + "Up to " + str(settings["characters"])) if settings["characters"] > 0 else print("8. " + formatText("Characters", 0, 24) + "Hide")
			print("9. " + formatText("Tags", 0, 24) + "Up to " + str(settings["tags"])) if settings["tags"] > 0 else print("9. " + formatText("Tags", 0, 24) + "Hide")
			print("0. " + formatText("Languages", 0, 24) + "Up to " + str(settings["languages"])) if settings["languages"] > 0 else print("0. " + formatText("Languages", 0, 24) + "Hide")
		else:
			if (selectedSetting in ["backlogCounts", "readCounts"]):
				if (selectedSetting == "backlogCounts"):
					print("Show the counts for backlog works.")
				else:
					print("Show the counts for read works.")
				print("* Costs 7 lines if at least 1 count is shown and at least 1 folder is in the current count\n  + 3 lines if both counts are shown and at least 1 folder is in both counts\n  + 1 line per folder.")
				print("1. Show")
				print("2. Hide")
			else:
				print("Show the top _ rankings for \"" + str(selectedSetting) + "\".")
				print("* Can show up to ", end="")
				if (selectedSetting == "ratings"):
					print("5", end="")
				elif (selectedSetting == "warnings" or selectedSetting == "categories"):
					print("6", end="")
				else:
					print("30", end="")
				print(" rankings.")
				print("* Costs 5 lines if shown + 1 line per ranking.")
		print("`. Back")

		try:
			userInput = input("> ")
			if (len(selectedSetting) == 0):
				if (userInput.isdecimal()):
					userInput = int(userInput)
					if (userInput == 1):
						selectedSetting = "backlogCounts"
					elif (userInput == 2):
						selectedSetting = "readCounts"
					elif (userInput == 3):
						selectedSetting = "ratings"
					elif (userInput == 4):
						selectedSetting = "warnings"
					elif (userInput == 5):
						selectedSetting = "categories"
					elif (userInput == 6):
						selectedSetting = "fandoms"
					elif (userInput == 7):
						selectedSetting = "relationships"
					elif (userInput == 8):
						selectedSetting = "characters"
					elif (userInput == 9):
						selectedSetting = "tags"
					elif (userInput == 0):
						selectedSetting = "languages"
				elif (userInput == "`"):
					changingSettings = False
			else:
				if (userInput.isdecimal()):
					userInput = int(userInput)
					if (selectedSetting in ["backlogCounts", "readCounts"]):
						if (userInput == 1):
							settings[selectedSetting] = True
							selectedSetting = ""
						elif (userInput == 2):
							settings[selectedSetting] = False
							selectedSetting = ""
					elif (
						(selectedSetting == "ratings" and 0 <= userInput <= 5)
						or (selectedSetting in ["warnings", "categories"] and 0 <= userInput <= 6)
						or (selectedSetting not in ["backlogCounts", "readCounts", "ratings", "warnings", "categories"] and 0 <= userInput <= 30)
					):
						settings[selectedSetting] = userInput
						selectedSetting = ""
				elif (userInput == "`"):
					selectedSetting = ""
		except:
			continue

	return settings

# Display the recap based on the data set, folder scores, folder marks, and recap settings
def createRecap(path, scores, marks, settings):
	with open(path) as f:
		data = json.load(f)

	uniqueBacklogEntries = []
	uniqueReadEntries = []

	categoryWorkCounts = []
	categoryChapterCounts = []
	categoryWordCounts = []
	for i in range(len(data["folderNames"])):
		categoryWorkCounts.append(0)
		categoryChapterCounts.append(0)
		categoryWordCounts.append(0)

	countableData = ["ratings", "warnings", "categories", "fandoms", "relationships", "characters", "tags", "languages"]
	backlogData = {}
	readData = {}
	combinedData = {}
	rankedData = {}
	for currentData in countableData:
		backlogData[currentData] = collections.Counter()
		readData[currentData] = collections.Counter()
		combinedData[currentData] = collections.Counter()
		rankedData[currentData] = []

	for currentFolder in range(len(data["savedData"])):
		for currentData in data["savedData"][currentFolder]:
			currentTitle = currentData[0]
			currentAuthor = currentData[1]
			currentRating = currentData[2]
			currentWarnings = currentData[3]
			currentCategories = currentData[4]
			currentFandoms = currentData[5]
			currentRelationships = currentData[6]
			currentCharacters = currentData[7]
			currentTags = currentData[8]
			currentLanguage = currentData[9]
			currentDatePublished = currentData[10]
			currentDateUpdated = currentData[11]
			currentWordCount = currentData[12]
			currentChapterCount = currentData[13]
			currentKudos = currentData[14]
			currentBookmarks = currentData[15]
			currentHits = currentData[16]

			uniqueEntry = True
			if (marks[currentFolder] == 0 and currentTitle not in uniqueBacklogEntries):
				uniqueBacklogEntries.append(currentTitle)
			elif (marks[currentFolder] == 1 and currentTitle not in uniqueReadEntries):
				uniqueReadEntries.append(currentTitle)
			else:
				uniqueEntry = False

			categoryWorkCounts[currentFolder] += 1
			categoryChapterCounts[currentFolder] += currentChapterCount
			categoryWordCounts[currentFolder] += currentWordCount

			if (uniqueEntry):
				if (marks[currentFolder] == 0):
					backlogData["ratings"][currentRating] += scores[currentFolder]
				else:
					readData["ratings"][currentRating] += scores[currentFolder]
				combinedData["ratings"][currentRating] += scores[currentFolder]

				for currentWarning in currentWarnings:
					if (marks[currentFolder] == 0):
						backlogData["warnings"][currentWarning] += scores[currentFolder]
					else:
						readData["warnings"][currentWarning] += scores[currentFolder]
					combinedData["warnings"][currentWarning] += scores[currentFolder]

				for currentCategory in currentCategories:
					if (marks[currentFolder] == 0):
						backlogData["categories"][currentCategory] += scores[currentFolder]
					else:
						readData["categories"][currentCategory] += scores[currentFolder]
					combinedData["categories"][currentCategory] += scores[currentFolder]

				for currentFandom in currentFandoms:
					if (marks[currentFolder] == 0):
						backlogData["fandoms"][currentFandom] += scores[currentFolder]
					else:
						readData["fandoms"][currentFandom] += scores[currentFolder]
					combinedData["fandoms"][currentFandom] += scores[currentFolder]

				for currentRelationship in currentRelationships:
					if (marks[currentFolder] == 0):
						backlogData["relationships"][currentRelationship] += scores[currentFolder]
					else:
						readData["relationships"][currentRelationship] += scores[currentFolder]
					combinedData["relationships"][currentRelationship] += scores[currentFolder]

				for currentCharacter in currentCharacters:
					if (marks[currentFolder] == 0):
						backlogData["characters"][currentCharacter] += scores[currentFolder]
					else:
						readData["characters"][currentCharacter] += scores[currentFolder]
					combinedData["characters"][currentCharacter] += scores[currentFolder]

				for currentTag in currentTags:
					if (marks[currentFolder] == 0):
						backlogData["tags"][currentTag] += scores[currentFolder]
					else:
						readData["tags"][currentTag] += scores[currentFolder]
					combinedData["tags"][currentTag] += scores[currentFolder]

				if (marks[currentFolder] == 0):
					backlogData["languages"][currentLanguage] += scores[currentFolder]
				else:
					readData["languages"][currentLanguage] += scores[currentFolder]
				combinedData["languages"][currentLanguage] += scores[currentFolder]

	backlogTotalCounts = {"works": 0, "chapters": 0, "words": 0}
	readTotalCounts = {"works": 0, "chapters": 0, "words": 0}

	for i in range(len(data["folderNames"])):
		if (marks[i] == 0):
			backlogTotalCounts["works"] += categoryWorkCounts[i]
			backlogTotalCounts["chapters"] += categoryChapterCounts[i]
			backlogTotalCounts["words"] += categoryWordCounts[i]
		else:
			readTotalCounts["works"] += categoryWorkCounts[i]
			readTotalCounts["chapters"] += categoryChapterCounts[i]
			readTotalCounts["words"] += categoryWordCounts[i]

	for currentData in countableData:
		rankedData[currentData] = combinedData[currentData].most_common(settings[currentData])

	recapText = ""
	recapText += "+=======================================================================+\n"
	recapText += "| ao3 recap | numbers are approximate and may not be entirely accurate  |\n"
	recapText += "+=======================================================================+\n"

	if (settings["backlogCounts"] or settings["readCounts"]):
		recapText += "| " + formatText("counts", 1, 69) + " |\n"
		recapText += "+-----------------------+---------------+---------------+---------------+\n"

		if (marks.count(0) > 0 and settings["backlogCounts"]):
			recapText += "| " + formatText("folder", 0, 21) + " | " + formatText("works", 0, 13) + " | " + formatText("chapters", 0, 13) + " | " + formatText("words", 0, 13) + " |\n"
			recapText += "+-----------------------+---------------+---------------+---------------+\n"
			for i in range(len(data["folderNames"])):
				if (marks[i] == 0 and categoryWorkCounts[i] > 0):
					recapText += "| " + formatText(data["folderNames"][i], 0, 21) + " | " + formatText(f'{categoryWorkCounts[i]:,}', 2, 13) + " | " + formatText(f'{categoryChapterCounts[i]:,}', 2, 13) + " | " + formatText(f'{categoryWordCounts[i]:,}', 2, 13) + " |\n"
			recapText += "+-----------------------+---------------+---------------+---------------+\n"
			recapText += "| " + formatText("total in backlog", 0, 21) + " | " + formatText(f'{backlogTotalCounts["works"]:,}', 2, 13) + " | " + formatText(f'{backlogTotalCounts["chapters"]:,}', 2, 13) + " | " + formatText(f'{backlogTotalCounts["words"]:,}', 2, 13) + " |\n"

		if (marks.count(1) > 0) and settings["readCounts"]:
			if (marks.count(0) > 0 and settings["backlogCounts"]):
				recapText += "+-----------------------+---------------+---------------+---------------+\n"
			else:
				recapText += "| " + formatText("folder", 0, 21) + " | " + formatText("works", 0, 13) + " | " + formatText("chapters", 0, 13) + " | " + formatText("words", 0, 13) + " |\n"
				recapText += "+-----------------------+---------------+---------------+---------------+\n"
			for i in range(len(data["folderNames"])):
				if (marks[i] == 1 and categoryWorkCounts[i] > 0):
					recapText += "| " + formatText(data["folderNames"][i], 0, 21) + " | " + formatText(f'{categoryWorkCounts[i]:,}', 2, 13) + " | " + formatText(f'{categoryChapterCounts[i]:,}', 2, 13) + " | " + formatText(f'{categoryWordCounts[i]:,}', 2, 13) + " |\n"
			recapText += "+-----------------------+---------------+---------------+---------------+\n"
			recapText += "| " + formatText("total in read", 0, 21) + " | " + formatText(f'{readTotalCounts["works"]:,}', 2, 13) + " | " + formatText(f'{readTotalCounts["chapters"]:,}', 2, 13) + " | " + formatText(f'{readTotalCounts["words"]:,}', 2, 13) + " |\n"

		recapText += "+=======================================================================+\n"

	for currentData in countableData:
		if (settings[currentData] > 0):
			recapText += "| " + formatText(currentData, 1, 69) + " |\n"
			recapText += "+-------+---------------------------------------+-------+-------+-------+\n"
			recapText += "| " + formatText("rank", 0, 5) + " | " + formatText(currentData.replace("ies", "y").rstrip("s"), 0, 37) + " | " + formatText("bklg", 0, 5) + " | " + formatText("read", 0, 5) + " | " + formatText("total", 0, 5) + " |\n"
			recapText += "+-------+---------------------------------------+-------+-------+-------+\n"
			for i in range(settings[currentData]):
				if (i < len(rankedData[currentData])):
					recapText += "| " + formatText(str(i + 1), 1, 5) + "\t| "
					if (currentData == "relationships"):
						if ("/" in rankedData[currentData][i][0]):
							currentCharacters = rankedData[currentData][i][0].split("/")
							relationshipType = " / "
						elif ("&" in rankedData[currentData][i][0]):
							currentCharacters = rankedData[currentData][i][0].split("&")
							relationshipType = " & "
						for j in range(len(currentCharacters)):
							if ("\"" in currentCharacters[j]):
								currentCharacters[j] = currentCharacters[j].split()[1][1:-1]
							elif (currentCharacters[j].lower() == "elizabeth caledonia ashe"):
								currentCharacters[j] = "Ashe"
							elif (currentCharacters[j].lower() == "jean-baptiste augustin"):
								currentCharacters[j] = "Baptiste"
							elif (currentCharacters[j].lower() == "cole cassidy" or currentCharacters[j].lower() == "jesse mccree"):
								currentCharacters[j] = "Cassidy"
							elif (currentCharacters[j].lower() == "doomfist: the successor | akande ogundimu"):
								currentCharacters[j] = "Doomfist"
							elif (currentCharacters[j].lower() == "junker queen | odessa \"dez\" stone"):
								currentCharacters[j] = "Junker Queen"
							elif (currentCharacters[j].lower() == "mei-ling zhou"):
								currentCharacters[j] = "Mei"
							elif (currentCharacters[j].lower() == "soldier: 76 | jack morrison"):
								currentCharacters[j] = "Soldier: 76"
							elif (currentCharacters[j].lower() == "wrecking ball (overwatch)"):
								currentCharacters[j] = "Wrecking Ball"
							elif (currentCharacters[j].lower() == "tekhartha zenyatta"):
								currentCharacters[j] = "Zenyatta"
							elif (currentCharacters[j].lower() == "tekhartha mondatta"):
								currentCharacters[j] = "Mondatta"
							else:
								currentCharacters[j] = currentCharacters[j].split()[0]
						recapText += formatText(currentCharacters[0] + relationshipType + currentCharacters[1], 0, 37) + " | "
					else:
						recapText += formatText(rankedData[currentData][i][0], 0, 37) + " | "
					recapText += formatText(backlogData[currentData][rankedData[currentData][i][0]], 2, 5) + " | "
					recapText += formatText(readData[currentData][rankedData[currentData][i][0]], 2, 5) + " | "
					recapText += formatText(rankedData[currentData][i][1], 2, 5) + " |\n"
				else:
					recapText += "|       |                                       |       |       |       |\n"
			recapText += "+=======================================================================+\n"

	recapCopied = False
	viewingRecap = True

	while (viewingRecap):
		clearScreen()
		print(recapText)
		print("Q. Copy to Clipboard (Copied!)") if recapCopied else print("Q. Copy to Clipboard")
		print("ENTER. Continue")

		try:
			userInput = input("> ")
			if (userInput.lower() == "q"):
				pyperclip.copy(recapText)
				recapCopied = True
			else:
				viewingRecap = False
		except:
			continue

startApp()