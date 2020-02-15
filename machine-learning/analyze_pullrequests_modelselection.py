# %%
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

os.getcwd()

# %%
data = '' # CONFIGURE DATA FILE as a dataframe
df = pd.read_csv(data)


# %%
# Categorical features
# Put category name : number of values
categorical_features = [
    'cat1', # cat 3
    'cat2', # cat 5
]

numeric_features = [
    'num1', # num
    'num2', # num
]


all_features = categorical_features + numeric_features

x = df[all_features]
# Response variable
# Merge took more than a week
y = None # Configure target variable

# %%
# PREPROCESS DATA
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import cross_val_score
from sklearn.feature_selection import VarianceThreshold, SelectKBest, mutual_info_classif

# Use standard scaler for numeric features
numeric_transformer = Pipeline(steps=[
    ('scaler', StandardScaler())
])

# Use one hot encoding for categorical features
categorical_transformer = Pipeline(steps = [
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# Put them together in a ColumnTransformer processor
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)])

# %%
# DEFINE ALL CLASSIFIERS
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import SGDClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier


classifiers = [
    # LM
    ('Logistic Regression', LogisticRegression()),
    ('SGD Classifier', SGDClassifier()),
    # TREES
    ('Random Forest', RandomForestClassifier()),
    ('Decision Tree', DecisionTreeClassifier()),
    # NNETS
    ('MLP Classifier', MLPClassifier()),
    ('2 Layer MLP Classifier', MLPClassifier(hidden_layer_sizes=(100, 50))),
]

# %%
# ITERATE OVER ALL CLASSIFIERS

for name, classifier in classifiers:

    print(f'{name}', end=' - ')
    pipe = Pipeline(steps=[('preprocessor', preprocessor), \
        ('variance', VarianceThreshold()), \
        #('k-best', SelectKBest(mutual_info_classif, 15)), \
        (name, classifier)])
    # Logistic Regression
    scores = cross_val_score(pipe, x, y, cv=10, scoring='roc_auc')
    print(f'mean score {np.mean(scores)}, std {np.std(scores)}')


