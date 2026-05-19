import cv2
import os
import time

def testar_camera_integrada():
    device_index = 0
    device_path = f"/dev/video{device_index}"

    largura = 640
    altura = 480
    fps_desejado = 30

    print("-" * 60)
    print("1. Inicializando webcam com OpenCV + V4L2...")
    print("-" * 60)

    cap = cv2.VideoCapture(device_index, cv2.CAP_V4L2)

    if not cap.isOpened():
        print(f"[ERRO] Não foi possível abrir a câmera em {device_path}")
        return

    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, largura)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, altura)
    cap.set(cv2.CAP_PROP_FPS, fps_desejado)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    print("2. Aplicando controles V4L2...")

    print("2. Aplicando patches V4L2 (Baseado na Imagem 3 do Guvcview)...")
    
    # 1. Força resolução e formato
    os.system("v4l2-ctl -d /dev/video2 -v width=640,height=480,pixelformat=MJPG")
    os.system("v4l2-ctl -d /dev/video2 -p 30")
    
    # 2. Desativa a "Taxa de quadros dinâmicos" (A caixinha desmarcada)
    # Isso impede a câmera de derrubar o FPS quando o ambiente escurece
    os.system("v4l2-ctl -d /dev/video2 -c exposure_auto_priority=0")
    
    # 3. Define "Exposição Automática" para Modo Manual (1)
    os.system("v4l2-ctl -d /dev/video2 -c exposure_auto=1")
    
    # 4. Define o "Tempo de exposição, absoluto" exatamente para 312
    os.system("v4l2-ctl -d /dev/video2 -c exposure_absolute=312")
    # ---------------------------------------------------------


    real_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    real_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    real_fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"\n[SUCESSO] Câmera aberta: {int(real_w)}x{int(real_h)} @ {real_fps:.2f} fps")
    print("-> Pressione 'q' para encerrar.\n")

    prev_time = time.perf_counter()
    fps_buffer = []

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("[AVISO] Falha ao ler frame do hardware.")
            break

        current_time = time.perf_counter()
        elapsed = current_time - prev_time
        prev_time = current_time

        if elapsed > 0:
            fps = 1.0 / elapsed
            fps_buffer.append(fps)
            if len(fps_buffer) > 30:
                fps_buffer.pop(0)
            avg_fps = sum(fps_buffer) / len(fps_buffer)
        else:
            avg_fps = 0

        cor = (0, 255, 0) if avg_fps >= 28 else (0, 0, 255)
        cv2.putText(
            frame,
            f"FPS Real: {avg_fps:.2f}",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            cor,
            2,
            cv2.LINE_AA
        )
        cv2.putText(
            frame,
            f"{int(real_w)}x{int(real_h)} MJPG",
            (20, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0),
            2,
            cv2.LINE_AA
        )

        cv2.imshow("Teste FPS - Webcam Integrada", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("-" * 60)
    print("Fechando a câmera...")
    cap.release()
    cv2.destroyAllWindows()
    print("[FIM] Teste concluído.")
    print("-" * 60)

if __name__ == "__main__":
    testar_camera_integrada()