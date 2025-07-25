# -*- coding: utf-8 -*-
"""Telco_Customer_Churn.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1kaDfLKQxFsSzpQJh3utq_G2WZgO6J1aF

# Telco Customer Churn

### 1. Introduction

#### Problem Overview

In a subscription-based business, customer churn refers
 to customers leaving or cancelling their service.
 Accurately predicting which customers are likely to churn enables proactive retention strategies, reducing revenue loss.

 This project uses machine learning techniques to classify whether a customer will churn based on behavioral and service-related features.

#### Dataset Descitption

[Dataset Link](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)

### Housekeeping
"""

# Commented out IPython magic to ensure Python compatibility.
!pip install ipython-autotime
# %load_ext autotime

"""### Data

#### Data Loading
"""

import kagglehub

# Download latest version
path = kagglehub.dataset_download("blastchar/telco-customer-churn")

print("Path to dataset files:", path)

import pandas as pd

df = pd.read_csv(path + "/WA_Fn-UseC_-Telco-Customer-Churn.csv")

df.shape

"""#### Initial Inspection"""

df.info()

# check missing values
df.isnull().sum()

# check unique values
df.nunique()

"""#### Data Cleansing"""

# Drop customerID
df.drop(columns=['customerID'], inplace=True)

# object (string) — to - numeric.
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
# df.info()

# Convert target variable Churn to 0 and 1
df['Churn'] = df['Churn'].map({'No': 0, 'Yes': 1})
#df.head()

# check categorical columns - will eventually need to be encoded.
categorical_cols = df.select_dtypes(include='object').columns.tolist()
print(categorical_cols)

df.head()

"""#### Exploratory Data Analysis

Columns like State, International Plan, and Voice Mail Plan contain text categories that need to be turned into numbers for the model to understand.

`LabelEncoder()` does this by giving each unique value a numeric code. We simply loop through these columns and use `fit_transform()` to convert them.
"""

from sklearn.preprocessing import LabelEncoder

labelencoder = LabelEncoder()
categorical_cols = ['gender', 'Partner', 'Dependents', 'PhoneService',
                    'MultipleLines', 'InternetService', 'OnlineSecurity',
                    'OnlineBackup', 'DeviceProtection', 'TechSupport',
                    'StreamingTV', 'StreamingMovies', 'Contract',
                    'PaperlessBilling', 'PaymentMethod', 'Churn']

for col in categorical_cols:
    df[col] = labelencoder.fit_transform(df[col])

df

"""we make sure all numeric columns are clean.
TotalCharges sometimes has empty strings, so we use `pd.to_numeric` to convert it, turning invalid entries into `NaN`, then fill those with the column’s median to keep the data consistent.
"""

df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df['TotalCharges'] = df['TotalCharges'].fillna(df['TotalCharges'].median())

# plot churn distribution
import matplotlib.pyplot as plt
import seaborn as sns

# plt.figure(figsize=(6,4))
# sns.countplot(x='Churn', data=df)
# plt.title('Churn Distribution')
# plt.xlabel('Churn (0 = No, 1 = Yes)')
# plt.ylabel('Count')
# plt.savefig('churn_dist.png', bbox_inches='tight')
# plt.show()
plt.figure(figsize=(3,2))  # smaller size
sns.countplot(x='Churn', data=df)
plt.title('Churn Distribution', fontsize=8)
plt.xlabel('Churn (0=No, 1=Yes)', fontsize=7)
plt.ylabel('Count', fontsize=7)
plt.tick_params(axis='both', which='major', labelsize=6)
plt.tight_layout()
plt.savefig('churn_dist_small.png', dpi=150, bbox_inches='tight')  # dpi higher for clarity
plt.show()

# Plot tenure distribution by churn
plt.figure(figsize=(3,2))
sns.histplot(data=df, x='tenure', hue='Churn', multiple='stack', bins=30)
plt.title('Tenure Distribution by Churn')
plt.xlabel('Tenure (Months)')
plt.ylabel('Number of Customers')
plt.savefig('tenue_dist_by_churn.png', bbox_inches='tight')
plt.show()

