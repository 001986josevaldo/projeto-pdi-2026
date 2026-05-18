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

def evaluate_pipeline_video(video_path):
    print(f"Iniciando avaliação de desempenho no vídeo: {video_path}")
    
    # Carrega o vídeo a partir do caminho fornecido
    cap = cv2.VideoCapture(video_path) 
    
    ret, frame = cap.read()
    if not ret:
        print(f"Erro: Não foi possível acessar o arquivo de vídeo: {video_path}")
        print("Verifique se o caminho está correto e tente novamente.")
        return

    # Redimensiona o primeiro frame para criar a base do pipeline
    frame = cv2.resize(frame, (640, 360))
    pipeline = PotholePipeline(frame.shape)
    
    fps_list = []
    frame_count = 0
    
    # Variáveis para a exibição do FPS a cada 1 segundo
    last_fps_time = time.perf_counter()
    frames_this_second = 0
    fps_display = 0.0
    
    print("Processando na velocidade máxima do processador...")
    print("Pressione 'Q' na janela de vídeo para encerrar precocemente e gerar o relatório.")

    # Inicia a contagem de tempo total
    start_total_time = time.perf_counter()

    while True:
        # Pega o tempo no exato início do ciclo
        start_frame_time = time.perf_counter()
        
        ret, frame = cap.read()
        if not ret:
            print("Fim do vídeo alcançado. Encerrando e gerando relatório...")
            break
            
        frame = cv2.resize(frame, (640, 360))
        
        # --- 1. PROCESSAMENTO PURO ---
        results, heatmap_img = pipeline.process(frame)
        
        # --- 2. ANOTAÇÕES VISUAIS ---
        for (x, y, w, h, severity) in results:
            color = (0, 0, 255) if severity == "grande" else (0, 255, 255) if severity == "medio" else (0, 255, 0)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, severity.upper(), (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # --- 3. LÓGICA DO FPS EM TELA (A CADA 1 SEGUNDO) ---
        frames_this_second += 1
        current_time = time.perf_counter()
        elapsed_since_last_sec = current_time - last_fps_time
        
        if elapsed_since_last_sec >= 1.0:
            fps_display = frames_this_second / elapsed_since_last_sec
            frames_this_second = 0
            last_fps_time = current_time
            
        fps_color = (0, 255, 0) if fps_display >= 20 else (0, 0, 255)
        
        cv2.putText(
            frame, 
            f"FPS: {int(fps_display)}", 
            (15, 35), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1.0, 
            fps_color, 
            3
        )
        
        # --- 4. EXIBIÇÃO EM TELA ---
        cv2.imshow("Avaliacao de Desempenho - Video", frame)
        
        if heatmap_img is not None:
            cv2.imshow("Avaliacao de Desempenho - Heatmap", heatmap_img)
            
        # --- 5. CÁLCULO DE FPS DO CICLO (Para o Relatório) ---
        end_frame_time = time.perf_counter()
        elapsed = end_frame_time - start_frame_time
        
        if elapsed > 0:
            current_fps = 1.0 / elapsed
            fps_list.append(current_fps)
            
        frame_count += 1
        
        # waitKey(1) avança o frame em 1 milissegundo, destravando o gargalo de tempo
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    end_total_time = time.perf_counter()
    
    # Limpa os recursos
    cap.release()
    cv2.destroyAllWindows()
    
    # --- GERAÇÃO DE RELATÓRIO ---
    if len(fps_list) > 0:
        media_fps = round(statistics.mean(fps_list), 2)
        desvio = round(statistics.stdev(fps_list) if len(fps_list) > 1 else 0, 2)
        tempo_total = round(end_total_time - start_total_time, 2)
        
        print("\n" + "="*40)
        print("📊 RESULTADOS DA AVALIAÇÃO DE DESEMPENHO (VÍDEO)")
        print("="*40)
        print(f"Total de frames processados: {frame_count}")
        print(f"Tempo total de processamento: {tempo_total} segundos")
        print(f"FPS Médio do Sistema:        {media_fps} FPS")
        print(f"Desvio-Padrão:               {desvio} FPS")
        print(f"FPS Mínimo:                  {round(min(fps_list), 2)}")
        print(f"FPS Máximo:                  {round(max(fps_list), 2)}")
        print("="*40)
        
        os.makedirs('results', exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'results/video_benchmark_{timestamp}.csv'
        
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
    # COLOQUE O CAMINHO DO SEU VÍDEO AQUI
    # Exemplo: "C:/Users/seu_usuario/projeto-pdi-2026/dataset/video_buracos.mp4"
    caminho_do_video = "/media/josevaldo/E02A-3159/BCC/8_sem/PI/projeto_integrador/projeto-pdi-2026/buraco/assets/samples/images/buraco.mp4" 
    
    evaluate_pipeline_video(caminho_do_video)