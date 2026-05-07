import cv2
from .preprocessing import Preprocessing
from src.pipeline.detection import Detection
from src.pipeline.classification import Classification
from src.pipeline.heatmap import Heatmap
#from src.pipeline.logger import Logger


class PotholePipeline:
    def __init__(self, img_shape):
        self.pre = Preprocessing()
        self.det = Detection()
        self.cls = Classification(img_shape)
        #self.logger = Logger()
        self.heatmap = Heatmap(img_shape)

    def process(self, img):
        processed = self.pre.apply(img)
        mask = self.pre.to_hsv_mask(img)

        edges = self.det.edges(processed)
        clean = self.det.clean(edges)

        contours = self.det.contours(clean)

        results = []

        for cnt in contours:
            area = cv2.contourArea(cnt)

            if area > 300:
                x, y, w, h = cv2.boundingRect(cnt)
                severity = self.cls.classify(area)

                #self.logger.log("buraco", severity, (x,y))
                results.append((x,y,w,h,severity))

        self.heatmap.update(contours)

        return results, self.heatmap.get_colormap()