# Plot monthly charges distribution by churn
plt.figure(figsize=(3,2))
sns.histplot(data=df, x='MonthlyCharges', hue='Churn', multiple='stack', bins=30)
plt.title('Monthly Charges by Churn')
plt.xlabel('Monthly Charges ($)')
plt.ylabel('Number of Customers')
plt.savefig('month_charges_by_churn.png', bbox_inches='tight')
plt.show()

# Bar plot: Contract type vs churn
plt.figure(figsize=(3,2))
sns.countplot(x='Contract', hue='Churn', data=df)
plt.title('Churn by Contract Type')
plt.xlabel('Contract Type')
plt.ylabel('Count')
plt.savefig('churn_by_contract_type.png', bbox_inches='tight')
plt.show()

# Bar plot: Internet service vs churn
plt.figure(figsize=(3,2))
sns.countplot(x='InternetService', hue='Churn', data=df)
plt.title('Churn by Internet Service Type')
plt.xlabel('Internet Service')
plt.ylabel('Count')
plt.savefig('churn_by_internet.png', bbox_inches='tight')
plt.show()

"""#### Feature Engineering

##### Feature Selection and Splitting Data
"""

# We divide the data into input features (X) and the target (y),
# then split it into training and test sets.
from sklearn.model_selection import train_test_split

# Note: The below line cause a compile error -- customerID is already dropped
# at this point. I will comment out and correct the code - B.J.
# X = df.drop(['customerID', 'Churn'], axis=1)
X = df.drop('Churn', axis=1)
y = df['Churn'] # target

X_train, X_test, y_train, y_test = train_test_split(X,
                                                    y,
                                                    test_size=0.2,
                                                    random_state=0)
print(X_train.dtypes)

"""##### Feature Scaling

Since our features vary in scale, we standardize them to help the model learn better and faster.

`StandardScaler()` shifts data to have a mean of 0 and a standard deviation of 1, putting all features on the same scale.

`fit_transform(X_train)`: fits and scales the training data.

`transform(X_test)`: scales the test data using the same parameters.
"""

from sklearn.preprocessing import StandardScaler

# Capture feaures for evaluationm prior to scaling (must be dataframe)
churn_feature_names = X_train.columns

# Perform the scaling
churn_scaler = StandardScaler()
scaled_X_train = churn_scaler.fit_transform(X_train)
scaled_X_test = churn_scaler.transform(X_test)

'''
Side note: After this transformation, X_train and X_test are NumPy arrays,
not pandas DataFrames. Access to .columns, .head() is lost. Renamed for clarity
'''

"""### Model Training"""

#import pandas as pd
#from sklearn.model_selection import train_test_split
#from sklearn.preprocessing import LabelEncoder

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report

# Models and hyperparameter tuning
baseline_models = {
    "Logistic Regression": (LogisticRegression(max_iter=2000),
        {'C': [0.01, 0.1, 1, 10]}),
    "Decision Tree": (DecisionTreeClassifier(),
        {'max_depth': [3, 5, 7], 'criterion': ['gini', 'entropy']})
}

# Dictionary to store best estimators, predictions and probabilities
baseline_best_models = {}
baseline_preds = {}
baseline_probs = {}

# Training and evaluation
for name, (model, params) in baseline_models.items():
    grid = GridSearchCV(model, params, cv=5,
                        scoring='accuracy').fit(scaled_X_train, y_train)

    # Collect best model for later evaluation
    best_model = grid.best_estimator_
    baseline_best_models[name] = best_model

    # Collect model prediction for later evaluation
    baseline_preds[name] = best_model.predict(scaled_X_test)

    # Probabilities
    if hasattr(best_model, "predict_proba"):
        baseline_probs[name] = best_model.predict_proba(scaled_X_test)[:, 1]

    print(f"{name}:", grid.best_params_)
    print(classification_report(y_test, grid.predict(scaled_X_test)))

"""### **Advanced Modeling**"""

