
**Smart City — Detecção Automática de Defeitos em Pavimento (Trilha 2 - Cenário A)**

**Disciplina:** Processamento Digital de Imagens (2026/1)**
****Instituição:** **UNEMAT — Nucleo Universitário de Rondonópolis
**Docente:**Prof. Dr. Carlos Alex Sander J. Gulo
****Grupo 2:** Josevaldo e Pedro Henrique

**1. Descrição do Projeto**

**Este produto de software realiza o sensoriamento visual contínuo de vias urbanas para a detecção automática de buracos no asfalto**. O sistema segmenta os defeitos, classifica-os por severidade (Pequeno, Médio ou Grande) com base na área relativa e gera logs georreferenciados para auxiliar na gestão pública municipal**.**

**2. Pipeline de PDI**

**O núcleo de processamento utiliza algoritmos clássicos de PDI a jusante da captura, conforme exigido pela trilha**:

* **Pré-processamento:** Conversão para Tons de Cinza e suavização via Filtro Gaussiano para redução de ruído.
* **Transformação de Perspectiva:** Aplicação de `warpPerspective` para obter uma visão  *bird's-eye view* **, garantindo precisão na análise espacial e de área**.
* **Segmentação de Bordas:** Utilização do algoritmo de **Canny** (ou Sobel) para identificar os limites das irregularidades no asfalto**.**
* **Operações Morfológicas:** Fechamento e dilatação para limpeza da máscara e união de regiões descontínuas**.**
* **Análise de Contornos:** Extração de área absoluta e relativa para classificação de severidade**.**
* **Geração de Resultados:** Marcação visual no vídeo, atualização de contadores na UI e registro em CSV**.**

**3. Instruções de Instalação e Execução**

**Para garantir a ****reprodutibilidade** do projeto**:**

* **Clone o repositório.**
* **Crie um ambiente virtual: **`python -m venv venv`
* **Ative o ambiente:**
  * **Windows: **`venv\Scripts\activate`
  * **Linux/Mac: **`source venv/bin/activate`
* **Instale as dependências: **`pip install -r requirements.txt`
* **Execute o sistema: **`python src/main.py`

**4. Requisitos de Hardware**

* **Câmera fixa (Webcam USB ou câmera de monitoramento IP) com resolução mínima de 720p.**
* **Iluminação adequada (o sistema é testado para operar em diferentes níveis de luz, mas exige visibilidade do pavimento)**.

**5. Resultados dos Protocolos de Teste**

**Resumo da validação realizada conforme os protocolos obrigatórios da Seção 5**:

| **Protocolo**   | **Procedimento**                           | **Resultado Esperado**                         |
| --------------------- | ------------------------------------------------ | ---------------------------------------------------- |
| **1. Luz**      | **Variação de iluminação (3 níveis)** | **Degradação máxima de 30% no F1-score**    |
| **2. Oclusão** | **Bloqueio do buraco por 3 segundos**      | **Retomada da detecção em até 2 segundos**  |
| **3. FPS**      | **Medição de taxa de quadros (60s)**     | **Média estável de ≥ 20 FPS**               |
| **4. Matriz**   | **Avaliação de 50 amostras rotuladas**   | **Acurácia mínima de 70%**                   |
| **5. Falhas**   | **Desconexão física da câmera**         | **Recuperação automática após reconexão** |

**6. Uso de IA Generativa**

**Em conformidade com o §7 das diretrizes**:

* **Ferramentas:** (Ex: ChatGPT, GitHub Copilot).
* **Aplicações:** (Ex: Auxílio na estruturação da interface gráfica e depuração de erros de sintaxe no pipeline de morfologia).
* **Declaração:** A equipe declara estar apta a explicar e modificar todos os trechos de código gerados por IA durante a sabatina técnica**.**

**7. Considerações Éticas (LGPD)**

**O sistema implementa ** **anonimização por padrão** **. Conforme o §6 do documento, qualquer captura incidental de placas de veículos ou rostos de pedestres em via pública é borrada em tempo real**. Não há persistência de dados pessoais sensíveis; apenas o log de eventos (tipo de buraco, severidade e coordenadas) é armazenado**.**

**8. Licença e Referências**

* **GONZALEZ, R. C.; WOODS, R. E. ** **Processamento Digital de Imagens** **. 4. ed. Pearson, 2018**.
* **Documentação OpenCV: https://docs.opencv.org**.
* **Dataset Sugerido: ****Pothole Image Dataset (Kaggle)**.
