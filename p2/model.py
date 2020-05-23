#!/usr/bin/env/python
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm

# Data import
path="../parsed/community/"
day_one="day_1"
day_two="day_2"
day_three="day_3"
file="_parsed.csv"
col_names = ["website-index", "time", "direction", "packet size"]

df_one = pd.read_csv(path+day_one+file, header=0, names=col_names, error_bad_lines=False, warn_bad_lines=False)
df_two = pd.read_csv(path+day_two+file, header=0, names=col_names, error_bad_lines=False, warn_bad_lines=False)
df_three = pd.read_csv(path+day_three+file, header=0, names=col_names, error_bad_lines=False, warn_bad_lines=False)

# Preprocess training data
df = df_one.append(df_two)
X = df.loc[:, df.columns != 'website-index']
y = df['website-index']

# Preprocess testing data
X_test = df_three.loc[:, df_three.columns != 'website-index']
y_test = df_three['website-index']

# Model training
clf = RandomForestClassifier()
clf.fit(X,y)

svm_model = svm.SVC()
svm_model.fit(X, y)

# Evaluate
rf_acc = clf.score(X_test, y_test)
svm_acc = svm_model.score(X_test, y_test)

print("RF acc: " + str(rf_acc))
print("SVM acc: " + str(svm_acc))