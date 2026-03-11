import random 
import json
import pickle
import numpy as np
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import tensorflow as tf

import nltk
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()

intents = json.loads(open('instents.json').read())

words = []
classes = []
documents = []
ignoreletters = ['?','!','.',',']

