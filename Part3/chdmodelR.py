# -*- coding: utf-8 -*-
"""CHDModel.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EQK6cxmsuIqunyx-upgvg3a_Qw4eAkrH
"""

# Commented out IPython magic to ensure Python compatibility.
try:
  # %tensorflow_version only exists in Colab.
#   %tensorflow_version 2.x
except Exception:
  pass

import functools
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
import tensorflow as tf
from tensorflow_core.python.keras import regularizers
from tensorflow.keras import layers
import pandas as pd

train_file = "heart_train.csv"
test_file = "heart_test.csv"

!head {train_file}

!head {test_file}

def show_batch(dataset):
  for batch, label in dataset.take(1):
    for key, value in batch.items():
      print("{:20s}: {}".format(key,value.numpy()))

class PackNumericFeatures(object):
  def __init__(self,names):
    self.names = names
  
  def __call__(self, features, labels):
    numeric_features = [features.pop(name) for name in self.names]
    numeric_features = [tf.cast(feat, tf.float32) for feat in numeric_features]
    numeric_features = tf.stack(numeric_features, axis=-1)
    features['numeric'] = numeric_features


    return features, labels

def get_dataset(file, **kwargs):
  dataset = tf.data.experimental.make_csv_dataset(
      file,
      batch_size = 50,
      label_name=LABEL_COLUMN,
      na_value ="?",
      num_epochs=1,
      ignore_errors=True,
      **kwargs)
  return dataset

LABEL_COLUMN = 'chd'
LABELS = [0, 1]

CATEGORIES = {'famhist': ['Present', 'Absent']}

SELECT_COLUMNS = ['sbp','tobacco','ldl','adiposity','famhist', 'typea','obesity','alcohol','age','chd']
raw_train_data = get_dataset(train_data, select_columns=SELECT_COLUMNS)
raw_test_data = get_dataset(test_data, select_columns=SELECT_COLUMNS)

train_batch, label_batch = next(iter(raw_train_data))
test_batch, label_batch = next(iter(raw_test_data))

NUMERIC_FEATURES = ['sbp','tobacco','ldl','adiposity', 'typea','obesity','alcohol','age']

packed_train_data = raw_train_data.map(
    PackNumericFeatures(NUMERIC_FEATURES))

packed_test_data = raw_test_data.map(
    PackNumericFeatures(NUMERIC_FEATURES))

train_batch, label_batch = next(iter(packed_train_data))
test_batch, label_batch = next(iter(packed_test_data))

desc = pd.read_csv(sys.argv[1])[NUMERIC_FEATURES].describe()

MEAN = np.array(desc.T['mean'])
STD = np.array(desc.T['std'])
def normalize_numeric_data(data, mean, std):
  return (data-mean)/std

normalizer = functools.partial(normalize_numeric_data, mean=MEAN, std=STD)

numeric_column = tf.feature_column.numeric_column('numeric', normalizer_fn=normalizer, shape=[len(NUMERIC_FEATURES)])
numeric_columns = [numeric_column]

train_batch['numeric']

numeric_layer = tf.keras.layers.DenseFeatures(numeric_columns)
numeric_layer(train_batch).numpy()

categorical_columns = []
for feature, vocab in CATEGORIES.items():
  cat_col = tf.feature_column.categorical_column_with_vocabulary_list(
        key=feature, vocabulary_list=vocab)
  categorical_columns.append(tf.feature_column.indicator_column(cat_col))

categorical_layer = tf.keras.layers.DenseFeatures(categorical_columns)
preprocessing_layer = tf.keras.layers.DenseFeatures(categorical_columns+numeric_columns)

model = tf.keras.Sequential([
  preprocessing_layer,
  layers.Dense(256, activation='relu',kernel_regularizer=regularizers.l2(0.005)),
  layers.Dropout(0.5),
   layers.Dense(128, activation='relu',kernel_regularizer=regularizers.l2(0.005)),
  layers.Dropout(0.5),
   layers.Dense(128, activation='selu',kernel_regularizer=regularizers.l2(0.005)),
  layers.Dropout(0.4),
  layers.Dense(1, activation='sigmoid')
])

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

train_data = packed_train_data.shuffle(500)
test_data = packed_test_data

print("--Train--")
model.fit(train_data, epochs=500)

test_loss, test_accuracy = model.evaluate(test_data)

print('\n\nTest Loss {}, Test Accuracy {}'.format(test_loss, test_accuracy * 100))

# Show some results
predictions = model.predict(test_data)
for prediction, CHD in zip(predictions[:50], list(test_data)[0][1][:50]):
  print("Predicted Coronary Heart Disease: {:.2%}".format(prediction[0]),
        " | Actual outcome: ",
        ("YES Coronary Heart Disease" if bool(CHD) else "NO Coronary Heart Disease"))