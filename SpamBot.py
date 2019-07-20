# python 3
import sys
from SpamDetector import Spam_Detector


if __name__ == "__main__":
	n_args = len(sys.argv)
	if n_args < 3 or n_args > 4:
		print("Error: expects python3 SpamBot.py <email> [\"run\",\"test\",\"train\"] (<ammount to read>)\n")
		sys.exit()
	
	emailAddr = sys.argv[1]
	print(emailAddr)
	bot = Spam_Detector()
	option = sys.argv[2]
	if n_args == 4:
		try :
			ammount = int(sys.argv[3])
			if ammount <= 0 :
				print("Error: invalid ammount, must be a intiger number > 0")
			elif option == "run":
				bot.run_detector(emailAddr, ammount)
			elif option == "train":
				bot.run_traning(emailAddr, ammount)
			elif option == "test":
				bot.run_test(emailAddr, ammount)
			else :
				print("Error: invalid option \n expects python3 SpamBot.py <email> [\"run\",\"test\",\"train\"] (<ammount to read>)\n")
		except :
			print("Error: invalid ammount, must be a intiger number > 0")
	else :
		if option == "run":
			bot.run_detector(emailAddr)
		elif option == "train":
			bot.run_traning(emailAddr)
		elif option == "test":
			bot.run_test(emailAddr)
		else :
			print("Error: invalid option \n expects python3 SpamBot.py <email> [\"run\",\"test\",\"train\"]\n")

