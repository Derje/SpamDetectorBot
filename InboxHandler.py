# Python3
import imaplib
import email
import sys
import getpass
import re
from EmailObj import email_data

pattern_uid = re.compile('\d+ \(UID (?P<uid>\d+)\)')

# *************************************************************************************************
# Inbox_Handler:
#      Class for manipulating and connecting to a Gmail inbox.
#      this is the section of the spam box that interfaces with the outside of the system.
#
#      __init__() ->   : initializes a gamail imbox.
#
#     login(e_address) ->  : login this hanndler into specified email account.
#
#     get_emails(ammount) -> [email] : retrive the emails currently in inbox.
#                                      if ammount is specified in will onaly read in that many
#                                      emails, else it will read in all the emails from the inbox.
#
#     move_to_spam(email) ->  : move a specified email to the spam follder
#
#     logout() ->  : disconects the handler from the email.
#


class Inbox_Handler:
	def __init__(self):
		self.mailbox = imaplib.IMAP4_SSL("imap.gmail.com", 993)
	
	def login(self, e_address):
		e_pass = getpass.getpass()
		self.e_address = e_address
		self.mailbox.login(e_address, e_pass)
		self.mailbox.select('inbox', readonly=False)
	
	def read_emails_for_traning(self, ammount = -1):
		traning_data = []
		traning_lables = []
		
		# read in the Ham emails from inbox
		self.mailbox.select('inbox', readonly=True)
		hams = self.get_emails(ammount)
		for email in hams:
			traning_data.append(email)
			traning_lables.append(0)
		self.mailbox.close()
		
		# read in the Spam emails from spam folder
		self.mailbox.select('[Gmail]/Spam', readonly=True)
		spams = self.get_emails(ammount)
		for email in spams:
			traning_data.append(email)
			traning_lables.append(1)
		
		return traning_data, traning_lables
		
		
	
	def get_emails(self, ammount=0):
		retcode, data = self.mailbox.search(None, 'ALL')
		if retcode != "OK":
			print("Error: unable get emails -> ", retcode)
			return None
		msgids = data[0].split()
		# Sets The ammount of emails to read in. it cantake a long time to read in
		# the emails so this allows us to specify the number to read in.
		# TODO change this to read in <ammont> emails from the last email recived
		msgids = msgids[-(ammount):]
		print(len(msgids))
		
		found = []
		
		for mid in msgids:
			# get uid
			err, data = self.mailbox.fetch(mid, "(UID)")
			if err != 'OK':
				print("Error: unable to fine email, not moved")
				return 0
			uid = pattern_uid.match(str(data[0], 'utf-8')).group('uid')
			typ, data = self.mailbox.fetch(mid, '(RFC822)')
			if typ != "OK":
				print("Error: unable to read data for id ", mid, " -> ", typ)
			for response_part in data:
				if isinstance(response_part, tuple):
					# read in the email
					msg = email.message_from_bytes(response_part[1])
					found.append(self.extract_email_data(uid, msg))
					# https://stackoverflow.com/questions/3527933/move-an-email-in-gmail-with-python-and-imaplib
					# https://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/
		return found
	
	def extract_email_data(self, uid, msg):
		# Extract the Data  and add store it.
		email_To = msg['To']
		email_subject = msg['subject']
		email_from = msg['from']
		email_text = ""
		email_html = ""
		email_parts = [0, 0]
		for part in msg.walk():
			if part.get_content_type() == "text/plain":
				email_parts[0] += 1
				text = part.get_payload(decode=True)
				try:
					email_text += text.decode("utf-8")
				except:
					pass
			elif part.get_content_type() == "text/html":
				email_parts[1] += 1
				html = part.get_payload(decode=True)
				try:
					email_html += html.decode("utf-8")
				except:
					pass
		return email_data(uid, email_To, email_from, email_subject, email_text, email_html, email_parts)
		# https://docs.python.org/3/library/email.message.html
		# https://rails-bestpractices.com/posts/2010/08/05/use-multipart-alternative-as-content_type-of-email/
		
	# https://stackoverflow.com/questions/3527933/move-an-email-in-gmail-with-python-and-imaplib
	def move_to_spam(self, email):
		err, _ = self.mailbox.uid('MOVE', email.getid(), '[Gmail]/Spam')
		if err != 'OK':
			print("Error: failed to move email to spam")
			return 0
		# https://developers.google.com/gmail/imap/imap-extensions?csw=1#x-gm-labels
		return 1  # sucess
	
	def logout(self):
		self.mailbox.close()
		self.mailbox.logout()

# *****************************************************************************************************

# ************************ TESTING CODE ***************************************************************
if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Error: expects python3 InboxHandler.py <email>\n")
		sys.exit()
	emailAddr = "mllcassey@gmail.com"  # sys.argv[1]
	
	print("Statring Testing\nUseing Email Address: %s" % emailAddr)
	myMailBox = Inbox_Handler()
	
	myMailBox.login(emailAddr)
	testnumb = 5
	print("Attempting to read in %d emails"%testnumb)
	my_emails = myMailBox.get_emails(testnumb)
	if len(my_emails) != testnumb :
		print("Test Failed")
	else :
		for e in my_emails:
			print("\n",e.short_string()," \n")
		print("Test Passed")
	
	
	print("Attempting To read in %d spam and %d ham emails" % (testnumb,testnumb))
	testdata, testlables = myMailBox.read_emails_for_traning(testnumb)
	if len(testdata) != 2 * testnumb:
		print("Test Failed")
	else:
		for i in range(len(testdata)):
			print("\n",testlables[i])
			print(testdata[i].short_string()," \n")
		print("Test Passed")
	
	
	myMailBox.logout()
	print("Tesing Compleet")


