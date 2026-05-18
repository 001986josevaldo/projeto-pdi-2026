import os
import csv
import datetime


class DataLogger:

    def __init__(self, output_dir="results"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def salvar_dados(self, results):

        if not results:
            print("Nenhum dado para salvar.")
            return

        timestamp_arquivo = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        os.makedirs(self.output_dir, exist_ok=True)

        filename = os.path.join(
            self.output_dir,
            f"event_log_{timestamp_arquivo}.csv"
        )

        with open(filename, mode='w', newline='', encoding='utf-8') as file:

            writer = csv.writer(file)

            # Cabeçalho
            writer.writerow([
                "timestamp",
                "tipo",
                "severidade",
                "x",
                "y",
                "largura",
                "altura"
            ])

            # Timestamp das detecções
            timestamp_dados = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for (x, y, w, h, severity) in results:

                writer.writerow([
                    timestamp_dados,
                    "buraco",
                    severity,
                    x,
                    y,
                    w,
                    h
                ])

        print(f"Dados salvos em: {filename}")