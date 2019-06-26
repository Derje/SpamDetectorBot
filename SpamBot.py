# python 3
import imaplib
import email
import sys
import getpass

class MailBox:
	def __init__(self):
		self.mailbox = imaplib.IMAP4_SSL("imap.gmail.com",993)

	def login(self, eAddr, ePass):
		self.mailbox.login(eAddr,ePass)
		folders = self.mailbox.list()
		for i in folders:
			print(i);

	def logout(self):
		self.mailbox.logout()





if __name__ == "__main__":
	if len(sys.argv) != 2 :
		print("Error: expects python3 SpamBot.py <email>\n")
		sys.exit()
	emailAddr = sys.argv[1]
	pasword = getpass.getpass()
	myMailBox = MailBox()
	myMailBox.login(emailAddr, pasword)

	#TODO insert Functionality in here 

	myMailBox.logout()
	#print("Spam Filtering Commpleet !!!")








