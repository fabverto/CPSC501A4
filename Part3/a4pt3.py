# -*- coding: utf-8 -*-
"""A4pt3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IwlPFaa7vvoLjeILXbIKIyC-rrUtUJwl
"""

# Commented out IPython magic to ensure Python compatibility.
try:
  # %tensorflow_version only exists in Colab.
#   %tensorflow_version 2.x
except Exception:
  pass

import functools
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
import tensorflow as tf

DATA_URL = "http://pages.cpsc.ucalgary.ca/~hudsonj/CPSC501F19/heart.csv"

data = pd.read_csv(DATA_URL)
print(data.head)

LABEL_COLUMN = data.chd
LABELS = data.drop('chd',axis=1)

x_train, x_test, y_train, y_test = train_test_split(LABEL_COLUMN, LABELS,test_size=0.2)
print("\nx_train:\n")
print(x_train.head())
print(x_train.shape)

print("\nx_test:\n")
print(x_test.head())
print(x_test.shape)