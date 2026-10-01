import pandas as pd
import numpy as np

from backend.services.codeforces_client import CodeforcesClient


class ML:

    def __init__(self,handle : str):

        self.handle = handle

    def data_set_cleaning(self):
        data = CodeforcesClient(handle=self.handle)
        solved = data.solved_problem_records_ML()
        unsolved = data.unsolved_problem_records_ML()
        id = []
        rating_list = []
        tags = []
        attempts = []
        status = []
        firstTriedAt = []


        for problem in solved:
            id.append(problem['id'])
            rating_list.append(problem['rating'])
            tags.append(problem['tags'])
            attempts.append(problem['attempts'])
            status.append(problem['solved'])
            firstTriedAt.append(problem['firstTriedAt'])

        for problem in unsolved:
            id.append(problem['id'])
            rating_list.append(problem['rating'])
            tags.append(problem['tags'])
            attempts.append(problem['attempts'])
            status.append(problem['solved'])
            firstTriedAt.append(problem['firstTriedAt'])


        df = pd.DataFrame({
            'id': id,
            'rating' : rating_list,
            'tags' : tags,
            'attempts' : attempts,
            'status' : status,
            'firstTriedAt' : firstTriedAt 
        })
        df = df.sort_values(by = 'firstTriedAt')
        df = df.dropna(subset=["rating"])
        df = df.reset_index(drop=True)
        return df

    def features_building(self):
        data = self.data_set_cleaning()
        datai = CodeforcesClient(handle=self.handle)
        tags = {}
        solved = datai.solved_problem_records_ML()
        unsolved = datai.unsolved_problem_records_ML()
        overall_sucesss_rate = len(solved) / (len(solved) + len(unsolved)) if (len(solved) + len(unsolved)) != 0 else 0
        overall_avg_rating_solved = sum([problem['rating'] for problem in solved]) / len(solved) if len(solved) != 0 else 0

        for tag_list,solve in zip(data['tags'],data['status']):
            for tag in tag_list:
                if tag not in tags:
                    if solve == 1:
                        tags[tag] = [1, 0,1.0]
                    else:
                        tags[tag] = [0, 1,0.0]
                else:
                    if solve == 1:
                        tags[tag][0] += 1
                        tags[tag][2] = (tags[tag][0] / (tags[tag][0] + tags[tag][1]))
                    else:
                        tags[tag][1] += 1
                        tags[tag][2] = (tags[tag][0] / (tags[tag][0] + tags[tag][1]))

        for tag in tags:
            # Calculate total attempts for each tag
            tags[tag].append(tags[tag][0] + tags[tag][1])
            rating_solved = 0
            rating_unsolved = 0
            for j in range(len(data)):
                # Calculate total rating for solved and unsolved problems for each tag
                if tag in data['tags'][j] and data['status'][j] == 1:
                    rating_solved += data['rating'][j]
                elif tag in data['tags'][j] and data['status'][j] == 0:
                    rating_unsolved += data['rating'][j]
            tags[tag].append(rating_solved)
            tags[tag].append(rating_unsolved)

        for tag in tags:
            # Calculate average rating for solved and unsolved problems
            tags[tag][len(tags[tag]) - 1] = int(tags[tag][len(tags[tag]) - 1] / tags[tag][1])    if tags[tag][1] != 0 else 0
            # Calculate average rating for solved problems
            tags[tag][len(tags[tag]) - 2] = int(tags[tag][len(tags[tag]) - 2] / tags[tag][0]) if tags[tag][0] != 0 else 0
            
            # Calculate adjusted success rate 
            adjusted_sucess_rate = ((tags[tag][0] + 5*overall_sucesss_rate) / (tags[tag][0] + tags[tag][1] + 5)) if (tags[tag][0] + tags[tag][1] + 5) != 0 else 0
           
            # Calculate difficulty factor based on average rating of solved problems
            diffculty_factor = tags[tag][4]/overall_avg_rating_solved if overall_avg_rating_solved != 0 else 0
            tags[tag].append(adjusted_sucess_rate)
            tags[tag].append(diffculty_factor)
            
            # Calculate topic strength score
            topic_strength_score = adjusted_sucess_rate * diffculty_factor
            tags[tag].append(topic_strength_score)



        for tag in tags:
            tags[tag] = {
                'solved': tags[tag][0],
                'unsolved': tags[tag][1],
                'success_rate': tags[tag][2],
                'total_attempts': tags[tag][3],
                'avg_rating_solved': tags[tag][4],
                'avg_rating_unsolved': tags[tag][5],
                'adjusted_success_rate': tags[tag][6],
                'difficulty_factor': tags[tag][7],
                'topic_strength_score': tags[tag][8]
            }

        # from_dict helps in converting the dictionary to a DataFrame, orient='index' means that the keys of the dictionary will become the index of the DataFrame
        tags_df = pd.DataFrame.from_dict(tags, orient='index')
        tags_df = tags_df.reset_index().rename(columns={'index': 'tag'})


        return tags_df

    def features(self):
        data = self.data_set_cleaning()
        # 1. Previous solved count
        previous_solved_data = []
        previous_solved = 0

        for status in data["status"]:
            previous_solved_data.append(previous_solved)

            if status == 1:
                previous_solved += 1

        # 2. Previous average solved rating
        previous_average_solved_rating_data = []

        previous_rating_sum = 0
        previous_rating_count = 0

        for rating, status in zip(data["rating"], data["status"]):

            # Store history BEFORE current problem
            if previous_rating_count != 0:
                previous_average_solved_rating_data.append(
                    previous_rating_sum / previous_rating_count
                )
            else:
                previous_average_solved_rating_data.append(0)

            # Update history AFTER current problem
            if status == 1:
                previous_rating_sum += rating
                previous_rating_count += 1

        # 3. Previous solved count for each tag
        tags_so_far_solved = {}
        tags_so_far_solved_data = []

        for tags, status in zip(data["tags"], data["status"]):

            # Make sure current tags exist
            for tag in tags:
                if tag not in tags_so_far_solved:
                    tags_so_far_solved[tag] = 0

            # Store BEFORE current problem
            tags_so_far_solved_data.append(
                tags_so_far_solved.copy()
            )

            # Update AFTER current problem
            if status == 1:
                for tag in tags:
                    tags_so_far_solved[tag] += 1
        # 4. Previous attempted count for each tag
        tags_so_far_attempted = {}
        tags_so_far_attempted_data = []

        for tags in data["tags"]:

            for tag in tags:
                if tag not in tags_so_far_attempted:
                    tags_so_far_attempted[tag] = 0

            # Store BEFORE current problem
            tags_so_far_attempted_data.append(
                tags_so_far_attempted.copy()
            )

            # Every problem is an attempt
            for tag in tags:
                tags_so_far_attempted[tag] += 1

        # 5. Historical success rate for each tag
        tag_success_rate_data = []

        for tags_solved, tags_attempted in zip(
            tags_so_far_solved_data,
            tags_so_far_attempted_data
        ):

            tag_success_rate = {}

            for tag in tags_attempted:

                if tags_attempted[tag] != 0:
                    tag_success_rate[tag] = (
                        tags_solved.get(tag, 0)
                        / tags_attempted[tag]
                    )
                else:
                    tag_success_rate[tag] = 0

            tag_success_rate_data.append(tag_success_rate)
        # 6. Average historical success rate for tags of current problem
        avg_tags_success_rate_data = []

        for current_tags, rates in zip(
            data["tags"],
            tag_success_rate_data
        ):

            values = [
                rates.get(tag, 0)
                for tag in current_tags
            ]

            if values:
                avg_tags_success_rate_data.append(
                    sum(values) / len(values)
                )
            else:
                avg_tags_success_rate_data.append(0)
        # 7. Average previous tag experience (attempted) for tags of current problem
        avg_tags_rate_attempted_data = []

        for current_tags, attempted in zip(
            data["tags"],
            tags_so_far_attempted_data
        ):

            values = [
                attempted.get(tag, 0)
                for tag in current_tags
            ]
            if values:
                avg_tags_rate_attempted_data.append(
                    sum(values) / len(values))
            else:
                avg_tags_rate_attempted_data.append(0)


        # 8. User rating at the time of each problem attempt
        datai = CodeforcesClient(self.handle)
        user_rating_history = datai.user_rating_history()
        user_rating_history = sorted(
            user_rating_history,
            key=lambda x: x["ratingUpdateTimeSeconds"]
        )

        user_rating_at_time_data = []

        if len(user_rating_history) == 0:

            # User has never had a rated contest
            user_rating_at_time_data = [0] * len(data)

        else:

            # Before user's first rated contest
            current_rating = user_rating_history[0]["newRating"]

            history_index = 0

            for first_tried_at in data["firstTriedAt"]:

                # Apply every rating update that occurred
                # before this problem was attempted
                while (
                    history_index < len(user_rating_history)
                    and user_rating_history[history_index][
                        "ratingUpdateTimeSeconds"
                    ] <= first_tried_at
                ):

                    current_rating = user_rating_history[
                        history_index
                    ]["newRating"]

                    history_index += 1

                user_rating_at_time_data.append(current_rating)


        rating_gap = []
        for rating,user_rating in zip(data['rating'],user_rating_at_time_data):
            rating_gap.append(rating - user_rating)

            




    
        data["previous_solved_count"] = previous_solved_data

        data["previous_avg_solved_rating"] = (
            previous_average_solved_rating_data
        )

        data["previous_tag_solved"] = (
            tags_so_far_solved_data
        )

        data["previous_tag_attempted"] = (
            tags_so_far_attempted_data
        )

        data["previous_tag_success_rate"] = (
            tag_success_rate_data
        )

        data["previous_avg_tag_success_rate"] = (
            avg_tags_success_rate_data
        )

        data["previous_avg_tag_attempted"] = (
            avg_tags_rate_attempted_data
        )

        data["user_rating_at_time"] = (
            user_rating_at_time_data
        )

        data['rating_gap'] = ( 
            rating_gap
        )


        return data,data['status']

    

            

        



if __name__ == '__main__':
    handle = input("Enter the handle of the user: ")
    fetcher = ML(handle=handle)
    data = fetcher.features_building()
    # print(data)

    # print(fetcher.data_set_cleaning())
    print(fetcher.features())








