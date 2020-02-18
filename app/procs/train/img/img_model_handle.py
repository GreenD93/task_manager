#------------------------------------------------------
# ImageModelHandler

class ImageModelHandler():

    #---------------------------------------------
    # constructor
    def __init__(self, name='bg_err'):
        self.name = name

    def train(self):
        pass

    def predict(self, items):
        pass

    def evaluate(self):
        pass

    # data generator
    def _train_model(self):
        pass

    def _load_model(self):
        pass

    def _load_weights(self):
        pass

    def _save_model(self):
        pass

    def _save_weights(self):
        pass