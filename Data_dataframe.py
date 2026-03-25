import pandas as pd 
from URLextract import Get_data as gd
import matplotlib.pyplot as plt


class Dataframe_former():
    def __init__(self,handle = ""):
        self.handle = handle

    def tags_count(self):

        unique_questions, question_tags = S1.question_tags()

        questions = pd.DataFrame({
            'Question Numbers': unique_questions,
            'Their respective tags': question_tags
        })

        return questions
    
    def question_tag_dataframe(self):
        unique_questions, question_tags = S1.question_tags()

        questions = pd.DataFrame({
            'Question Numbers': unique_questions,
            'Their respective tags': question_tags
        })

        return questions


    def tag_count_from_df(self):
        questions = self.question_tag_dataframe()

        tag_counts = (
            questions['Their respective tags']
            .explode()
            .value_counts()
            .reset_index()
        )

        tag_counts.columns = ['Tag', 'Count']
        return tag_counts
    
    def tags_plot(self):
        questions = self.tag_count_from_df()

        labels = [
            f"{tag} ({count})"
            for tag, count in zip(questions['Tag'], questions['Count'])
        ]

        fig, ax = plt.subplots(figsize=(6,4))

        wedges, texts, autotexts = ax.pie(
            questions['Count'],
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.75
        )

        ax.legend(
            wedges,
            labels,
            title="Tags",
            loc="center left",
            bbox_to_anchor=(1, 0.5)
        )

        plt.title('Tag Distribution')
        plt.tight_layout()
        plt.show()
    
    def show_unsolved(self):
        unique_questions, question_tags = S1.question_tags()
        questions = S1.unsolved_questions()
        return list(set(questions) - set(unique_questions))



if __name__ == '__main__':
    inputer = input()
    S2 = Dataframe_former(inputer)
    S1 = gd(inputer)

    # print(S2.json_dataframe())
    # print(S2.tag_count_from_df())
    print(S2.tags_plot())
                          
    