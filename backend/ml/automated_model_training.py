import sys
import pathlib
# lets this file run directly (Run button / python file.py), not only with python -m
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import pathlib as path

import joblib

from backend.ml.model_training_data_set_extraction import Data_set_extraction as DSEs
from backend.ml.multi_data_process import MultiDataProcessTocsv as MDPs
from backend.ml.Multi_data_training_model import Training as MPs
from backend.ml.evaluation import Evaluation


class Automated_model_training:

    def __init__(self, contest_id):
        self.contest_id = contest_id
        self.DSE = DSEs(contest_id)
        self.MP = MPs()

    def automated_model_training(self):
        # writes data_set_training/<contest_id>.csv
        self.DSE.randomize_handles()

        # builds features for those handles into all_users_features.csv
        self.MDP = MDPs(self.contest_id)
        self.MDP.save_features_to_csv()

        return self.train_and_save()

    def train_and_save(self):
        # trains on whatever is in all_users_features.csv, no Codeforces calls
        self.MP.training()

        # both models get scored on the same new test set
        y_prob_test, Y_test = self.MP.pipeline.test_probabilities(self.MP.X_test, self.MP.Y_test)
        new_evaluation = Evaluation(y_prob=y_prob_test, y_true=Y_test)
        new_auc = new_evaluation.roc_auc()
        new_brier = new_evaluation.brier_score()
        print("New model test ROC-AUC:", new_auc, " Brier:", new_brier)

        saved_dir = path.Path(__file__).parent / 'saved'
        model_path = saved_dir / 'model.joblib'
        scaler_path = saved_dir / 'scaler.joblib'

        if model_path.exists() and scaler_path.exists():
            old_model = joblib.load(model_path)
            old_scaler = joblib.load(scaler_path)
            old_prob = old_model.predict_proba(old_scaler.transform(self.MP.X_test))[:, 1]
            old_evaluation = Evaluation(y_prob=old_prob, y_true=Y_test)
            old_auc = old_evaluation.roc_auc()
            old_brier = old_evaluation.brier_score()
            print("Saved model test ROC-AUC:", old_auc, " Brier:", old_brier)

            # Brier checks ranking and the probabilities together (the recommender shows
            # the probabilities), and ROC-AUC must not drop by more than a little
            if new_brier >= old_brier or new_auc < old_auc - 0.01:
                print("New model is not better, keeping the saved one")
                return False

        saved_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.MP.pipeline.model, model_path)
        joblib.dump(self.MP.pipeline.scaler, scaler_path)
        print("Model saved to", saved_dir)
        return True


if __name__ == "__main__":
    contest_id = input("Enter the contest ID: ")
    Automated_model_training(contest_id).automated_model_training()
