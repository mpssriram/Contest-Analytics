import sys
import pathlib
# lets this file run directly (Run button / python file.py), not only with python -m
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import pandas as pd
from backend.ml.data_set import ML as MLs
import pathlib as path

class MultiDataProcess:
    def __init__(self, handles):
        self.handles = handles
        self.ml_instances = [MLs(handle=handle) for handle in handles]

  

    def get_features_for_all_handles(self):
        all_features = []
        for ml_instance in self.ml_instances:
            try:
                features, status = ml_instance.features()
                features['handle'] = ml_instance.handle

                # solved = (features['status'] == 1).sum()
                # unsolved = (features['status'] == 0).sum()
                # print(ml_instance.handle, "rows:", len(features), "solved:", solved, "unsolved:", unsolved)

                all_features.append(features)
            except Exception as e:
                print("Failed for", ml_instance.handle, ":", e)

        return all_features

class MultiDataProcessTocsv(MultiDataProcess):

    def __init__(self, contest_id='1100'):
        csv_path = path.Path(__file__).parent / 'data_set_training' / f'{contest_id}.csv'
        df = pd.read_csv(csv_path)
        handles = list(df['handle'])
        super().__init__(handles)


    def save_features_to_csv(self):
        all_features = self.get_features_for_all_handles()
        if len(all_features) == 0:
            raise ValueError("Features failed for every handle, nothing to save (see the 'Failed for' lines above)")
        combined_df = pd.concat(all_features, ignore_index=True)

        combined_df = combined_df.drop(columns=['previous_tag_solved', 'previous_tag_attempted', 'previous_tag_success_rate'])

        save_path = path.Path(__file__).parent / 'data_set_training' / 'all_users_features.csv'

        # add to the users we already have instead of overwriting them
        # a handle that shows up again gets its old rows swapped for the fresh ones
        if save_path.exists():
            old_df = pd.read_csv(save_path)
            repeated = set(old_df['handle']) & set(combined_df['handle'])
            print("repeated users replaced:", len(repeated))
            old_df = old_df[~old_df['handle'].isin(repeated)]
            combined_df = pd.concat([old_df, combined_df], ignore_index=True)

        combined_df.to_csv(save_path, index=False)
        print("Saved to", save_path)

        print("users:", combined_df['handle'].nunique())
        print("rows:", len(combined_df))
        print("solved:", (combined_df['status'] == 1).sum())
        print("unsolved:", (combined_df['status'] == 0).sum())

if __name__ == "__main__":
   process = MultiDataProcessTocsv()
   process.save_features_to_csv()