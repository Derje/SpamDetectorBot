# python 3
import imaplib
import email
import sys
import getpass
import re
import string
from bs4 import BeautifulSoup

pattern_uid = re.compile('\d+ \(UID (?P<uid>\d+)\)')

punctation_translator = str.maketrans(string.punctuation.replace("'",""), ' '*(len(string.punctuation)-1))

#************************************************************************************************
# email_data:
#    class for storing the information (featchers) of a particular email.
#    this class also handles proforming varius test on the email data to extract featchers. 
#            
#    __init__(self, mid, dest, send, subj, text, html, parts) :  creates an email objects onaly keep whats relivant
#    ../
#                          
#
#
class email_data:
    def __init__(self, mid, dest, send, subj, text, html, parts):
        self.mid = mid
        self.dest = dest
        self.send = send
        self.subj = self.parse_email(subj)
        self.text = self.parse_email(text)
        self.filter_html(html)
        self.parts = parts
        

    def getid(self):
        return self.mid

    def get_text(self):
        return self.text

    def get_sub(self):
        return self.subj

    def filter_html(self, html):
    	soup = BeautifulSoup(html, features="html.parser")
    	self.links = []
    	for link in soup.findAll('a', attrs={'href': re.compile("^http(s)://")}, href=True):
    		self.links.append(link.get('href'))
    	self.img_count = len(soup.findAll('img'))
    	# remove the duplicets
    	self.links = set(self.links)
    	
    	#https://stackoverflow.com/questions/39582787/unable-to-find-all-links-with-beautifulsoup-to-extract-links-from-a-website-lin
    	#https://pythonspot.com/extract-links-from-webpage-beautifulsoup/
    	#https://www.pythonforbeginners.com/beautifulsoup/beautifulsoup-4-python
    	#https://www.digitalocean.com/community/tutorials/how-to-work-with-web-data-using-requests-and-beautiful-soup-with-python-3
    	#https://www.digitalocean.com/community/tutorials/how-to-scrape-web-pages-with-beautiful-soup-and-python-3 
    	#https://www.crummy.com/software/BeautifulSoup/bs3/documentation.html

    def parse_email(self, text):
    	# remove any special charicteres from the string
    	line = ""
    	for c in text:
    		if ord(c)>31 and ord(c)<126:
    			line += c
    		else :
    			line += " "
    	#line = ''.join(c for c in text if ord(c)>31 and ord(c)<126)
    	line = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' ',line,flags=re.MULTILINE)
    	
    	return re.sub(' +', ' ',line.translate(punctation_translator))
    	#return re.sub(r'https?:\/\/.*[\r\n]*', '', line, flags=re.MULTILINE)
    	#https://stackoverflow.com/questions/20183669/remove-formatting-from-strings
    	#https://stackoverflow.com/questions/9347419/python-strip-with-n

    def to_string(self):
    	return "Email:"+str(self.mid,'utf-8')+"\nSubject: "+self.subj+\
    	"\nfrom: "+self.send+" To: "+self.dest+"\n#images:"+str(self.get_imgs_n())+" #links:"+str(self.get_link_n())+\
    	" parts:"+(" Text" if self.parts[0] == 1 else "")+(" HTML" if self.parts[1] == 1 else "")+"\n"+\
    	self.get_text()
    
    def short_string(self):
    	return "Email:"+str(self.mid,'utf-8')+"\nSubject: "+self.subj+\
    	"\nfrom: "+self.send+" To: "+self.dest+"\n#images:"+str(self.get_imgs_n())+" #links:"+str(self.get_link_n())+\
    	" parts:"+(" Text" if self.parts[0] == 1 else "")+(" HTML" if self.parts[1] == 1 else "")+"\n"
    
    def get_imgs_n(self):
    	return self.img_count
    	
    def get_link_n(self):
    	return len(self.links)
    	
    def multi_lingle(self):
    	return (1 if 'utf 8' in self.subj else 0)
    	# https://ncona.com/2011/06/using-utf-8-characters-on-an-e-mail-subject/ 
    
    def get_sender(self):
   		return self.send

    	
# ********************************************************************************************

# ********************************************************************************************
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
        self.mailbox.login(e_address, e_pass)
        self.mailbox.select('inbox', readonly=False)

    def get_emails(self, ammount=-1):
        retcode, data = self.mailbox.search(None, 'ALL')
        if retcode != "OK":
            print("Error: unable get emails -> ", retcode)
            return None
        msgids = data[0].split()

        # Sets The ammount of emails to read in. it cantake a long time to read in 
        # the emails so this allows us to specify the number to read in. 
        # TODO change this to read in <ammont> emails from the last email recived. 
        msgids = msgids[:ammount]
        print(len(msgids))

        found = []

        for mid in msgids:
            typ, data = self.mailbox.fetch(mid, '(RFC822)')
            if typ != "OK":
                print("Error: unable to read data for id ", mid, " -> ", typ)
            for response_part in data:
                if isinstance(response_part, tuple):

                    # read in the email
                    msg = email.message_from_bytes(response_part[1])

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

                    found.append(email_data(mid, email_To, email_from, email_subject, email_text, email_html, email_parts))

                   
                    # https://stackoverflow.com/questions/3527933/move-an-email-in-gmail-with-python-and-imaplib
                    # https://docs.python.org/3/library/email.message.html
                    # https://rails-bestpractices.com/posts/2010/08/05/use-multipart-alternative-as-content_type-of-email/
                    # https://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/

        return found

    # https://stackoverflow.com/questions/3527933/move-an-email-in-gmail-with-python-and-imaplib
    def move_to_spam(self, email):
        # get the UID for the email.
        err, data = self.mailbox.fetch(email.getid(), "(UID)")
        if err != 'OK':
            print("Error: unable to fine email, not moved")
            return 0
        print(str(data[0], 'utf-8'))
        uid = pattern_uid.match(str(data[0], 'utf-8')).group('uid')

        err, _ = self.mailbox.uid('MOVE', uid, '[Gmail]/Spam')
        if err != 'OK':
            print("Error: failed to move email to spam")
            return 0

		# https://developers.google.com/gmail/imap/imap-extensions?csw=1#x-gm-labels

        return 1  # sucess

    def logout(self):
        self.mailbox.close()
        self.mailbox.logout()

# *********************************************************************************************

# *********************************************************************************************
# spam_filter 
#        is_subscribed(): checks if the emails is in a given list of subscribed senders who are
#                         advertising but you whant to be included. 
#
class spam_filter:

	def __init__(self):
		pass
	
	def is_subscribed(self, email):
		#TODO check if get_sender() is located in the list. 
		pass
	
	
	
#
#**********************************************************************************************


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error: expects python3 SpamBot.py <email>\n")
        sys.exit()
    emailAddr = "mllcassey@gmail.com"  # sys.argv[1]
    myMailBox = Inbox_Handler()
    myMailBox.login(emailAddr)

    # TODO insert Functionality in here
    my_emails = myMailBox.get_emails(5)
    for e in my_emails:
    	print("\n",e.short_string()," \n")
    # how to move an email to spam myMailBox.move_to_spam(my_emails[1])
    
    myMailBox.logout()
    
