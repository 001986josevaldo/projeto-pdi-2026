from sklearn.metrics import precision_score, recall_score, f1_score

class Metrics:
    def __init__(self):
        self.y_true = []
        self.y_pred = []

    def add(self, true, pred):
        self.y_true.append(true)
        self.y_pred.append(pred)

    def report(self):
        return {
            "precision": precision_score(self.y_true, self.y_pred),
            "recall": recall_score(self.y_true, self.y_pred),
            "f1": f1_score(self.y_true, self.y_pred)
        }