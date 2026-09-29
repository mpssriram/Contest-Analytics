from model_pipeline import ModelPipeline as MP
from evaluation import Evaluation
import pathlib as path
import pandas as pd
from sklearn.metrics import roc_auc_score

FEATURES = ['rating','previous_solved_count','previous_avg_solved_rating','previous_avg_tag_success_rate','previous_avg_tag_attempted','user_rating_at_time','rating_gap']


class Training:

    def __init__(self):
        self.pipeline = MP()

    def split_per_user(self):
        df = pd.read_csv(path.Path(__file__).parent / 'data_set_training' / 'all_users_features.csv')


        X_train = []
        Y_train = []
        X_val = []
        Y_val = []
        X_test = []
        Y_test = []

        for handle in df['handle'].unique():
            user_df = df[df['handle'] == handle]
            parts = self.pipeline.train_test_split(user_df[FEATURES], user_df['status'])
            X_train.append(parts[0])
            Y_train.append(parts[1])
            X_val.append(parts[2])
            Y_val.append(parts[3])
            X_test.append(parts[4])
            Y_test.append(parts[5])

        self.X_train = pd.concat(X_train, ignore_index=True)
        self.Y_train = pd.concat(Y_train, ignore_index=True)
        self.X_validation = pd.concat(X_val, ignore_index=True)
        self.Y_validation = pd.concat(Y_val, ignore_index=True)
        self.X_test = pd.concat(X_test, ignore_index=True)
        self.Y_test = pd.concat(Y_test, ignore_index=True)

        return self.X_train, self.Y_train, self.X_validation, self.Y_validation, self.X_test, self.Y_test

    def training(self):
        X_train, Y_train, X_validation, Y_validation, X_test, Y_test = self.split_per_user()
        self.model, self.y_prob, self.Y_validation = self.pipeline.model_trainning(
            X_train, Y_train, X_validation, Y_validation, X_test, Y_test
        )


if __name__ == "__main__":
    training = Training()
    training.training()

    # thresholds = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]
    # print("threshold, TP, TN, FP, FN, metrics")
    # for t in thresholds:
    #     ev = Evaluation(threshold=t, y_prob=training.y_prob, y_true=training.Y_validation)
    #     print(t, ev.model_calculations(), ev.metrics())

    # print("Validation ROC-AUC:", roc_auc_score(training.Y_validation, training.y_prob))

    print("TEST RESULT at threshold 0.65")
    y_prob_test, Y_test = training.pipeline.test_probabilities(training.X_test, training.Y_test)
    ev = Evaluation(threshold=0.65, y_prob=y_prob_test, y_true=Y_test)
    print(ev.model_calculations())
    print(ev.metrics())
    print("Test ROC-AUC:", roc_auc_score(Y_test, y_prob_test))

        
