import csv
import os
from datetime import datetime


class EventLogger:

    def __init__(self, file_path="logs/events.csv"):

        os.makedirs("logs", exist_ok=True)

        self.file_path = file_path

        if not os.path.exists(file_path):

            with open(file_path, "w", newline="") as f:

                writer = csv.writer(f)

                writer.writerow([
                    "timestamp",
                    "tipo",
                    "estado",
                    "coordenada"
                ])

    def log(self, tipo, estado, coordenada):

        with open(self.file_path, "a", newline="") as f:

            writer = csv.writer(f)

            writer.writerow([
                datetime.now(),
                tipo,
                estado,
                coordenada
            ])