# Perform Hyperparametric Tuning
# Create parameter grid for RF
'''
Random Forest Hyperparameters Not Used:
    max_leaf_nodes: Max number of leaf nodes
    bootstrap: Whether bootstrap samples are used
    n_jobs: Number of cores used for training
'''
churn_randomforest_param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [5, 10, 15],
    'min_samples_split': [2, 5],
    'class_weight': ['balanced'],
    'random_state': [42],
    'max_features': ['sqrt', 'log2'],
    'criterion': ['gini', 'entropy'],
}

# Create parameter grid for XGB
'''
XGBoost Hyperparameters Not Used:
    objective: Learning task (binary classification = 'binary:logistic')
    eval_metric: Metric to evaluate on validation set
'''
churn_xgboost_param_grid = {
    'n_estimators': [100, 200],
    'learning_rate': [0.01, 0.1],
    'max_depth': [3, 6],
    'subsample': [0.8, 1.0],
    'colsample_bytree': [0.8, 1.0],
    'scale_pos_weight': [1, 2],
    'min_child_weight': [1, 5],
    'gamma': [0, 0.1, 0.2],
    'random_state': [42],
    'objective': ['binary:logistic'],
}

"""### **Find the Best Values**"""

from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

print("Tuning takes approxmiately 3 minutes...")
# Random Forest Grid Search
churn_rf_grid = GridSearchCV(
    RandomForestClassifier(),
    churn_randomforest_param_grid,
    scoring='f1',
    cv=5,
    verbose=1,
    n_jobs=-1
)
churn_rf_grid.fit(scaled_X_train, y_train)

# XGBoost Grid Search
churn_xgb_grid = GridSearchCV(
    XGBClassifier(
        use_label_encoder=False,
        eval_metric='logloss'
    ),
    churn_xgboost_param_grid,
    scoring='f1',
    cv=5,
    verbose=1,
    n_jobs=-1
)
churn_xgb_grid.fit(scaled_X_train, y_train)

"""### **Advanced Model Evaluation**"""

from sklearn.metrics import classification_report, confusion_matrix

# Display Results of Random Forest
print("Best Churn RF Params:", churn_rf_grid.best_params_)

# Best model for Random Forest
churn_rf_best_model = churn_rf_grid.best_estimator_
print(classification_report(y_test,
                            churn_rf_best_model.predict(scaled_X_test)))

# Display Results for XGBoost
print("Best XGB Params:", churn_xgb_grid.best_params_)

# Best model for XGB
churn_xgb_best_model = churn_xgb_grid.best_estimator_
print(classification_report(y_test,
                            churn_xgb_best_model.predict(scaled_X_test)))

"""## Interpretation

### **Generate Predictions**
"""

# Create Predictions and Probabilities for Random Forest
churn_rf_preds = churn_rf_best_model.predict(scaled_X_test)
churn_rf_probs = churn_rf_best_model.predict_proba(scaled_X_test)[:, 1]

# Create Predictions and Probabilities for XGBoost
churn_xgb_preds = churn_xgb_best_model.predict(scaled_X_test)
churn_xgb_probs = churn_xgb_best_model.predict_proba(scaled_X_test)[:, 1]

"""### **Make Confusion Matrices**"""

import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

def plot_conf_matrix(y_actual, y_pred, title, map_color='Blues'):
    cm = confusion_matrix(y_actual, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap=map_color)
    plt.title(f"{title} Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")

    # Save the figure with model name in filename
    plot_filename = f"{title.replace(' ', '_').lower()}_confusion_matrix.png"
    plt.savefig(plot_filename, bbox_inches='tight')
    plt.show()

# Draw earlier modeling matrices
plot_conf_matrix(y_test,
                baseline_preds["Logistic Regression"],
                "Logistic Regression"
)

plot_conf_matrix(y_test,
                baseline_preds["Decision Tree"],
                "Decision Tree",
                "Oranges"
)

# Draw both matrices for the Advanced modeling.
plot_conf_matrix(y_test, churn_rf_preds, "Random Forest", "Greens")
plot_conf_matrix(y_test, churn_xgb_preds, "XGBoost", 'Purples')

