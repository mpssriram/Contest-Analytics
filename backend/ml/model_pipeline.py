import sys
import pathlib
# lets this file run directly (Run button / python file.py), not only with python -m
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))



from backend.ml.data_set import ML as MLs
# here we are getting a model of logistic regression and training it on the data set we have created in the data_set.py file
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, FunctionTransformer
from sklearn.pipeline import make_pipeline
import numpy as np


def log_solved_count(x):
    # previous_solved_count only grows over time, so test rows (a user's latest problems)
    # land far above anything seen in training. log keeps those big counts in a range the model knows
    x = x.copy()
    x['previous_solved_count'] = np.log1p(x['previous_solved_count'])
    return x




class ModelPipeline:

    def __init__(self,handle = None):
        if handle is not None:
            self.ml = MLs(handle=handle)
            features,status = self.ml.features()
            self.features = features
            self.x = features[['rating','previous_solved_count','previous_avg_solved_rating','previous_avg_tag_success_rate','previous_avg_tag_attempted','user_rating_at_time','rating_gap']]
            self.y = status


    def train_test_split(self,x=None,y=None,test_size = 0.2,validation_size = 0.2):
        if x is None:
            x = self.x
            y = self.y

        split_index = int((len(x))*(1-test_size-validation_size))
        split_index_validation = int((len(x))*(1-test_size))

        X_train = x[:split_index]
        Y_train = y[:split_index]
        X_validation = x[split_index:split_index_validation]
        Y_validation = y[split_index:split_index_validation]
        X_test = x[split_index_validation:]
        Y_test = y[split_index_validation:]

        return X_train,Y_train,X_validation,Y_validation,X_test,Y_test

    def model_trainning(self,X_train,Y_train,X_validation,Y_validation,X_test,Y_test):
        
        # log step lives inside the scaler, so anything that loads scaler.joblib
        # (recommend.py, the saved-model check) gets the same log without extra code
        self.scaler = make_pipeline(FunctionTransformer(log_solved_count), StandardScaler())

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_validation_scaled = self.scaler.transform(X_validation)

        # model gets trained on the  training data set 
        # max_iter=1000 gives Logistic Regression enough optimization
        # iterations to converge while learning the model coefficients

        self.model = LogisticRegression(max_iter = 1000,class_weight='balanced')
        # fit() method is used to train the model on the training data set 

        self.model.fit(X_train_scaled,Y_train)

        # class_weight='balanced' trains as if half the rows were unsolved, which pushes every
        # probability down: problems scored 35-80% were really solved 88-94% of the time.
        # a sigmoid fitted on the validation rows maps the scores back to real solve chances.
        # it keeps the order of the scores, so ROC-AUC stays the same
        self.model = CalibratedClassifierCV(FrozenEstimator(self.model), method="sigmoid")
        self.model.fit(X_validation_scaled, Y_validation)

        # note: these validation probabilities were also used for the calibration,
        # so judge the model on the test set (test_probabilities), not on these
        y_prob = self.model.predict_proba(X_validation_scaled)[:,1]



        return self.model,y_prob,Y_validation

    def test_probabilities(self,X_test,Y_test):
        """
        This method is used to get the probabilities of the test set.
        """
        X_test_scaled = self.scaler.transform(X_test)
        y_prob_test = self.model.predict_proba(X_test_scaled)[:,1]
        return y_prob_test, Y_test


if __name__ == "__main__":
    handle = input("Enter the handle of the user: ")
    pipeline = ModelPipeline(handle=handle)

    print(pipeline.model_trainning())



