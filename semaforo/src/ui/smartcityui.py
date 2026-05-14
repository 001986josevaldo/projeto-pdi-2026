import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import sys  
# =========================
# BASE DO PROJETO
# =========================

# ui.py -> sobe dois níveis
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# =========================
# IMPORTS INTERNOS
# =========================

from src.ui.main_menu import MainMenu
from src.ui.dashboard import Dashboard

from src.pipeline.traffic_light import TrafficLightDetector
from src.utils.violelation_monitor import ViolationMonitor
from src.utils.video_converter import VideoConverter

converter = VideoConverter()

class SmartCityUI:

    def __init__(self, root):

        self.root = root

        self.root.title("Smart City Panel")

        self.root.configure(bg="#000000")

        self.root.geometry("1400x850")

        # =========================
        # VARIÁVEIS
        # =========================

        self.cap = None
        self.camera_index = 1

        self.camera_disconnected = False
        self.running = False

        self.current_frame = None
        self.frame_width = 0
        self.frame_height = 0

        self.display_width = 1000
        self.display_height = 700
        self.roi = None

        self.line_points = []

        self.selecting_roi = False

        self.selecting_line = False

        self.start_x = 0
        self.start_y = 0

        self.signal_status = "UNKNOWN"

        self.violations = 0

        self.fps = 0

        self.use_flip = False  # controla se deve espelhar o frame
        self.input_type = None  # webcam ou video
        self.temp_rect_id = None
        self.temp_point_ids = []

        # =========================
        # LAYOUT PRINCIPAL
        # =========================

        self.main_frame = tk.Frame(
            self.root,
            bg="black"
        )

        self.main_frame.pack(
            fill="both",
            expand=True
        )

        # =========================
        # ÁREA VIDEO
        # =========================

        self.video_frame = tk.Frame(
            self.main_frame,
            bg="black"
        )

        self.video_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.canvas = tk.Canvas(
            self.video_frame,
            bg="black",
            width=1000,
            height=700,
            highlightthickness=0
        )

        self.canvas.pack(fill="both", expand=True)

        # eventos mouse
        self.canvas.bind("<Button-1>", self.mouse_down)

        self.canvas.bind("<B1-Motion>", self.mouse_move)

        self.canvas.bind("<ButtonRelease-1>", self.mouse_up)

        # =========================
        # PAINEL DIREITO
        # =========================

        self.sidebar = tk.Frame(
            self.main_frame,
            bg="#050505",
            width=320
        )

        self.sidebar.pack(
            side="right",
            fill="y"
        )

        # =========================
        # TÍTULO
        # =========================

        title = tk.Label(
            self.sidebar,
            text="SMART CITY PANEL",
            fg="#00ff00",
            bg="#050505",
            font=("Consolas", 28, "bold")
        )

        title.pack(pady=30)

        # =========================
        # STATUS SEMÁFORO
        # =========================

        self.signal_label = tk.Label(
            self.sidebar,
            text=f"Sinal: {self.signal_status}",
            fg="white",
            bg="#303030",
            font=("Consolas", 22),
            padx=20,
            pady=10
        )

        self.signal_label.pack(
            fill="x",
            padx=20,
            pady=10
        )

        # =========================
        # VIOLAÇÕES
        # =========================

        self.violations_label = tk.Label(
            self.sidebar,
            text=f"VIOLATIONS: {self.violations}",
            fg="white",
            bg="#050505",
            font=("Consolas", 22)
        )

        self.violations_label.pack(
            anchor="w",
            padx=25,
            pady=20
        )

        # =========================
        # FPS
        # =========================

        self.fps_label = tk.Label(
            self.sidebar,
            text=f"FPS: {self.fps}",
            fg="#00ffff",
            bg="#050505",
            font=("Consolas", 22)
        )

        self.fps_label.pack(
            anchor="w",
            padx=25,
            pady=10
        )

        # =========================
        # EVENTOS
        # =========================

        events_title = tk.Label(
            self.sidebar,
            text="LAST EVENTS:",
            fg="yellow",
            bg="#050505",
            font=("Consolas", 22)
        )

        events_title.pack(
            anchor="w",
            padx=25,
            pady=30
        )

        self.events_box = tk.Text(
            self.sidebar,
            bg="black",
            fg="white",
            height=15,
            font=("Consolas", 12)
        )

        self.events_box.pack(
            fill="both",
            padx=20,
            pady=10,
            expand=True
        )

        # =========================
        # PAINEL INFERIOR
        # =========================

        self.bottom_panel = tk.Frame(
            self.video_frame,
            bg="#050505"
        )

        self.bottom_panel.pack(
            fill="x",
            pady=10
        )

        # =========================
        # CONTROLES
        # =========================

        self.build_controls()

    # ==================================================
    # CONTROLES
    # ==================================================

    def build_controls(self):

        # --------------------------
        # ENTRADA
        # --------------------------

        input_frame = tk.LabelFrame(
            self.bottom_panel,
            text="Entrada",
            bg="#050505",
            fg="white",
            font=("Consolas", 12)
        )

        input_frame.pack(
            side="left",
            padx=10
        )

        self.input_combo = ttk.Combobox(
            input_frame,
            values=["Webcam", "Vídeo"],
            state="readonly",
            width=20
        )

        self.input_combo.current(0)

        self.input_combo.pack(
            padx=10,
            pady=10
        )

        start_btn = tk.Button(
            input_frame,
            text="Iniciar",
            bg="#202020",
            fg="white",
            command=self.start_camera,
            width=12
        )

        start_btn.pack(
            side="left",
            padx=10,
            pady=10
        )

        stop_btn = tk.Button(
            input_frame,
            text="Parar",
            bg="#202020",
            fg="red",
            command=self.stop_camera,
            width=12
        )

        stop_btn.pack(
            side="left",
            padx=10,
            pady=10
        )

        # --------------------------
        # ROI
        # --------------------------

        roi_frame = tk.LabelFrame(
            self.bottom_panel,
            text="ROI - Semáforo",
            bg="#050505",
            fg="white",
            font=("Consolas", 12)
        )

        roi_frame.pack(
            side="left",
            padx=10
        )

        roi_btn = tk.Button(
            roi_frame,
            text="Selecionar ROI",
            command=self.select_roi,
            width=20
        )

        roi_btn.pack(
            padx=10,
            pady=10
        )

        # --------------------------
        # LINHA
        # --------------------------

        line_frame = tk.LabelFrame(
            self.bottom_panel,
            text="Linha de Retenção",
            bg="#050505",
            fg="white",
            font=("Consolas", 12)
        )

        line_frame.pack(
            side="left",
            padx=10
        )

        line_btn = tk.Button(
            line_frame,
            text="Selecionar Linha",
            command=self.select_line,
            width=20
        )

        line_btn.pack(
            padx=10,
            pady=10
        )

        # --------------------------
        # PROCESSAMENTO
        # --------------------------

        process_frame = tk.LabelFrame(
            self.bottom_panel,
            text="Processamento",
            bg="#050505",
            fg="white",
            font=("Consolas", 12)
        )

        process_frame.pack(
            side="left",
            padx=10
        )

        process_btn = tk.Button(
            process_frame,
            text="Iniciar Processamento",
            command=self.start_processing,
            bg="#00aa00",
            fg="white",
            width=22,
            height=2
        )

        process_btn.pack(
            padx=10,
            pady=10
        )
    # ==================================================
    # CAMERA
    # ==================================================

    def start_camera(self):

        opcao = self.input_combo.get().lower()

        print("Entrada selecionada:", opcao)
        # limpa seleção anterior
        self.reset_selections()
        # =========================
        # WEBCAM
        # =========================

        if opcao == "webcam":

            self.cap = cv2.VideoCapture(self.camera_index)

            self.use_flip = True
            self.input_type = "webcam"

        # =========================
        # VIDEO
        # =========================

        elif opcao == "vídeo" or opcao == "video":

            from tkinter import filedialog

            video_path = filedialog.askopenfilename(
                title="Selecione um vídeo",
                filetypes=[
                    ("Vídeos", "*.mp4 *.avi *.mov *.mkv *.webm"),
                    ("Todos", "*.*")
                ]
            )

            if not video_path:
                return

            self.cap = cv2.VideoCapture(video_path)

            self.use_flip = False
            self.input_type = "video"

        # =========================
        # VALIDAÇÃO
        # =========================

        if self.cap is None or not self.cap.isOpened():

            print("Erro ao abrir entrada.")

            return

        self.camera_disconnected = False

        # =========================
        # PRIMEIRO FRAME
        # =========================

        ret, frame = self.cap.read()

        if not ret or frame is None:

            print("Erro ao capturar frame.")

            return

        # espelha webcam
        if self.use_flip:
            frame = cv2.flip(frame, 1)

        self.current_frame = frame.copy()
        self.frame_height, self.frame_width = frame.shape[:2]

        # exibe SOMENTE o primeiro frame
        self.show_frame(frame)

        # NÃO inicia loop ainda
        self.running = False

        return opcao

    def stop_camera(self):

        self.running = False

        if self.cap:
            self.cap.release()


    def canvas_to_frame(self, x, y):

        real_x = int(
            x * self.frame_width / self.display_width
        )

        real_y = int(
            y * self.frame_height / self.display_height
        )

        return real_x, real_y
    
        # ==================================================
    # UPDATE FRAME
    # ==================================================
    def update_frame(self):

        if not self.running:
            return

        ret, frame = self.cap.read()

        # =========================
        # ENTRADA INVALIDA / FIM DE VÍDEO
        # =========================

        if not ret or frame is None:

            if self.input_type == "webcam":

                if not self.camera_disconnected:

                    self.camera_disconnected = True

                    print("⚠️ Webcam desconectada.")

                    self.add_event(
                        "Webcam desconectada"
                    )

                self.show_disconnected_screen()

                self.try_reconnect_camera()

                self.root.after(1000, self.update_frame)

                return

            # fim do vídeo ou entrada inválida em modo vídeo
            self.running = False

            self.add_event(
                "Fim do vídeo"
            )

            print("🚫 Fim do vídeo.")

            # libera vídeo
            if self.cap is not None:
                self.cap.release()
                self.cap = None

            # limpa ROI e linha
            self.reset_selections()

            # limpa frame atual
            self.current_frame = None

            # limpa canvas
            self.canvas.delete("all")

            # mensagem amigável
            self.canvas.create_text(
                500,
                320,
                text="PROCESSAMENTO FINALIZADO",
                fill="white",
                font=("Consolas", 26, "bold")
            )

            self.canvas.create_text(
                500,
                380,
                text="Selecione um novo vídeo",
                fill="yellow",
                font=("Consolas", 18)
            )

            return

        # =========================
        # RECONEXÃO
        # =========================

        if self.camera_disconnected:

            self.camera_disconnected = False

            print("✅ Entrada reconectada.")

            self.add_event(
                "Entrada reconectada"
            )

        if self.use_flip:
            frame = cv2.flip(frame, 1)

        self.current_frame = frame.copy()
        self.frame_height, self.frame_width = frame.shape[:2]

        # desenha ROI
        if self.roi:

            x, y, w, h = self.roi

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (255, 0, 0),
                2
            )

        # desenha linha
        if len(self.line_points) == 2:

            cv2.line(
                frame,
                self.line_points[0],
                self.line_points[1],
                (0, 0, 255),
                3
            )

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        image = Image.fromarray(rgb)

        image = image.resize(
            (
                self.display_width,
                self.display_height
            )
        )

        imgtk = ImageTk.PhotoImage(image=image)

        self.canvas.imgtk = imgtk

        self.canvas.create_image(
            0,
            0,
            anchor="nw",
            image=imgtk
        )

        self.root.after(10, self.update_frame)
    
    def try_reconnect_camera(self):

        try:

            if self.input_type != "webcam":
                return

            if self.cap is not None:
                self.cap.release()

            self.cap = cv2.VideoCapture(
                self.camera_index
            )

        except Exception as e:

            print("Erro reconexão:", e)
    
    def start_processing(self):

        if self.cap is None:
            return

        self.running = True

        self.update_frame()

        print("🚦 Processamento iniciado")
    
    def show_disconnected_screen(self):

        self.canvas.delete("all")

        self.canvas.create_text(
            500,
            300,
            text="WEBCAM DESCONECTADA",
            fill="red",
            font=("Consolas", 28, "bold")
        )

        self.canvas.create_text(
            500,
            360,
            text="Reconecte o dispositivo USB...",
            fill="white",
            font=("Consolas", 18)
        )
    def add_event(self, text):

        self.events_box.insert(
            tk.END,
            f"{text}\n"
        )

        self.events_box.see(tk.END)

    def reset_selections(self):

        # ROI
        self.roi = None

        # linha
        self.line_points = []

        # estados
        self.selecting_roi = False
        self.selecting_line = False

        # temporários
        self.temp_rect_id = None
        self.temp_point_ids = []

        # limpa overlays
        self.canvas.delete("overlay")
        self.canvas.delete("selection")

        self.add_event(
            "ROI e linha resetados"
        )

    def show_frame(self, frame):

        self.canvas.delete("all")

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        image = Image.fromarray(rgb)

        image = image.resize(
            (
                self.display_width,
                self.display_height
            )
        )

        imgtk = ImageTk.PhotoImage(image=image)

        self.canvas.imgtk = imgtk

        self.canvas.create_image(
            0,
            0,
            anchor="nw",
            image=imgtk
        )

        # desenha ROI e linha atuais como camada de overlay
        if self.roi:
            x, y, w, h = self.roi
            self.canvas.create_rectangle(
                x,
                y,
                x + w,
                y + h,
                outline="red",
                width=2,
                tag="overlay"
            )

        if len(self.line_points) == 2:
            self.canvas.create_line(
                self.line_points[0][0],
                self.line_points[0][1],
                self.line_points[1][0],
                self.line_points[1][1],
                fill="lime",
                width=3,
                tag="overlay"
            )

    def select_roi(self):

        if self.current_frame is None:
            self.add_event("Frame não disponível para seleção de ROI")
            return

        self.selecting_roi = True
        self.selecting_line = False
        self.start_x = None
        self.start_y = None
        self.temp_rect_id = None
        self.canvas.delete("selection")
        self.add_event("Clique e arraste para selecionar o ROI")

    def select_line(self):

        if self.current_frame is None:
            self.add_event("Frame não disponível para seleção de linha")
            return

        self.selecting_line = True
        self.selecting_roi = False
        self.line_points = []
        self.canvas.delete("selection")
        self.add_event("Clique em dois pontos para definir a linha")

    # ==================================================
    # ROI
    # ==================================================

    def enable_roi_selection(self):

        self.selecting_roi = True

        self.selecting_line = False
        

    # ==================================================
    # LINHA
    # ==================================================

    def enable_line_selection(self):

        self.selecting_line = True

        self.selecting_roi = False

        self.line_points = []

    # ==================================================
    # MOUSE
    # ==================================================

    def mouse_down(self, event):

        if self.selecting_roi:

            self.start_x = event.x

            self.start_y = event.y

    def mouse_move(self, event):

        if self.selecting_roi and self.start_x is not None and self.start_y is not None:
            self.canvas.delete("selection")
            self.temp_rect_id = self.canvas.create_rectangle(
                self.start_x,
                self.start_y,
                event.x,
                event.y,
                outline="yellow",
                width=2,
                dash=(4, 2),
                tag="selection"
            )

    def mouse_up(self, event):

        if self.selecting_roi and self.start_x is not None and self.start_y is not None:

            cx1 = min(self.start_x, event.x)
            cy1 = min(self.start_y, event.y)
            cx2 = max(self.start_x, event.x)
            cy2 = max(self.start_y, event.y)

            x1, y1 = self.canvas_to_frame(cx1, cy1)
            x2, y2 = self.canvas_to_frame(cx2, cy2)

            self.roi = (
                x1,
                y1,
                x2 - x1,
                y2 - y1
            )

            self.selecting_roi = False
            self.canvas.delete("selection")
            self.add_event("ROI de semáforo selecionado")
            self.show_frame(self.current_frame)

        elif self.selecting_line:

            real_x, real_y = self.canvas_to_frame(
                event.x,
                event.y
            )

            self.line_points.append(
                (real_x, real_y)
            )

            point_id = self.canvas.create_oval(
                event.x - 4,
                event.y - 4,
                event.x + 4,
                event.y + 4,
                fill="yellow",
                outline="yellow",
                tag="selection"
            )
            self.temp_point_ids.append(point_id)

            if len(self.line_points) == 2:
                self.selecting_line = False
                self.canvas.delete("selection")
                self.add_event("Linha de retenção selecionada")
                self.show_frame(self.current_frame)

            elif len(self.line_points) == 1:
                self.add_event("Clique no segundo ponto para completar a linha")


# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = SmartCityUI(root)

    root.mainloop()