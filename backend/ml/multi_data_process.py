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

    def __init__(self):
        csv_path = path.Path(__file__).parent / 'data_set_training' / '1100.csv'
        df = pd.read_csv(csv_path)
        handles = list(df['handle'])
        super().__init__(handles)


    def save_features_to_csv(self):
        all_features = self.get_features_for_all_handles()
        combined_df = pd.concat(all_features, ignore_index=True)

        combined_df = combined_df.drop(columns=['previous_tag_solved', 'previous_tag_attempted', 'previous_tag_success_rate'])

        save_path = path.Path(__file__).parent / 'data_set_training' / 'all_users_features.csv'
        combined_df.to_csv(save_path, index=False)
        print("Saved to", save_path)

        print("users:", combined_df['handle'].nunique())
        print("rows:", len(combined_df))
        print("solved:", (combined_df['status'] == 1).sum())
        print("unsolved:", (combined_df['status'] == 0).sum())

if __name__ == "__main__":
   process = MultiDataProcessTocsv()
   process.save_features_to_csv()