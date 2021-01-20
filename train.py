#%%
import pandas as pd

from simpletransformers.classification import ClassificationModel

# Train and Evaluation data needs to be in a Pandas Dataframe of two columns. The first column is the text with type str, and the second column is the label with type int.

df = pd.DataFrame(train_data)
train=df.sample(frac=0.8,random_state=200)
eval_df=df.drop(train.index)

# Create a ClassificationModel
model = ClassificationModel("roberta", "roberta-base")

# Train the model
# model.train_model(train_df)

# Evaluate the model
result, model_outputs, wrong_predictions = model.eval_model(eval_df)

# %%
