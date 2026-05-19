# webcam_config.py
import os
import cv2

class WebcamConfigurator:
    def __init__(self, device_index=2):
        self.device_index = device_index

    def apply_v4l2_settings(self):
        """Aplica otimizações diretamente no driver V4L2 do Linux."""
        device_path = f"/dev/video{self.device_index}"
        print(f"[V4L2] Aplicando otimizações em {device_path}...")
        try:
            os.system(f"v4l2-ctl -d {device_path} -v width=640,height=480,pixelformat=MJPG")
            os.system(f"v4l2-ctl -d {device_path} -p 30")
            os.system(f"v4l2-ctl -d {device_path} -c exposure_auto_priority=0 > /dev/null 2>&1")
            os.system(f"v4l2-ctl -d {device_path} -c exposure_dynamic_framerate=0 > /dev/null 2>&1")
            os.system(f"v4l2-ctl -d {device_path} -c exposure_auto=1 > /dev/null 2>&1")
            os.system(f"v4l2-ctl -d {device_path} -c exposure_absolute=312 > /dev/null 2>&1")
            print(f"[V4L2] Configurações aplicadas com sucesso em {device_path}")
        except Exception as e:
            print(f"[V4L2] Erro ao configurar {device_path}: {e}")

    def setup_camera_properties(self, cap):
        """Configura as propriedades nativas do OpenCV para o VideoCapture."""
        if cap and cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            cap.set(cv2.CAP_PROP_FPS, 30)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            return True
        return False