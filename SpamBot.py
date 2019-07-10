# python 3
import imaplib
import email
import sys
import getpass
import re

# class to madle the manipulation of the email account.
pattern_uid = re.compile('\d+ \(UID (?P<uid>\d+)\)')

class email_data:
	def __init__(self, mid, dest, send, subj, data):
		self.mid = mid
		self.dest = dest 
		self.send = send
		self.subj = subj
		self.data = self.parse_email(data)
	def getid(self):
		return self.mid
	def get_text(self):
		return self.data
	
	def parse_email(self, data):
		#TODO Implement this 
		return data; 


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
		self.mailbox.select('inbox', readonly = False)
		
	def get_emails(self, ammount = -1):
		retcode, data = self.mailbox.search(None, 'ALL')
		if retcode != "OK":
			print("Error: unable get emails -> ", retcode)
			return None
		msgids = data[0].split()
		
		# this bit was really added more so we could limit the ammount we read for testing, 
		# but can allos be used in practice so i am not complaining 
		# spectifiying ammount limits the ammount of emails it reads, defaults to all of them
		msgids = msgids[:ammount]
		print(len(msgids))
			
		found = [] 
		
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
							try :
								email_body += body.decode("utf-8")
							except :
								#print(body)
								pass
								
					found.append(email_data(mid,email_To,email_from,email_subject,email_body))
					
					
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
		return found
		
	
	# https://stackoverflow.com/questions/3527933/move-an-email-in-gmail-with-python-and-imaplib 
	def move_to_spam(self, email):
		# get the UID for the email. 
		err, data = self.mailbox.fetch(email.getid(), "(UID)")
		if err != 'OK' :
			print("Error: unable to fine email, not moved")
			return 0
		print(str(data[0], 'utf-8'))
		uid = pattern_uid.match(str(data[0], 'utf-8')).group('uid')
		
		err, _ = self.mailbox.uid('MOVE', uid, '[Gmail]/Spam')
		if err != 'OK':
			print("Error: failed to move email to spam")
			return 0
        
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
	my_emails = myMailBox.get_emails(5)
	for e in my_emails:
		print("\n\n start *********** \n",e.get_text())
	#myMailBox.move_to_spam(my_emails[1])
	
	print(" the number of emails : ",len(my_emails))
	
	myMailBox.logout()
	# print("Spam Filtering Commpleet !!!")








