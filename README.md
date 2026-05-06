**Smart City: Monitoramento Integrado de Vias Urbanas**

**Este projeto foi desenvolvido como parte da disciplina de ****Processamento Digital de Imagens (PDI)** no curso de Ciência da Computação da **UNEMAT — Câmpus Universitário de Rondonópolis**.

**👥 Integrantes (Grupo 2)**

* **Josevaldo**
* **Pedro Henrique**

**📝 Descrição do Projeto**

**O sistema utiliza técnicas de visão computacional para realizar o sensoriamento visual contínuo de vias urbanas através de câmeras fixas, focando em dois cenários críticos para a gestão pública:**

* **Detecção de Buracos:** Identificação e classificação de falhas no pavimento asfáltico por severidade**.**
* **Monitoramento de Semáforos:** Detecção do estado luminoso (cores) e registro automático de infrações por avanço de sinal vermelho**.**

**⚙️ Pipeline de PDI**

**O núcleo do processamento segue as exigências técnicas da trilha, utilizando algoritmos clássicos de PDI**:

* **Segmentação:** Espaço de cor **HSV** para o semáforo e filtros **Canny/Sobel** para contornos de buracos.
* **Análise de Movimento:** Subtração de fundo via  **MOG2 ou KNN** **.**
* **Espacialidade:** Transformação de perspectiva ( **warpPerspective** **) para visão ** *bird's-eye* **.**
* **Morfologia:** Operações de limpeza de máscara e análise de contornos para cálculo de área e severidade.

**🚀 Instalação e Execução**

**Conforme as exigências de reprodutibilidade**:

* **Crie um ambiente isolado: **`python -m venv venv`
* **Ative o ambiente:**
  * **Windows: **`venv\Scripts\activate`
  * **Linux/Mac: **`source venv/bin/activate`
* **Instale as dependências: **`pip install -r requirements.txt`
* **Execute o sistema: **`python src/main.py`

**📊 Protocolos de Teste**

**O sistema é validado através de 5 protocolos obrigatórios**:

* **Robustez Luminosa:** Operação estável em diferentes níveis de luz.
* **Resiliência a Oclusão:** Retomada de detecção após bloqueio do alvo.
* **Telemetria de FPS:** Garantia de performance mínima de  **20 FPS** **.**
* **Matriz de Confusão:** Acurácia mínima de **70%** (testada com o *Pothole Image Dataset* do Kaggle)**.**
* **Tolerância a Falhas:** Recuperação após desconexão da webcam.

**⚖️ Conformidade com a LGPD**

**Em conformidade com a Lei 13.709/2018, este sistema implementa ** **anonimização por padrão** **. Placas de veículos e rostos de pedestres detectados incidentalmente são borrados em tempo real e não são persistidos em logs ou arquivos de imagem, garantindo a privacidade dos dados capturados em via pública**.

**🤖 Uso de IA Generativa**

* **Ferramentas:** (Ex: ChatGPT, GitHub Copilot)
* **Usos:** (Ex: Geração de trechos de código de interface, depuração de erros e auxílio na redação deste README).

**📄 Licença e Referências**

* **GONZALEZ, R. C.; WOODS, R. E. Processamento Digital de Imagens. 4. ed. Pearson, 2018**.
* **Documentação OpenCV: https://docs.opencv.org**.