"""### **Generate ROC Curves**"""

from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt


plot_counter = 1
# Mirror the color mappings from conf matrices
MODEL_COLORS = {
    "Logistic Regression": "#3498db",   # blue
    "Decision Tree": "#e67e22",         # orange
    "Random Forest": "#2ecc71",         # green
    "XGBoost": "#6a0dad"                # purple
}

def plot_roc_curves(y_true, model_probs_dict):
    '''
    Generates a reuseable roc curve for multiple models.
    '''
    global plot_counter
    plt.figure(figsize=(8, 6))

    # Iterate through the input models and draw lines
    for model_name, probs in model_probs_dict.items():
        fpr, tpr, _ = roc_curve(y_true, probs)
        roc_auc = auc(fpr, tpr)
        mod_color = MODEL_COLORS.get(model_name, None)
        plt.plot(fpr, tpr, label=f"{model_name} (AUC = {roc_auc:.2f})",
                 color=mod_color)

    # Standard random guess line
    plt.plot([0, 1], [0, 1], 'k--', label='Random Guess')
    plt.title("ROC Curve Comparison")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend(loc="lower right")
    plt.grid(True)
    plt.tight_layout()

    # File will be saved for later extraction
    plt.savefig(f'churn_roc_curve_{plot_counter}.png', bbox_inches='tight')
    plot_counter += 1
    plt.show()

# Draw the plot with Logistic Regression model
plot_roc_curves(
    y_test,
    {
        "Logistic Regression": baseline_probs["Logistic Regression"]
    }
)

# Draw the plot with Decision Tree model
plot_roc_curves(
    y_test,
    {
        "Decision Tree": baseline_probs["Decision Tree"]
    }
)

# Draw the plot with Random Forest model
plot_roc_curves(
    y_test,
    {
        "Random Forest": churn_rf_probs
    }
)

# Draw the plot with XGBoost model
plot_roc_curves(
    y_test,
    {
        "XGBoost": churn_xgb_probs
    }
)

# Draw the plot with combined models
plot_roc_curves(
    y_test,
    {
        "Logistic Regression": baseline_probs["Logistic Regression"],
        "Decision Tree": baseline_probs["Decision Tree"],
        "Random Forest": churn_rf_probs,
        "XGBoost": churn_xgb_probs
    }
)

"""### **Evaluate Feature Importance**"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def generate_feature_importance_plot(model, feature_names, title):
    if hasattr(model, "feature_importances_"):
        # For tree-based models
        feat_importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        # For linear models like Logistic Regression
        feat_importances = np.abs(model.coef_[0])
    else:
        raise AttributeError("Model does not support feature importances.")

    # In Descending Order
    indices = np.argsort(feat_importances)[::-1]

    # Plot top 10
    plt.figure(figsize=(10, 6))
    sns.barplot(x=feat_importances[indices][:10],
            y=np.array(churn_feature_names)[indices][:10],
            color=MODEL_COLORS[title])

    plt.title(f"Top 10 Features - {title}")
    plt.xlabel("Importance Score")
    plt.ylabel("Feature")
    plt.tight_layout()

    # Save the figure with model name in filename
    plot_filename = f"{title.replace(' ', '_').lower()}_feature_imp.png"
    plt.savefig(plot_filename, bbox_inches='tight')
    plt.show()

# Get feature importances from trained Logistic Regression
model_name = "Logistic Regression"
generate_feature_importance_plot(baseline_best_models[model_name],
                                 churn_feature_names,
                                 model_name)

# Get feature importances from trained Decision Tree
model_name = "Decision Tree"
generate_feature_importance_plot(baseline_best_models[model_name],
                                 churn_feature_names,
                                 model_name)

# Get feature importances from trained Random Forest
generate_feature_importance_plot(churn_rf_best_model,
                                 churn_feature_names,
                                 "Random Forest")

# Get feature importances from trained XGBoost
generate_feature_importance_plot(churn_xgb_best_model,
                                 churn_feature_names,
                                 "XGBoost")