# Python3
import glob
import numpy as np
import pickle
import re
from sklearn.naive_bayes import MultinomialNB
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix


# ***************************************************************************************************
# Text_Classifier
#       train_classifier(): trains the classifier on sample data.
#
#
class Text_Classifier:

	def __init__(self):

		try:
			self.Classifier_Pipeline = pickle.load(open("Text_Classi.p", "rb"))
		except:
			self.Classifier_Pipeline = Pipeline([('bow', CountVectorizer(
			    analyzer=self.perprocess_text)), ('tfidf', TfidfTransformer()), ('classifier', MultinomialNB())])
			traning_data, traning_lables = self.load_data("train")
			self.train_classifier(traning_data, traning_lables)

	def load_data(self, type):
		data = []
		lables = []
		paths = ["data/nonspam-"+type+"/*.txt", "data/spam-"+type+"/*.txt"]
		for t in range(2):
			files = glob.glob(paths[t])
			for name in files:
				try:
					with open(name, "r") as f:
						data.append(f.read())
						lables.append(t)
				except IOError as exc:
					raise
		return data, lables

	def perprocess_text(self, message):
		message = re.sub('\d', 'numb', message).replace("$", "dollar")
		message = message.lower().split()
		message = [
		    word for word in message if word not in stopwords.words('english')]
		stemmer = PorterStemmer()
		message = [stemmer.stem(word) for word in message]
		return np.array(message)

	def train_classifier(self, traning_data, traning_lables):
		traning_lables = np.array(traning_lables)
		self.Classifier_Pipeline.fit(traning_data, traning_lables)
		pickle.dump(self.Classifier_Pipeline, open("Text_Classi.p", "wb"))

	def test_classifier(self):
		test_data, test_lables = self.load_data("test")
		#test_data = test_data[:10]
		#test_lables = test_lables[:10]
		pred = self.Classifier_Pipeline.predict(test_data)
		test_lables = np.array(test_lables)
		print("Report : \n", classification_report(test_lables, pred))
		print("Confusion_matrix : \n", confusion_matrix(test_lables, pred))

	def classify(self, data):
		return self.Classifier_Pipeline.predict_proba(data)


#
#******************************************************************************************************

# ************************ TESTING CODE ***************************************************************
if __name__ == "__main__":
	text_classi = Text_Classifier()
	text_classi.test_classifier()


