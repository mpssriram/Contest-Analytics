import pathlib as path
import random

import pandas as pd
import requests




class Data_set_extraction:
    # min_rating / max_rating pick which users to collect. the default 500-1500 keeps the
    # old behaviour; use e.g. 1500-2400 on a Div 1 / Div 2 round to get stronger users
    def __init__(self,contest_id, min_rating=500, max_rating=1500):
        self.contest_id = contest_id
        self.min_rating = min_rating
        self.max_rating = max_rating
        self.url =  f'https://codeforces.com/api/contest.ratingChanges?contestId={contest_id}'

    def get_handles(self):
        response = requests.get(self.url)
        if response.status_code == 200 and response.json()['status'] == 'OK':
            handles = []
            rating = []
            for row in response.json()['result']:
                
                if row['oldRating'] >= self.min_rating and row['oldRating'] <= self.max_rating:
                    handles.append(row['handle'])
                    rating.append(row['oldRating'])

            return handles,rating
        else:
            raise RuntimeError(f"Failed to fetch data. Status code: {response.status_code}, {response.text}")

    def randomize_handles(self):
        handles,rating = self.get_handles()
        if len(handles) == 0:
            raise ValueError(f"No users rated {self.min_rating}-{self.max_rating} in contest {self.contest_id}. "
                             "Use the contest ID from the URL (codeforces.com/contest/<id>), not the round number.")

        random.seed(42)
        positions = random.sample(range(len(handles)), min(50, len(handles)))

        chosen_handles = []
        chosen_rating = []

        for i in positions:
            chosen_handles.append(handles[i])
            chosen_rating.append(rating[i])

        df = pd.DataFrame({
            'handle': chosen_handles,
            'rating': chosen_rating
        })

        df.to_csv(path.Path(__file__).parent / 'data_set_training' / f'{self.contest_id}.csv', index=False)


if __name__ == "__main__":
    contest_id = input("Enter the contest ID: ")
    data_set_extraction = Data_set_extraction(contest_id)
    data_set_extraction.randomize_handles()



