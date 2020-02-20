from pprint import pprint

import tensorflow as tf
from tensorflow.keras import Model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, BatchNormalization, Dropout, Activation
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam,RMSprop, SGD

#------------------------------------------------------
# ImageModelHandler

class ImageModelHandler():

    #---------------------------------------------
    # constructor
    def __init__(self,
        name='bg_err',
        img_width=IMG_WIDTH,
        max_sample_count=MAX_SAMPLE_COUNT,
        batch_size=BATCH_SIZE,
        max_epoch_count=MAX_EPOCH_COUNT
    ):
        self.name = name

        #-------------------------------
        # 상수
        self.img_width = img_width
        self.max_sample_count = max_sample_count  # true, false 각 샘플의 최대개수
        self.batch_size = batch_size
        self.max_epoch_count = max_epoch_count

        #-------------------------------
        # 모델 유형결정
        self.name = name

        self._prepare()

        pass

    #---------------------------------------------
    # _prepare
    def _prepare(self):
        pprint('>> _prepare')
        self._load_model()
        self._load_weights()
        pass

    #---------------------------------------------
    # train
    def train(self):
        pprint('>> train')
        self._train_model()
        pass

    def predict(self, items):
        pass

    def evaluate(self):
        pass

    # data generator
    def _train_model(self):
        pprint('>> _train_model')

        #-------------------------------------------
        # dataset generator 가져오기
        # dataset_generator = DatasetGenerator(
        #     selected_flag=self.selected_flag,
        #     max_sample_count=self.max_sample_count,
        #     batch_size=self.batch_size,
        #     img_width=self.img_width)
        #
        # train_data_generator, val_data_generator, real_true_row_count, real_false_row_count = dataset_generator.get_data_generators(trainable=True)
        # total_count = dataset_generator.get_row_count()


        #-------------------------------------------
        # model compile
        # history = self.model.fit_generator(
        #     train_data_generator,
        #     steps_per_epoch = train_steps,
        #     epochs=self.max_epoch_count,
        #     validation_data=val_data_generator,
        #     validation_steps=validation_steps,
        #     verbose=2,
        #     callbacks=[
        #         LossAndErrorPrintingCallback(name=self.name),
        #         EarlyStoppingAtMinValLoss(
        #             model_handler=self,
        #             prev_best=get_prev_best(),
        #             patience=get_epoch_retry_count()
        #         )
        #     ],
        # )
        pass

    def _load_model(self):

        input_shape = (self.img_width, self.img_width, 3)

        model = Sequential(
            Conv2D(16, kernel_size=(3, 3), padding='same', activation='relu', input_shape=input_shape),
            MaxPooling2D(pool_size=(2, 2)),
            Conv2D(16, kernel_size=(3, 3), padding='same', activation='relu'),
            MaxPooling2D(pool_size=(2, 2)),
            Conv2D(16, kernel_size=(3, 3), padding='same', activation='relu'),
            MaxPooling2D(pool_size=(2, 2)),
            Flatten(),
            Dense(512, activation='relu'),
            Dropout(0.25),
            Dense(1, activation='sigmoid')
        )

        model.compile(loss='binary_crossentropy',
                      optimizer='sgd',
                      # optimizer='rmsprop',
                      # optimizer='adam',

                      metrics=['accuracy'])

        model.summary()
        pass

    def _load_weights(self):
        pass

    def _save_model(self):
        pass

    def _save_weights(self):
        pass