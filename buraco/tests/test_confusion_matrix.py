import cv2
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
import xml.etree.ElementTree as ET
from buraco.src.pipeline.pipeline import PotholePipeline

def load_ground_truth(annotations_folder, images_folder):
    ground_truth = {}
    for filename in os.listdir(images_folder):
        if filename.endswith(('.png', '.jpg')):
            xml_file = os.path.join(annotations_folder, filename.replace('.png', '.xml').replace('.jpg', '.xml'))
            if os.path.exists(xml_file):
                tree = ET.parse(xml_file)
                root = tree.getroot()
                size = root.find('size')
                width = int(size.find('width').text)
                height = int(size.find('height').text)
                img_area = width * height
                
                max_area = 0
                for obj in root.findall('object'):
                    bndbox = obj.find('bndbox')
                    xmin = int(bndbox.find('xmin').text)
                    ymin = int(bndbox.find('ymin').text)
                    xmax = int(bndbox.find('xmax').text)
                    ymax = int(bndbox.find('ymax').text)
                    area = (xmax - xmin) * (ymax - ymin)
                    if area > max_area:
                        max_area = area
                
                if max_area == 0:
                    severity = 'nenhum'
                else:
                    area_rel = max_area / img_area
                    if area_rel < 0.001:
                        severity = 'pequeno'
                    elif area_rel < 0.01:
                        severity = 'medio'
                    else:
                        severity = 'grande'
            else:
                severity = 'nenhum'
            ground_truth[filename] = severity
    return ground_truth

def run_evaluation(images_folder, ground_truth):
    # ground_truth é um dicionário: {'imagem1.png': 'grande', 'imagem2.png': 'pequeno', ...}
    y_true = []
    y_pred = []
    
    # Inicia pipeline genérico (assumindo tamanho padrão, o pipeline se ajusta)
    pipeline = PotholePipeline((480, 640)) 
    
    for filename in os.listdir(images_folder):
        if filename.endswith(('.png', '.jpg')):
            filepath = os.path.join(images_folder, filename)
            img = cv2.imread(filepath)
            
            if img is None or filename not in ground_truth:
                continue
                
            # Roda o seu algoritmo
            results, _ = pipeline.process(img)
            
            # Pega a severidade do maior buraco detectado (ou 'nenhum' se não achar)
            if results:
                # results = [(x,y,w,h,severity), ...]
                # Ordena pela área (w*h) para pegar o buraco principal
                results.sort(key=lambda item: item[2]*item[3], reverse=True)
                pred_severity = results[0][4]
            else:
                pred_severity = 'nenhum'
                
            y_true.append(ground_truth[filename])
            y_pred.append(pred_severity)

    # Gerando Matriz de Confusão
    labels = ['nenhum', 'pequeno', 'medio', 'grande']
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    plt.xlabel('Previsto pelo Sistema')
    plt.ylabel('Real (Ground Truth)')
    plt.title('Matriz de Confusão - Detecção de Buracos')
    
    os.makedirs('results', exist_ok=True)
    plt.savefig('results/confusion_matrix.png')
    print("Matriz salva em results/confusion_matrix.png")
    labels = ['nenhum', 'pequeno', 'medio', 'grande']
    print(classification_report(y_true, y_pred, target_names=labels, labels=labels, zero_division=0))

if __name__ == "__main__":
    # Carrega ground truth dos arquivos XML
    ground_truth = load_ground_truth('assets/samples/annotations/', 'assets/samples/images2/')
    run_evaluation('assets/samples/images2/', ground_truth)