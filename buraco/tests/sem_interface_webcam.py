import sys
import os
import cv2
import time
import datetime
import csv
import statistics

# Garante que o Python reconheça a raiz do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from buraco.src.pipeline.pipeline import PotholePipeline

def evaluate_pipeline_webcam():
    print("Iniciando avaliação de desempenho com a Logitech C930e...")
    
    # ---------------------------------------------------------
    # CONFIGURAÇÕES DEFINITIVAS DE HARDWARE (Mapeado do Guvcview)
    # ---------------------------------------------------------
    print("Aplicando configurações de hardware via V4L2...")
    
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

    # Agora sim, o OpenCV assume a câmera já configurada
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2) 
    
    # Reforça no OpenCV
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    ret, frame = cap.read()
    if not ret:
        print("Erro: Não foi possível acessar a Webcam no /dev/video2.")
        return

    # IMPORTANTE: Descomentei o resize aqui para o pipeline receber a dimensão certa (16:9)
    frame = cv2.resize(frame, (640, 360))
    pipeline = PotholePipeline(frame.shape)
    
    fps_list = []
    frame_count = 0
    
    # Variáveis para a exibição do FPS a cada 1 segundo
    last_fps_time = time.perf_counter()
    frames_this_second = 0
    fps_display = 0.0
    
    print("Pressione 'Q' na janela de vídeo para encerrar e gerar o relatório.")

    # Inicia a contagem de tempo total
    start_total_time = time.perf_counter()

    while True:
        # Pega o tempo no exato início do ciclo (Para o relatório de benchmark)
        start_frame_time = time.perf_counter()
        
        ret, frame = cap.read()
        if not ret:
            print("Falha na leitura do frame da webcam.")
            break
            
        # IMPORTANTE: A câmera captura 640x480 (4:3), mas sua UI/Pipeline
        # provavelmente usa 640x360 (16:9). É vital redimensionar para evitar erro no processamento.
        frame = cv2.resize(frame, (640, 360))
        
        # --- 1. PROCESSAMENTO PURO ---
        results, heatmap_img = pipeline.process(frame)
        
        # --- 2. ANOTAÇÕES VISUAIS ---
        
        for (x, y, w, h, severity) in results:
            color = (0, 0, 255) if severity == "grande" else (0, 255, 255) if severity == "medio" else (0, 255, 0)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, severity.upper(), (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # --- 3. LÓGICA DO FPS EM TELA ---
        frames_this_second += 1
        current_time = time.perf_counter()
        elapsed_since_last_sec = current_time - last_fps_time
        
        if elapsed_since_last_sec >= 1.0:
            fps_display = frames_this_second / elapsed_since_last_sec
            frames_this_second = 0
            last_fps_time = current_time

        # CÁLCULO DO FPS MÉDIO 
        tempo_corrido = current_time - start_total_time
        fps_medio = frame_count / tempo_corrido if tempo_corrido > 0 else 0
            
        fps_color = (0, 255, 0) if fps_display >= 20 else (0, 0, 255)

        cv2.putText(frame, f"FPS Atual: {int(fps_display)}", (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 1.0, fps_color, 2)
        #cv2.putText(frame, f"FPS Medio: {int(fps_medio)}", (15, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        
        # --- 4. EXIBIÇÃO EM TELA ---
        cv2.imshow("Avaliacao de Desempenho - Deteccoes", frame)
            
        # --- 5. CÁLCULO DE FPS DO CICLO (Para o CSV) ---
        end_frame_time = time.perf_counter()
        elapsed = end_frame_time - start_frame_time
        
        if elapsed > 0:
            current_fps = 1.0 / elapsed
            fps_list.append(current_fps)
            
        frame_count += 1
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    end_total_time = time.perf_counter()
    
    cap.release()
    cv2.destroyAllWindows()
    
    # --- GERAÇÃO DE RELATÓRIO ---
    if len(fps_list) > 0:
        media_fps = round(statistics.mean(fps_list), 2)
        desvio = round(statistics.stdev(fps_list) if len(fps_list) > 1 else 0, 2)
        tempo_total = round(end_total_time - start_total_time, 2)
        
        print("\n" + "="*40)
        print("📊 RESULTADOS DA AVALIAÇÃO DE DESEMPENHO")
        print("="*40)
        print(f"Total de frames processados: {frame_count}")
        print(f"Tempo total de execução:     {tempo_total} segundos")
        print(f"FPS Médio do Sistema:        {media_fps} FPS")
        print(f"Desvio-Padrão:               {desvio} FPS")
        print(f"FPS Mínimo:                  {round(min(fps_list), 2)}")
        print(f"FPS Máximo:                  {round(max(fps_list), 2)}")
        print("="*40)
        
        os.makedirs('results', exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'results/webcam_benchmark_{timestamp}.csv'
        
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Metrica', 'Valor'])
            writer.writerow(['Total de Frames', frame_count])
            writer.writerow(['Tempo Total (s)', tempo_total])
            writer.writerow(['Media FPS', media_fps])
            writer.writerow(['Desvio-Padrao', desvio])
            writer.writerow(['Minimo FPS', round(min(fps_list), 2)])
            writer.writerow(['Maximo FPS', round(max(fps_list), 2)])
            
        print(f"📁 Relatório salvo em: {filename}")
    else:
        print("Nenhum frame processado. Relatório não gerado.")

if __name__ == "__main__":
    evaluate_pipeline_webcam()