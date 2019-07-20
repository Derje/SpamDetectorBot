# Python3
import sys
import glob
import numpy as np
import pickle
import email
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.tree import DecisionTreeClassifier
from EmailObj import email_data
from InboxHandler import Inbox_Handler
from TextClassifier import Text_Classifier

# *********************************************************************************************
# Spam_Detector 
#         TODO description :) 
#
class Spam_Detector:

	def __init__(self):
		self.imbox = Inbox_Handler()
		self.text_classi = Text_Classifier()
		
		try:
			self.decision_tree = pickle.load(open("decis_tree.p", "rb"))
		except:
			self.decision_tree = DecisionTreeClassifier(random_state=2, max_depth=6)
			train_data, train_lables = self.load_data();
			self.train_detector(train_data, train_lables)
		
	
	# Takes in a list of email objects and returnes a featcher list of the emails for use by the decision tree
	# feature array: 
	# <clasification score, #img, #links, components, utf8 in subj, length of email text> 
	def test_emails(self, emails):
		features = []
		clf = self.classify_emails_text(emails)
		for numb in range(len(emails)):
			e = emails[numb]
			feat = [clf[numb][1], e.get_imgs_n(), e.get_link_n(), e.get_comps(), e.multi_lingle(), len(e.get_text())]
			features.append(feat)
		return np.array(features)
	
	def train_detector(self, traning_emails, traning_lables):
		# train the Text Classifiyer 
		traning_messages = [(email.get_sub() + email.get_text()) for email in traning_emails]
		self.text_classi.train_classifier(traning_messages, traning_lables)
		
		# train the decission tree
		traning_data = self.test_emails(traning_emails)
		self.decision_tree.fit(traning_data, traning_lables)
		pickle.dump(self.decision_tree, open("decis_tree.p", "wb"))
		
	
	def test_detector(self):
		emails, lables = self.load_data()
		test_data = self.test_emails(emails)
		pred = self.decision_tree.predict(test_data)
		
		print("Report : \n", classification_report(lables, pred))
		print("Confusion_matrix : \n", confusion_matrix(lables, pred))
		
	def load_data(self):
		data = []
		lables = []
		paths = ["../SampleEmails/ham/*.eml", "../SampleEmails/spam/*.eml"]
		for t in range(2):
			files = glob.glob(paths[t])
			for name in files:
				with open(name, "rb") as f:
					msg = email.message_from_bytes(f.read())
					e = self.imbox.extract_email_data(-1, msg)
					data.append(e)
					lables.append(t)
		return data, np.array(lables)

	def classify_emails_text(self, emails):
		messages = [(email.get_sub() + email.get_text()) for email in emails]
		return self.text_classi.classify(messages)
	
	def run_detector(self, e_addr, ammount = 0):
		# login to the client and read in the emails. 
		self.imbox.login(e_addr)
		emails = self.imbox.get_emails(ammount)
		if len(emails) < 1 :
			print("Error: No emails To Read")
			self.imbox.logout()
			return 1
		
		# run the classification
		email_feat = self.test_emails(emails)
		preds = self.decision_tree.predict(email_feat)
		
		# move the relivant emails. 
		for n in range(len(emails)):
			if preds[n] == 1:
				self.imbox.move_to_spam(emails[n])
		self.imbox.logout()
		return 0
	
	def run_traning(self, e_addr, ammount = 0):
		# login to the client and get emails. 
		self.imbox.login(e_addr)
		traindata, trainlables = self.imbox.read_emails_for_traning(ammount)
		if len(traindata) < 1 :
			print("Error: No emails To Read")
			self.imbox.logout()
			return 1
		
		# train the detector
		self.train_detector(traindata, trainlables)
		self.imbox.logout()
	
	def run_test(self, e_addr, ammount = 0):
		self.imbox.login(e_addr)
		print("testing with account %s\n" % e_addr)
		testdata, testlables = self.imbox.read_emails_for_traning(ammount)
		if len(testdata) < 1 :
			print("Error: No emails To Read")
			self.imbox.logout()
			return 1
		
		# run the classification
		email_feat = self.test_emails(testdata)
		preds = self.decision_tree.predict(email_feat)
		
		print("Report : \n", classification_report(testlables, preds))
		print("Confusion_matrix : \n", confusion_matrix(testlables, preds))
	
	def is_subscribed(self, email):
		# TODO check if sender is on a list of exceptions, advertising but not spam!!! 
		pass
	
	
	
#
#**********************************************************************************************

# ************************ TESTING CODE ***************************************************************
if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Error: expects python3 InboxHandler.py <email>\n")
		sys.exit()
	emailAddr = "mllcassey@gmail.com"  # sys.argv[1]
	
	print("testing spam detector no conection");
	bot = Spam_Detector()
	bot.test_detector()
	
	#print("testing spam detector conected to %s without self traning" % emailAddr)
	#bot.run_test(emailAddr)
	
	
	#print("testing spam detector conected to %s with self traning" % emailAddr)
	#bot = Spam_Detector()
	#bot.run_traning(emailAddr)
	
	#bot = Spam_Detector()
	#bot.run_test(emailAddr)
	
	#TODO add in test here to test the functionality of the decition tree make it train on the items of data in the inbox and then test on another sample of it. 


