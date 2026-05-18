class Classification:
    def __init__(self, img_shape):
        self.img_area = img_shape[0] * img_shape[1]

    def classify(self, area):
        area_rel = area / self.img_area

        if area_rel < 0.003:
            return "pequeno"
        elif area_rel < 0.02:
            return "medio"
        else:
            return "grande"