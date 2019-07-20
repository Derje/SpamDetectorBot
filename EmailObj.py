# Python3 
import re
import string
from bs4 import BeautifulSoup

punctation_translator = str.maketrans(string.punctuation.replace("'", "").replace("$", ""), ' '*(len(string.punctuation)-2))

#************************************************************************************************
# email_data:
#    class for storing the information (featchers) of a particular email.
#    this class also handles proforming varius test on the email data to extract featchers.
#
#    __init__(self, mid, dest, send, subj, text, html, parts) :  creates an email objects onaly keep whats relivant
#    ../
#  TODO finish this 
#
#
class email_data:
	def __init__(self, uid, dest, send, subj, text, html, parts):
		self.uid = uid
		self.dest = str(dest)
		self.send = str(send)
		self.subj = self.parse_email(str(subj))
		self.text = self.parse_email(text)
		self.filter_html(html)
		self.parts = parts
	
	def getid(self):
		return self.uid
	
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
		
		# https://stackoverflow.com/questions/39582787/unable-to-find-all-links-with-beautifulsoup-to-extract-links-from-a-website-lin
		# https://pythonspot.com/extract-links-from-webpage-beautifulsoup/
		# https://www.pythonforbeginners.com/beautifulsoup/beautifulsoup-4-python
		# https://www.digitalocean.com/community/tutorials/how-to-work-with-web-data-using-requests-and-beautiful-soup-with-python-3
		# https://www.digitalocean.com/community/tutorials/how-to-scrape-web-pages-with-beautiful-soup-and-python-3
		# https://www.crummy.com/software/BeautifulSoup/bs3/documentation.html
	
	def parse_email(self, text):
		# remove any special charicteres from the string
		line = ""
		for c in text:
			if ord(c) > 31 and ord(c) < 126:
				line += c
			else:
				line += " "
		line = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' ', line, flags=re.MULTILINE)
		return re.sub(' +', ' ', line.translate(punctation_translator))
		# return re.sub(r'https?:\/\/.*[\r\n]*', '', line, flags=re.MULTILINE)
		# https://stackoverflow.com/questions/20183669/remove-formatting-from-strings
		# https://stackoverflow.com/questions/9347419/python-strip-with-n
		# https://stackoverflow.com/questions/34860982/replace-the-punctuation-with-whitespace
		# https://www.w3resource.com/python-exercises/re/python-re-exercise-42.php
		# https://stackoverflow.com/questions/1546226/simple-way-to-remove-multiple-spaces-in-a-string
		# https://docs.python.org/3/library/re.html#re.match
	
	def to_string(self):
		return "Email:"+str(self.uid)+"\nSubject: "+self.subj +\
		"\nfrom: "+self.send+" To: "+self.dest+"\n#images:"+str(self.get_imgs_n())+" #links:"+str(self.get_link_n()) +\
		" parts:"+(" Text" if self.parts[0] == 1 else "")+(" HTML" if self.parts[1] == 1 else "")+"\n" +\
		self.get_text()
		
	def short_string(self):
		return "Email:"+str(self.uid)+"\nSubject: "+ self.subj +\
		"\nfrom: "+self.send+" To: "+self.dest+"\n#images:"+ str(self.get_imgs_n()) +" #links:"+ str(self.get_link_n()) +\
		" parts:"+(" Text" if self.parts[0] == 1 else "") +(" HTML" if self.parts[1] == 1 else "")+"\n"
	
	def get_imgs_n(self):
		return self.img_count
	
	def get_link_n(self):
		return len(self.links)
	
	def multi_lingle(self):
		return (1 if 'utf 8' in self.subj else 0)
		# https://ncona.com/2011/06/using-utf-8-characters-on-an-e-mail-subject/
	
	def get_sender(self):
		return self.send
	
	def get_comps(self):
		# Get the Components of the email as a discreet state space. 
		# 0 -> ! html or text 
		# 1 -> text
		# 2 -> html
		# 3 -> text & html
		return self.parts[0] + 2 * self.parts[1]

# ********************************************************************************************

