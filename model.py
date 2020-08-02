# Importing the libraries
import matplotlib.pyplot as plt
#import pickle

import pandas as pd
import numpy as np
import random

#from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


url_dataset = pd.read_csv("urldata.csv",',',error_bad_lines=False)
url_dataframe = pd.DataFrame(url_dataset)
url_array = np.array(url_dataframe)

random.shuffle(url_array)


def getTokens(url):
	
  tokensBySlash = str(url.encode('utf-8')).split('/')	
  allTokens = []
	
  for i in tokensBySlash:
    tokens = str(i).split('-')	
    tokensByDot = []
		
    for j in range(0,len(tokens)):
      tempTokens = str(tokens[j]).split('.')
      tokensByDot = tokensByDot + tempTokens
		
    allTokens = allTokens + tokens + tokensByDot
	
  allTokens = list(set(allTokens))


  if 'com' in allTokens:
    allTokens.remove('com')

  return allTokens


y = [data[1] for data in url_array]
url_list = [data[0] for data in url_array]

vectorizer = TfidfVectorizer(tokenizer = getTokens)
X = vectorizer.fit_transform(url_list)

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2, random_state=42)

logit = LogisticRegression(solver='sag')	
logit.fit(X_train, y_train)

#print("Accuracy ",logit.score(X_test, y_test))

# Saving model to disk
pickle.dump(logit, open('model.pkl','wb'))

# Loading model to compare the results
#model = pickle.load(open('model.pkl','rb'))

