import cv2
import time

def teste_camera_pura():
    print("Iniciando Teste da Câmera Nua...")
    cap = cv2.VideoCapture(0)
    
    # Tentativa de forçar desempenho
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    last_time = time.perf_counter()
    frames = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frames += 1
        current_time = time.perf_counter()
        
        # A cada 1 segundo, imprime o FPS real de captura
        if current_time - last_time >= 1.0:
            print(f"FPS Físico da Câmera: {frames}")
            frames = 0
            last_time = current_time

        cv2.imshow("Teste de Camera Pura", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    teste_camera_pura()