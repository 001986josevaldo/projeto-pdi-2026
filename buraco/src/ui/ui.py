# ui.py
import sys
import os
os.environ["OPENCV_LOG_LEVEL"] = "ERROR"
import glob

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import cv2
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import time
import datetime
import numpy as np
import csv
import statistics
from src.devices.camera_manager import CameraManager
from src.devices.webcam_config import WebcamConfigurator
from src.pipeline.pipeline import PotholePipeline
from src.utils.data_logger import DataLogger


# ─────────────────────────────────────────────
# CONFIGURAÇÃO GLOBAL: apenas a Webcam 
FIXED_CAM_INDEX = 2
# ─────────────────────────────────────────────

class SmartCityUI:
    def __init__(self, root):
        self.fps_list = []
        self.fps_buffer = []
        os.makedirs('results', exist_ok=True)
        self.root = root
        self.root.title("Smart City: Monitoramento de Vias (Cenário A - Buracos)")
        self.root.geometry("1200x700")
        self.root.configure(bg="#2c3e50")

        self.cap = None
        self.static_image = None
        self.is_video = True
        self.pipeline = None
        self.cam_sources = []
        self.current_cam_source = None
        self.camera_name = tk.StringVar(value="Webcam 2")

        self.prev_frame_time = None
        self.calibration_mode = False
        self.last_heatmap_tk = None
        self.frame_counter = 0
        self.last_results = []
        self.last_heatmap_img = None
        self.PIPELINE_SKIP = 2

        self.setup_ui()

        self.data_logger = DataLogger()

        # ── Instancia a classe de configuração externa ──
        self.current_device_index = FIXED_CAM_INDEX
        self.webcam_config = WebcamConfigurator(device_index=self.current_device_index)
        self.webcam_config.apply_v4l2_settings()

        self.camera_manager = CameraManager()
        self._open_fixed_camera()   # ← abre diretamente a câmera 2

        self.update_frame()

    def _open_fixed_camera(self):
        """Abre exclusivamente a webcam de índice FIXED_CAM_INDEX."""
        self.camera_manager.release()  # garante que não há câmera aberta

        cap = cv2.VideoCapture(FIXED_CAM_INDEX, cv2.CAP_V4L2)
        if not cap.isOpened():
            print(f"[ERRO] Não foi possível abrir a câmera no índice {FIXED_CAM_INDEX}.")
            self.camera_name.set("Nenhuma")
            return

        # Injeta o VideoCapture diretamente no CameraManager
        self.camera_manager.cap = cap
        self.camera_manager.current_source = {
            'index': FIXED_CAM_INDEX,
            'name': f'Webcam {FIXED_CAM_INDEX}'
        }

        # Usa a classe externa para aplicar as propriedades do OpenCV
        self.webcam_config.setup_camera_properties(cap)

        self.current_cam_source = self.camera_manager.current_source
        self.current_device_index = FIXED_CAM_INDEX
        self.camera_name.set(f'Webcam {FIXED_CAM_INDEX}')
        print(f"[CAM] Webcam {FIXED_CAM_INDEX} aberta com sucesso.")

    def setup_ui(self):
        self.left_panel = tk.Frame(self.root, bg="#34495e", width=640, height=480)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.video_label = tk.Label(self.left_panel, bg="#000000")
        self.video_label.pack(pady=10)

        self.control_frame = tk.Frame(self.left_panel, bg="#34495e")
        self.control_frame.pack(fill=tk.X, pady=10)

        self.btn_webcam = tk.Button(
            self.control_frame, text="📷 Webcam ",
            command=self.start_webcam, bg="#16a085", fg="white"
        )
        self.btn_webcam.pack(side=tk.LEFT, padx=5)

        self.btn_file = tk.Button(
            self.control_frame, text="📁 Carregar Foto/Vídeo",
            command=self.load_file, bg="#2980b9", fg="white"
        )
        self.btn_file.pack(side=tk.LEFT, padx=5)

        self.btn_salvar = tk.Button(
            self.control_frame, text="Salvar",
            command=self.salvar_dados, bg="#3498db", fg="white"
        )
        self.btn_salvar.pack(side=tk.RIGHT, padx=5)

        self.right_panel = tk.Frame(self.root, bg="#2c3e50", width=350)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        self.lbl_fps = tk.Label(
            self.right_panel, text="FPS: --",
            font=("Arial", 16, "bold"), fg="#2ecc71", bg="#2c3e50"
        )
        self.lbl_fps.pack(pady=10)

        tk.Label(self.right_panel, text="Monitoramento de Severidade",
                 font=("Arial", 14), fg="white", bg="#2c3e50").pack(pady=5)
        self.lbl_pequeno = tk.Label(self.right_panel, text="Pequenos: 0",
                                    font=("Arial", 12), fg="#2ecc71", bg="#2c3e50")
        self.lbl_pequeno.pack()
        self.lbl_medio = tk.Label(self.right_panel, text="Médios: 0",
                                  font=("Arial", 12), fg="#f1c40f", bg="#2c3e50")
        self.lbl_medio.pack()
        self.lbl_grande = tk.Label(self.right_panel, text="Grandes: 0",
                                   font=("Arial", 12), fg="#e74c3c", bg="#2c3e50")
        self.lbl_grande.pack()

        tk.Label(self.right_panel, text="Mapa de Incidência (Heatmap)",
                 font=("Arial", 14), fg="white", bg="#2c3e50").pack(pady=20)
        
        self.placeholder_img = ImageTk.PhotoImage(Image.new("RGB", (320, 240), "#000000"))
        
        self.heatmap_label = tk.Label(
            self.right_panel,
            bg="#000000",
            image=self.placeholder_img
        )
        self.heatmap_label.pack()

    def start_webcam(self):
        """Reabre a webcam 2 (sem alternância entre câmeras)."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None

        self._open_fixed_camera()

        if self.camera_manager.is_opened():
            # Substituído pela chamada do gerenciador externo
            self.webcam_config.apply_v4l2_settings()
            self.is_video = True
            self.static_image = None
            self.prev_frame_time = None
            self.fps_buffer = []
            self.fps_list = []
            self.lbl_fps.config(text="FPS: --", fg="#2ecc71")
        else:
            self.camera_name.set("Nenhuma")
            self.lbl_fps.config(text="FPS: N/A", fg="#e74c3c")

    def load_file(self):
        filepath = filedialog.askopenfilename(
            title="Selecione uma Foto ou Vídeo do Dataset",
            filetypes=[("Imagens e Vídeos", "*.png *.jpg *.jpeg *.mp4 *.avi"),
                       ("Todos os arquivos", "*.*")]
        )
        if not filepath:
            return

        self.last_heatmap_img = None
        self.last_heatmap_tk = None

        if filepath.lower().endswith(('.png', '.jpg', '.jpeg')):
            self.lbl_fps.config(text="FPS: N/A", fg="#7f8c8d")
            self.camera_manager.release()
            self.current_cam_source = None
            self.is_video = False
            self.cap = None
            
            raw_img = cv2.imread(filepath)
            self.camera_name.set("Foto carregada")
            
            if raw_img is not None:
                self.static_image = cv2.resize(raw_img, (640, 480))
                self.pipeline = PotholePipeline(self.static_image.shape)
        else:
            if self.cap:
                self.cap.release()
            self.camera_manager.release()
            self.current_cam_source = None
            self.cap = cv2.VideoCapture(filepath)
            self.is_video = True
            self.static_image = None
            self.prev_frame_time = None
            self.lbl_fps.config(text="FPS: --", fg="#2ecc71")
            ret, frame = self.cap.read()
            if ret:
                self.pipeline = PotholePipeline(frame.shape)

    def salvar_dados(self):
        self.data_logger.salvar_dados(self.last_results)

    def apply_anonymization(self, frame):
        h, w = frame.shape[:2]
        roi_top = frame[0:int(h * 0.3), 0:w]
        blurred_top = cv2.GaussianBlur(roi_top, (51, 51), 0)
        frame[0:int(h * 0.3), 0:w] = blurred_top
        cv2.putText(frame, "LGPD: Anonimizacao Ativa", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        return frame

    def update_frame(self):
        current_time = time.perf_counter()
        if self.is_video and self.prev_frame_time is not None:
            elapsed = current_time - self.prev_frame_time
            if elapsed > 0:
                fps = 1.0 / elapsed
                self.fps_buffer.append(fps)
                if len(self.fps_buffer) > 30:
                    self.fps_buffer.pop(0)
                avg_fps = sum(self.fps_buffer) / len(self.fps_buffer)
                cor = "#2ecc71" if avg_fps >= 20 else "#e74c3c"
                self.lbl_fps.config(text=f"FPS: {int(avg_fps)}", fg=cor)
                self.fps_list.append(avg_fps)
                if len(self.fps_list) > 600:
                    self.fps_list.pop(0)
        self.prev_frame_time = current_time

        if self.is_video:
            if self.cap is not None:
                ret, frame = self.cap.read()
                if ret and frame is not None and self.pipeline is None:
                    self.pipeline = PotholePipeline(frame.shape)
            else:
                if not self.camera_manager.is_opened():
                    ret, frame = False, None
                else:
                    ret, frame = self.camera_manager.read()
                    if ret and frame is not None and self.pipeline is None:
                        self.pipeline = PotholePipeline(frame.shape)

            if not ret or frame is None:
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "Camera Desconectada!", (50, 220),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                cv2.putText(frame, "Tentando reconectar...", (50, 270),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                # Substituído pelo gerenciador externo no fluxo de reconexão
                self.webcam_config.apply_v4l2_settings()
                if self.current_cam_source:
                    self._open_fixed_camera()
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img_tk = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))
                self.video_label.imgtk = img_tk
                self.video_label.configure(image=img_tk)
                self.root.after(500, self.update_frame)
                return
        else:
            if self.static_image is None:
                self.root.after(200, self.update_frame)
                return
            frame = self.static_image.copy()
            if self.pipeline is None:
                self.pipeline = PotholePipeline(frame.shape)

        if self.pipeline is None:
            self.root.after(15, self.update_frame)
            return

        self.frame_counter += 1
        run_pipeline = (self.frame_counter % self.PIPELINE_SKIP == 0)

        heatmap_img = None
        if run_pipeline:
            try:
                results, heatmap_img = self.pipeline.process(frame)
                self.last_results = results
            except Exception:
                import traceback
                traceback.print_exc()
                results = self.last_results
        else:
            results = self.last_results

        counts = {"pequeno": 0, "medio": 0, "grande": 0}
        for (x, y, w, h, severity) in results:
            if severity in counts:
                counts[severity] += 1
            color = (0, 0, 255) if severity == "grande" else \
                    (0, 255, 255) if severity == "medio" else (0, 255, 0)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, severity.upper(), (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        if run_pipeline:
            self.lbl_pequeno.config(text=f"Pequenos: {counts['pequeno']}")
            self.lbl_medio.config(text=f"Médios: {counts['medio']}")
            self.lbl_grande.config(text=f"Grandes: {counts['grande']}")

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_tk = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))
        self.video_label.imgtk = img_tk
        self.video_label.configure(image=img_tk)

        if heatmap_img is not None:
            self.last_heatmap_img = heatmap_img

            heatmap_rgb = cv2.cvtColor(heatmap_img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(heatmap_rgb)
            pil_img = pil_img.resize((320, 240), Image.Resampling.LANCZOS)

            hm_tk = ImageTk.PhotoImage(pil_img)
            self.last_heatmap_tk = hm_tk
            self.heatmap_label.imgtk = hm_tk
            self.heatmap_label.configure(image=hm_tk)

        elif self.last_heatmap_img is None:
            placeholder = np.zeros((240, 320, 3), dtype=np.uint8)
            self.last_heatmap_img = placeholder
            hm_tk = ImageTk.PhotoImage(image=Image.fromarray(placeholder))
            self.heatmap_label.imgtk = hm_tk
            self.heatmap_label.configure(image=hm_tk)

        if self.is_video:
            self.root.after(1, self.update_frame)
        else:
            self.root.after(200, self.update_frame)

    def on_closing(self):
        if len(self.fps_list) > 0:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'results/fps_log_{timestamp}.csv'
            try:
                with open(filename, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Metrica', 'Valor (FPS)'])
                    media_fps = round(statistics.mean(self.fps_list), 2)
                    writer.writerow(['Media', media_fps])
                    writer.writerow(['Resultado', 'APROVADO' if media_fps >= 20 else 'REPROVADO'])
                    writer.writerow(['Desvio-Padrao', round(
                        statistics.stdev(self.fps_list) if len(self.fps_list) > 1 else 0, 2)])
                    writer.writerow(['Minimo', round(min(self.fps_list), 2)])
                    writer.writerow(['Maximo', round(max(self.fps_list), 2)])
                print(f"Log de FPS salvo em: {filename}")
            except Exception as e:
                print(f"Erro ao salvar arquivo de log: {e}")

        self.camera_manager.release()
        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartCityUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()