import os
import numpy as np
import pandas as pd
from pandas.plotting import scatter_matrix
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from sklearn import model_selection
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score

metadata_filename = "asdfasdf.csv"

# Load the data
metadata_df = pd.read_csv("path/to/data"+metadata_filename)
#print(metadata_df.head(10))

# Plot the scatter plot
#scatter_matrix(metadata_df,diagonal="kde")
#plt.savefig("scatter_matrix.png", bbox_inches='tight')
#plt.show()

# Select useful columns
X = metadata_df[["peakFreq","snr","centralFreq","duration", "bandwidth"]]
Y = metadata_df['label'].astype('category')

# Split training and test sets
validation_size = 0.20
X_train, X_test, Y_train, Y_test = model_selection.train_test_split(X, Y, test_size=validation_size, stratify = Y)
#print(X_train.head())

# TRY SOME MODELS

#--- kNN ---#

vecinos_array = range(2,15,4)

for n_neighbors in vecinos_array:
    clf = KNeighborsClassifier(n_neighbors)
    clf.fit(X_train,Y_train)
    predictions = clf.predict(X_test)
    print("kNN", n_neighbors, accuracy_score(Y_train, clf.predict(X_train)), accuracy_score(Y_test, predictions))
    #print(confusion_matrix(Y_test, predictions))
    #print(classification_report(Y_test, predictions))

#--- SVM ---#

gamma_array = [1e-6,1e-5]
c_array = [1e3,1e4]

for gamma in gamma_array:
    for c in c_array:
        clf = svm.SVC(gamma=gamma, C=c)
        clf.fit(X_train,Y_train)
        predictions = clf.predict(X_test)
        print("SVM", gamma, c, accuracy_score(Y_train, clf.predict(X_train)), accuracy_score(Y_test, predictions))

#--- Decision Tree ---#

clf = DecisionTreeClassifier()
clf.fit(X_train,Y_train)
predictions = clf.predict(X_test)
print("Decision Tree", accuracy_score(Y_train, clf.predict(X_train)), accuracy_score(Y_test, predictions))


#--- Random Forest ---#

clf = RandomForestClassifier()
clf.fit(X_train,Y_train)
predictions = clf.predict(X_test)
print("Random Forest", accuracy_score(Y_train, clf.predict(X_train)), accuracy_score(Y_test, predictions))
