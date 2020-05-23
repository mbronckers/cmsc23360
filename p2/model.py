#!/usr/bin/env/python
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from joblib import dump, load

from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
from sklearn.linear_model import LogisticRegression

# Community data import (make sure to have path with access to parsed community data)
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

lr = LogisticRegression(random_state=0, max_iter=10e5)
lr.fit(X, y)

# Evaluate
rf_acc = clf.score(X_test, y_test)
svm_acc = svm_model.score(X_test, y_test)
lr_acc = lr.score(X_test, y_test)

print("Logistic Reg acc: " + str(lr_acc))
print("RF acc: " + str(rf_acc))
print("SVM acc: " + str(svm_acc))

# Save models
dump(clf, 'rf_model.joblib')
dump(svm_model, 'svm_model.joblib')

# Load models
# svm_model = load('svm_model.joblib')