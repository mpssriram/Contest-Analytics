from backend.ml import model_pipeline as ML_pp

class Evaluation:

    def __init__(self, handle=None, threshold=0.5, y_prob=None, y_true=None):
        if handle is not None:
            self.pipeline = ML_pp.ModelPipeline(handle=handle)
            self.model, self.y_prob, self.y_validation = self.pipeline.model_trainning()
            self.X_train, self.Y_train, self.X_validation, self.Y_validation, self.X_test, self.y = (self.pipeline.train_test_split())
        else:
            self.y_prob = y_prob
            self.y_validation = y_true
        self.threshold = threshold

    def model_calculations(self):
        y_prob = []
        for i in range(len(self.y_prob)):
            if self.y_prob[i] >= self.threshold:
                y_prob.append(1)
            else:
                y_prob.append(0)
        TP = 0
        TN = 0
        FP = 0
        FN = 0

        for i in zip(y_prob,self.y_validation):
            if i[0] == 1 and i[1] == 1:
                TP += 1
            elif i[0] == 0 and i[1] == 0:
                TN += 1
            elif i[0] == 1 and i[1] == 0:
                FP += 1
            elif i[0] == 0 and i[1] == 1:
                FN += 1

        return TP,TN,FP,FN
            

        
    def metrics(self):
        TP,TN,FP,FN = self.model_calculations()
        accuracy = (TP+TN)/(TP+TN+FP+FN) if (TP+TN+FP+FN) != 0 else 0
        precision = TP/(TP+FP) if (TP+FP) != 0 else 0
        recall = TP/(TP+FN) if (TP+FN) != 0 else 0  
        f1_score = 2*(precision*recall)/(precision+recall) if (precision+recall) != 0 else 0
        Specificity = TN / (TN + FP) if (TN + FP) != 0 else 0
        balanced_accuracy = (recall + Specificity) / 2

        return accuracy,precision,recall,f1_score,Specificity,balanced_accuracy

if __name__ == "__main__":
    handle = input("Enter the handle of the user: ")

    evaluation = Evaluation(handle=handle,threshold=0.5)

    TP, TN, FP, FN = evaluation.model_calculations()

    print("TP:", TP)
    print("TN:", TN)
    print("FP:", FP)
    print("FN:", FN)

    print("Total validation samples:", TP + TN + FP + FN)
    print("Metrics:", evaluation.metrics())

    print("Minimum probability:", min(evaluation.y_prob))
    print("Maximum probability:", max(evaluation.y_prob))

        # Step 1: sorted validation probabilities
    y_val = evaluation.Y_validation.values

    pairs = []
    for i in range(len(evaluation.y_prob)):
        pairs.append((evaluation.y_prob[i], y_val[i]))

    pairs.sort()

    print("Sorted validation probabilities:")
    for i in pairs:
        if i[1] == 0:
            print(i[0], i[1], "UNSOLVED")
        else:
            print(i[0], i[1])

    # Step 2: threshold sweep
    thresholds = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]

    print("threshold, TP, TN, FP, FN, precision, recall, f1, specificity, balanced_accuracy")
    for t in thresholds:
        evaluation.threshold = t
        TP, TN, FP, FN = evaluation.model_calculations()
        accuracy, precision, recall, f1_score, Specificity, balanced_accuracy = evaluation.metrics()
        print(t, TP, TN, FP, FN, precision, recall, f1_score, Specificity, balanced_accuracy)


    # Step 3: full rows of the unsolved validation problems
    split_index = len(evaluation.X_train)

    print("Unsolved validation problems:")
    for i in range(len(y_val)):
        if y_val[i] == 0:
            print("----------")
            print("probability:", evaluation.y_prob[i])
            print("status check:", evaluation.pipeline.y.iloc[split_index + i])
            print(evaluation.pipeline.features.iloc[split_index + i])

    print(evaluation.pipeline.features.index[:10])
    print(evaluation.pipeline.features["firstTriedAt"].is_monotonic_increasing)

    count = 0
    for r in evaluation.pipeline.features["user_rating_at_time"]:
        if r == 0:
            count += 1
    print("rows with user_rating_at_time = 0:", count)

    solved_count = 0
    unsolved_count = 0
    for r, s in zip(evaluation.pipeline.features["user_rating_at_time"], evaluation.pipeline.features["status"]):
        if r == 0:
            if s == 1:
                solved_count += 1
            else:
                unsolved_count += 1
    print("rating 0 rows -> solved:", solved_count, "unsolved:", unsolved_count)
    print("first row user_rating_at_time:", evaluation.pipeline.features["user_rating_at_time"][0])

    print("TEST RESULT")
    y_prob_test, Y_test = evaluation.pipeline.test_probabilities()
    evaluation.y_prob = y_prob_test
    evaluation.y_validation = Y_test
    evaluation.threshold = 0.85
    print(evaluation.model_calculations())
    print(evaluation.metrics())

        