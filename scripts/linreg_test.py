# General imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from analysis_utils import *

def get(x,y):
    X = []
    for i,t in enumerate(x):
        X.append([t])
    X = np.array(X)
    X = np.hstack((X, X*X))
    # print(X)
    regressor = LinearRegression().fit(X, y)
    return r2_score(regressor.predict(X), y)

# Generating data
X = np.random.randn(10,1)
c = np.random.uniform(-10,10,(10,))
# adding another non-linear column
X = np.hstack((X, X*X))
Y = (4*X[:,1] + c)
# plt.scatter(X[:, 0], Y)
# plt.show()
# plt.scatter(X[:, 1], Y)
# plt.show()
# Applying linear reg

# print(X,Y)
regressor = LinearRegression().fit(X, Y)
# Checking the accuracy
print(r2_score(regressor.predict(X), Y))
print(getLinRegScore(X[:,0],Y))
print(get(X[:,0],Y))


