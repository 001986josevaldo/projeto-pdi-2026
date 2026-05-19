import cv2
from .preprocessing import Preprocessing
# imports relativos internos do pacote pipeline
from .detection import Detection
from .classification import Classification
from .heatmap import Heatmap
# from .logger import Logger


class PotholePipeline:
    def __init__(self, img_shape):
        self.pre = Preprocessing()
        self.det = Detection()
        self.cls = Classification(img_shape)
        #self.logger = Logger()
        self.heatmap = Heatmap(img_shape)
        self.heatmap_counter = 0

    def process(self, img):
        processed = self.pre.apply(img)
        mask = self.pre.to_hsv_mask(processed)
        # Limpeza morfológica diretamente na máscara
        clean = self.det.clean(mask)
        contours = self.det.contours(clean)

        results = []
        min_area = self.cls.img_area * 0.0005
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            
            if area > min_area:
                x, y, w, h = cv2.boundingRect(cnt)
                severity = self.cls.classify(area)

                #self.logger.log("buraco", severity, (x,y))
                results.append((x,y,w,h,severity))

        heatmap_img = None
        
        self.heatmap.update(contours)
        heatmap_img = self.heatmap.get_colormap()
        
        return results, heatmap_img