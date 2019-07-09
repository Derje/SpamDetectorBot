# python 3
import imaplib
import email
import sys
import getpass

# class to madle the manipulation of the email account.


class MailBox:
	def __init__(self):
		self.mailbox = imaplib.IMAP4_SSL("imap.gmail.com", 993)

	def login(self, eAddr, ePass):
		self.mailbox.login(eAddr, ePass)
		self.mailbox.select('inbox')

	def getEmails(self):
		# get the current emails in the inbox.
		retcode, data = self.mailbox.search(None, 'ALL')
		if retcode != "OK":
			return (1, None)
		msgids = data[0].split()
		for mid in msgids:
			typ, data = self.mailbox.fetch(mid, '(RFC822)')
			if typ != "OK":
				print("not ok");
			for response_part in data:
				print(response_part)
	
	def moveEmails(self, loc):
		# function for moving the emails arround.
		pass
		
	def logout(self):
		self.mailbox.close()
		self.mailbox.logout()


# ********************************************************************************************
# Inbox_Handler:
#      Class for manipulating and connecting to a Gmail inbox. 
#      this is the section of the spam box that interfaces with the outside of the system. 
# 
#      __init__() ->   : initializes a gamail imbox. 
#
#     login(e_address) ->  : login this hanndler into specified email account. 
#
#     get_emails() -> [email] : retrive the emails currently in inbox. 
#
#     move_to_spam(email) ->  : move a specified email to the spam follder 
#
#     logout() ->  : disconects the handler from the email. 
# 
class Inbox_Handler:
	def __init__(self):
		self.mailbox = imaplib.IMAP4_SSL("imap.gmail.com",993)

	def login(self, e_address):
		e_pass = getpass.getpass()
		self.mailbox.login(e_address,e_pass)
		self.mailbox.select('inbox')
		
	def get_emails(self):
		retcode, data = self.mailbox.search(None, 'ALL')
		if retcode != "OK":
			print("Error: unable get emails -> ", retcode)
			return None
		msgids = data[0].split()
		
		# TODO 
		# remove the following line. Debugin line added for testing purposes. 
		msgids = msgids[0:1]
		
		
		emails = [] 
		
		for mid in msgids:
			typ, data = self.mailbox.fetch(mid, '(RFC822)' )
			if typ != "OK":
				print("Error: unable to read data for id ", mid," -> ",typ);
			for response_part in data:
				if isinstance(response_part, tuple):
				
					# read in the email 
					msg = email.message_from_bytes(response_part[1])
					
					#Extract the Data  and add store it.
					email_To = msg['To']
					email_subject = msg['subject']
					email_from = msg['from']
					email_body  = " "
					count = 0
					for part in msg.walk():
						count += 1
						if part.get_content_type() == "text/plain":
							body = part.get_payload(decode=True)
							print(body)
							email_body += body 
					email = ["ID":mid, "To":email_To, "sub":email_subject, "from":email_from, "body":email_body]
					emails.append(email)
					
					
					#keys = msg. keys()
					#for key in keys:
						#print("\n\n\n ", key, " : ", msg[key], "\n")
					#for part in msg.walk():
					#	print("the next part :", part)
					#email_To = msg['To']
					#email_subject = msg['subject']
					#email_from = msg['from']
					#print('From : ' + email_from + '\n')
					#print('Subject : ' + email_subject + '\n')
					#print('msg to : ', email_To, '\n')
					
					# https://stackoverflow.com/questions/3527933/move-an-email-in-gmail-with-python-and-imaplib
					# https://docs.python.org/3/library/email.message.html
					
					#print("the content : ", msg.get_body())
		
	
	# https://stackoverflow.com/questions/3527933/move-an-email-in-gmail-with-python-and-imaplib 
	def move_to_spam(self, email):
		# get the UID for the email. 
		err, data = imap.fetch(email["ID"], "(UID)")
		if err != 'OK' :
			print("Error: unable to fine email, not moved")
			return 0
		uid = pattern_uid.match(data).group('uid')
		
		err, _ = imap.uid('MOVE', uid, '(\Spam)')
		if err != 'OK':
			print("Error: failed to move email to spam")
			return 0
		
		
		# alternate approach
		
		# Copy the email to the spam follder. 
		#err, _ = imap.uid('COPY', uid, '(\Spam)')
		#if err != 'OK':
		#	print("Error: failed to move email to spam")
		#	return 0
		
		# remove the email from the gmail. 
		#err, _ = imap.uid('STORE', msg_uid , '+FLAGS', '(\Deleted)')
		#if err != 'OK' :
		#	print("Error: failed to deleet from imbox")
		#	return 0
        #imap.expunge()	
        
        
		return 1 #sucess 
		
		
	def logout(self):
		self.mailbox.close()
		self.mailbox.logout()

# *********************************************************************************************



if __name__ == "__main__":
	if len(sys.argv) != 2 :
		print("Error: expects python3 SpamBot.py <email>\n")
		sys.exit()
	emailAddr = "mllcassey@gmail.com"   #sys.argv[1]
	myMailBox = Inbox_Handler()
	myMailBox.login(emailAddr)

	# TODO insert Functionality in here 
	myMailBox.get_emails()
	
	myMailBox.logout()
	# print("Spam Filtering Commpleet !!!")








