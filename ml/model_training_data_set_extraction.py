import pandas as pd
import requests
import random 




class Data_set_extraction:
    def __init__(self,contest_id):
        self.contest_id = contest_id
        self.url =  f'https://codeforces.com/api/contest.ratingChanges?contestId={contest_id}'

    def get_handles(self):
        response = requests.get(self.url)
        if response.status_code == 200 and response.json()['status'] == 'OK':
            handles = []
            rating = []
            for row in response.json()['result']:
                
                if row['oldRating'] >= 500 and row['oldRating'] <= 1500:
                    handles.append(row['handle'])
                    rating.append(row['oldRating'])

            return handles,rating
        else:
            return f"Failed to fetch data. Status code: {response.status_code}", response.text

    def randomize_handles(self):
        handles,rating = self.get_handles()
        positions = random.sample(range(len(handles)), 50)

        random.seed(42)
        chosen_handles = []
        chosen_rating = []

        for i in positions:
            chosen_handles.append(handles[i])
            chosen_rating.append(rating[i])

        df = pd.DataFrame({
            'handle': chosen_handles,
            'rating': chosen_rating
        })

        df.to_csv(f'./ml/data_set_training/{self.contest_id}.csv', index=False)


if __name__ == "__main__":
    contest_id = input("Enter the contest ID: ")
    data_set_extraction = Data_set_extraction(contest_id)
    data_set_extraction.randomize_handles()



