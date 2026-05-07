import sys
import os
os.environ["OPENCV_LOG_LEVEL"] = "ERROR"
import glob
# Garante que o Python reconheça a raiz do projeto (projeto-pdi-2026)
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


from src.pipeline.pipeline import PotholePipeline

class SmartCityUI:
    def __init__(self, root):
        self.fps_list = []
        os.makedirs('results', exist_ok=True) # Cria a pasta se não existir
        self.root = root
        self.root.title("Smart City: Monitoramento de Vias (Cenário A - Buracos)")
        self.root.geometry("1200x700")
        self.root.configure(bg="#2c3e50")

        # Variáveis de Fonte de Mídia
        self.cap = None
        self.static_image = None
        self.is_video = True
        self.pipeline = None
        self.cam_sources = []
        self.current_cam_source = None
        self.camera_name = tk.StringVar(value="Nenhuma")

        # Variáveis de Telemetria e Estado
        self.prev_frame_time = 0
        self.new_frame_time = 0
        self.calibration_mode = False

        self.setup_ui()
        
        # Inicia com a Webcam por padrão
        self.camera_manager = CameraManager()
        self.camera_manager.open_default_camera()
        self.update_frame()

        

    def setup_ui(self):
        # --- PAINEL ESQUERDO: Visualização Principal ---
        self.left_panel = tk.Frame(self.root, bg="#34495e", width=800, height=600)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.video_label = tk.Label(self.left_panel, bg="#000000")
        self.video_label.pack(pady=10)

        # Botões de Controle de Mídia e Calibração
        self.control_frame = tk.Frame(self.left_panel, bg="#34495e")
        self.control_frame.pack(fill=tk.X, pady=10)

        # Novos Botões de Fonte de Imagem
        self.btn_webcam = tk.Button(self.control_frame, text="📷 Alternar Webcam", command=self.start_webcam, bg="#16a085", fg="white")
        self.btn_webcam.pack(side=tk.LEFT, padx=5)

        #self.btn_switch_camera = tk.Button(self.control_frame, text="🔄 Alternar Câmera", command=self.switch_camera_ui, bg="#1abc9c", fg="white")
        #self.btn_switch_camera.pack(side=tk.LEFT, padx=5)

        self.btn_file = tk.Button(self.control_frame, text="📁 Carregar Foto/Vídeo", command=self.load_file, bg="#2980b9", fg="white")
        self.btn_file.pack(side=tk.LEFT, padx=5)

        # Botão de Calibração (mantido)
        self.btn_roi = tk.Button(self.control_frame, text="Calibrar ROI", command=self.toggle_calibration, bg="#3498db", fg="white")
        self.btn_roi.pack(side=tk.RIGHT, padx=5)

        # --- PAINEL DIREITO: Dados e Contadores ---
        self.right_panel = tk.Frame(self.root, bg="#2c3e50", width=350)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        self.lbl_fps = tk.Label(self.right_panel, text="FPS: 0", font=("Arial", 16, "bold"), fg="#2ecc71", bg="#2c3e50")
        self.lbl_fps.pack(pady=10)

        #self.lbl_camera = tk.Label(self.right_panel, textvariable=self.camera_name, font=("Arial", 12), fg="white", bg="#2c3e50")
        #self.lbl_camera.pack(pady=4)

        tk.Label(self.right_panel, text="Monitoramento de Severidade", font=("Arial", 14), fg="white", bg="#2c3e50").pack(pady=5)
        self.lbl_pequeno = tk.Label(self.right_panel, text="Pequenos: 0", font=("Arial", 12), fg="#2ecc71", bg="#2c3e50")
        self.lbl_pequeno.pack()
        self.lbl_medio = tk.Label(self.right_panel, text="Médios: 0", font=("Arial", 12), fg="#f1c40f", bg="#2c3e50")
        self.lbl_medio.pack()
        self.lbl_grande = tk.Label(self.right_panel, text="Grandes: 0", font=("Arial", 12), fg="#e74c3c", bg="#2c3e50")
        self.lbl_grande.pack()

        tk.Label(self.right_panel, text="Mapa de Incidência (Heatmap)", font=("Arial", 14), fg="white", bg="#2c3e50").pack(pady=20)
        self.heatmap_label = tk.Label(self.right_panel, bg="#000000")
        self.heatmap_label.pack()

    def start_webcam(self):

        success = self.camera_manager.open_default_camera()

        if success:

            self.is_video = True

            self.static_image = None

            self.camera_name.set(
                self.camera_manager.current_source['name']
            )


    def switch_camera_ui(self):

        success = self.camera_manager.switch_camera()

        if success:

            self.camera_name.set(
                self.camera_manager.current_source['name']
            )



    def load_file(self):
        # Abre o explorador de arquivos
        filepath = filedialog.askopenfilename(
            title="Selecione uma Foto ou Vídeo do Dataset",
            filetypes=[("Imagens e Vídeos", "*.png *.jpg *.jpeg *.mp4 *.avi"), ("Todos os arquivos", "*.*")]
        )
        if not filepath:
            return # O usuário cancelou a seleção

        # Verifica se é imagem ou vídeo pela extensão
        if filepath.lower().endswith(('.png', '.jpg', '.jpeg')):
            if self.cap:
                self.cap.release()
            self.static_image = cv2.imread(filepath)
            self.is_video = False
            self.pipeline = PotholePipeline(self.static_image.shape)
        else:
            if self.cap:
                self.cap.release()
            self.cap = cv2.VideoCapture(filepath)
            self.is_video = True
            self.static_image = None
            ret, frame = self.cap.read()
            if ret:
                self.pipeline = PotholePipeline(frame.shape)

    def toggle_calibration(self):
        self.calibration_mode = not self.calibration_mode
        self.btn_roi.config(bg="#e67e22" if self.calibration_mode else "#3498db")

    def apply_anonymization(self, frame):
        h, w = frame.shape[:2]
        roi_top = frame[0:int(h*0.3), 0:w]
        blurred_top = cv2.GaussianBlur(roi_top, (51, 51), 0)
        frame[0:int(h*0.3), 0:w] = blurred_top
        cv2.putText(frame, "LGPD: Anonimizacao Ativa", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        return frame

    def update_frame(self):
        # 1. Obtendo o Frame (de vídeo/webcam ou da foto estática)
        if self.is_video:
            if not self.camera_manager.is_opened():
                ret = False
                frame = None
            else:
                ret, frame = self.camera_manager.read()
                if ret and frame is not None and self.pipeline is None:
                    self.pipeline = PotholePipeline(frame.shape)

            if not ret or frame is None:
                # TOLERÂNCIA A FALHAS (Cabo desconectado)
                # Cria uma tela preta de aviso
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "Camera Desconectada!", (50, 240), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                cv2.putText(frame, "Tentando reconectar...", (50, 280), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                # Tenta religar a câmera no background
                if self.current_cam_source:
                    self.open_camera_source(self.current_cam_source)
                else:
                    self.camera_manager.open_default_camera()
                
                # Renderiza o aviso e pausa o pipeline
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img_tk = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb).resize((750, 450)))
                self.video_label.imgtk = img_tk
                self.video_label.configure(image=img_tk)
                
                # Aguarda 500ms e tenta o próximo frame
                self.root.after(500, self.update_frame)
                return
        else:
            if self.static_image is None:
                self.root.after(100, self.update_frame)
                return
            # Se for foto, criamos uma cópia para não desenhar retângulos infinitos em cima da mesma matriz
            frame = self.static_image.copy()
            time.sleep(0.03) # Simula um "FPS" para a interface não congelar por processar rápido demais

        if self.pipeline is None:
            self.root.after(10, self.update_frame)
            return

        # 2. Processamento via Pipeline e Anonimização
        results, heatmap_img = self.pipeline.process(frame)
        #frame = self.apply_anonymization(frame)

        # 3. Anotações Visuais
        counts = {"pequeno": 0, "medio": 0, "grande": 0}
        for (x, y, w, h, severity) in results:
            counts[severity] += 1
            color = (0, 0, 255) if severity == "grande" else (0, 255, 255) if severity == "medio" else (0, 255, 0)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, severity.upper(), (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # 4. Atualizando Dados UI
        self.lbl_pequeno.config(text=f"Pequenos: {counts['pequeno']}")
        self.lbl_medio.config(text=f"Médios: {counts['medio']}")
        self.lbl_grande.config(text=f"Grandes: {counts['grande']}")

        self.new_frame_time = time.time()
        fps = 1 / (self.new_frame_time - self.prev_frame_time) if self.prev_frame_time > 0 else 0
        self.prev_frame_time = self.new_frame_time
        
        self.lbl_fps.config(text=f"FPS: {int(fps)}", fg="#2ecc71" if fps >= 20 else "#e74c3c")

        # 5. Renderização (Vídeo e Heatmap)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_tk = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb).resize((750, 450), Image.Resampling.LANCZOS))
        self.video_label.imgtk = img_tk
        self.video_label.configure(image=img_tk)

        heatmap_rgb = cv2.cvtColor(heatmap_img, cv2.COLOR_BGR2RGB)
        hm_tk = ImageTk.PhotoImage(image=Image.fromarray(heatmap_rgb).resize((300, 200), Image.Resampling.LANCZOS))
        self.heatmap_label.imgtk = hm_tk
        self.heatmap_label.configure(image=hm_tk)

        self.root.after(15, self.update_frame)
        # No final do método update_frame(self), logo após calcular o fps:
        if fps > 0 and fps < 1000: # Filtra ruídos de inicialização
            self.fps_list.append(fps)

    def on_closing(self):
        # Salvando log de telemetria
        if len(self.fps_list) > 0:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'results/fps_log_{timestamp}.csv'
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Metrica', 'Valor (FPS)'])
                writer.writerow(['Media', round(statistics.mean(self.fps_list), 2)])
                writer.writerow(['Desvio-Padrao', round(statistics.stdev(self.fps_list) if len(self.fps_list) > 1 else 0, 2)])
                writer.writerow(['Minimo', round(min(self.fps_list), 2)])
                writer.writerow(['Maximo', round(max(self.fps_list), 2)])
            print(f"Log de FPS salvo em {filename}")

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