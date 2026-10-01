

from backend.ml.data_set import ML as MLs
# here we are getting a model of logistic regression and training it on the data set we have created in the data_set.py file
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler




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
        
        self.scaler = StandardScaler()

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_validation_scaled = self.scaler.transform(X_validation)

        # model gets trained on the  training data set 
        # max_iter=1000 gives Logistic Regression enough optimization
        # iterations to converge while learning the model coefficients

        self.model = LogisticRegression(max_iter = 1000,class_weight='balanced')
        # fit() method is used to train the model on the training data set 

        self.model.fit(X_train_scaled,Y_train)

        # predict() method is used to make predictions on the test data set
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



