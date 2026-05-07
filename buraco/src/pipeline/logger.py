import csv
from datetime import datetime

class Logger:
    def __init__(self, file="log.csv"):
        self.file = file

    def log(self, tipo, severidade, coord):
        with open(self.file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), tipo, severidade, coord])