# %%
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

os.getcwd()

# %%
data = ''
df = pd.read_csv(data)

SEARCH_PARAMETERS = False

def search_best_parameter(pipe, param_grid, x, y):
    """
        Utility function for searching for the best parameter within param_grid 
        in the ML pipeline.
        Returns a tuple with the best params and the best score (fit)  
    """
    search = GridSearchCV(pipe, param_grid, n_jobs=-1, cv=10)
    search.fit(x, y)
    return search.best_params_, search.best_score_


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

# Response variable
x = df[all_features]
# Merge took more than a week
y = None # CONFIGURE target variable

# Keep an explicit train/test set for the feature permutation experiment
from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(x, y, stratify=y, random_state=42, test_size=.1)

# %%
# We want to explore a handful of ML methods
# So we will use pipelines to search the best method, hyperparameter, etc.
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.decomposition import PCA
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import cross_val_score
from sklearn.feature_selection import VarianceThreshold, SelectFromModel, SelectKBest, chi2, mutual_info_classif


# %%
# PREPROCESS DATA
# Create the transformers for each type of columns
numeric_transformer = Pipeline(steps=[
    ('scaler', StandardScaler())
])
  

categorical_transformer = Pipeline(steps = [
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)])


# %%
def get_feature_names(estimator, preprocessor_id = 'preprocessor', selector_id = 'k-best'):
    """
        This is a (very bad) utility function to get the feature names
        from a pipeline with:
            - preprocessor with onehot
            - k-best selector
        
    """
    # Getting the generate category fetures names
    # FIXME: Try to make it more generic to every pipeline (not sure if it possible)
    # FIXME: It seems sklearn-pandas can help mitigate this issue, try this later
    category_features = estimator[preprocessor_id].transformers_[1][1]['onehot'].get_feature_names(categorical_features)
    all_features = list(category_features) + numeric_features

    # Getting the indexes of selected features with K-Best
    selected_features_indexes = estimator[selector_id].get_support(indices=True)
    selected_features = np.take(all_features, selected_features_indexes)
    return selected_features

# 

# %%
from sklearn.ensemble import RandomForestClassifier
# RANDOM FOREST
# Random Forest seems the best model form the ones we tried
pipe = Pipeline(steps=[('preprocessor', preprocessor), \
    ('variance', VarianceThreshold()), \
    ('k-best', SelectKBest(mutual_info_classif, 15)), \
    ('forest', RandomForestClassifier())])

clf = pipe.fit(x_train, y_train)

# %%
# Tree feature importance
# From https://scikit-learn.org/stable/auto_examples/inspection/plot_permutation_importance.html#sphx-glr-auto-examples-inspection-plot-permutation-importance-py
feature_importances = clf['forest'].feature_importances_
sorted_idx = feature_importances.argsort()
 
# Plot the feture importance
import matplotlib.pyplot as plt

features = get_feature_names(clf)

y_ticks = np.arange(0, len(features))
fig, ax = plt.subplots()
ax.barh(y_ticks, feature_importances[sorted_idx])
ax.set_yticklabels(features[sorted_idx])
ax.set_yticks(y_ticks)
ax.set_title("Random Forest Feature Importances (MDI)")
fig.tight_layout()
plt.show()

# %%
# Permutation Importance (test set)
from sklearn.inspection import permutation_importance
clf = pipe.fit(x_train, y_train)

result = permutation_importance(clf, x_test, y_test, n_repeats=20,
                                random_state=42, n_jobs=-1)
sorted_idx = result.importances_mean.argsort()

fig, ax = plt.subplots()
ax.boxplot(result.importances[sorted_idx].T,
           vert=False, labels=x_test.columns[sorted_idx])
ax.set_title("Permutation Importances (test set)")
fig.tight_layout()
plt.show()

# %%
# Permutation Importance (training set)
from sklearn.inspection import permutation_importance
clf = pipe.fit(x_train, y_train)

result = permutation_importance(clf, x_train, y_train, n_repeats=20,
                                random_state=42, n_jobs=-1)
sorted_idx = result.importances_mean.argsort()

fig, ax = plt.subplots()
ax.boxplot(result.importances[sorted_idx].T,
           vert=False, labels=x_train.columns[sorted_idx])
ax.set_title("Permutation Importances (training set)")
fig.tight_layout()
plt.show()


# %%
# ELI5 explain weights
import eli5
eli5.explain_weights_df(clf[-1], feature_names=get_feature_names(clf))

# %%
from sklearn.linear_model import LogisticRegression
# LOGISTIC REGRESSION 
# ALthough not the best mode, this one is easier to understand
pipe = Pipeline(steps=[('preprocessor', preprocessor), \
    ('variance', VarianceThreshold()), \
    ('k-best', SelectKBest(mutual_info_classif, 15)), \
    ('forest', LogisticRegression())])

clf = pipe.fit(x_train, y_train)
eli5.explain_weights_df(clf[-1], feature_names=get_feature_names(clf))

