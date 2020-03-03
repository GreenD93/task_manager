# coding: utf-8

from pprint import pprint

import os
import time
import warnings

import numpy as np
import cv2

import tensorflow as tf
from tensorflow.keras import Model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, BatchNormalization, Dropout, Activation
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam, RMSprop, SGD
from tensorflow.keras.callbacks import EarlyStopping

from utils.util import *
from utils.settings import *
from utils.db_utils import *

from procs.train.train_settings import *

from procs.train.img.img_dataset_generator import DatasetGenerator
from procs.train.img.img_train_callbacks import LossAndErrorPrintingCallback, EarlyStoppingAtMinValLoss


#------------------------------------------------------
# ImageModelHandler

class ImageModelHandler():

    #---------------------------------------------
    # constructor
    def __init__(self,
        name='bg_err',
        n_class=N_CLASS,
        img_width=IMG_WIDTH,
        max_sample_count=MAX_SAMPLE_COUNT,
        batch_size=BATCH_SIZE,
        max_epoch_count=MAX_EPOCH_COUNT
    ):

        warnings.filterwarnings(action='ignore')

        self.model = None
        self.trained = False

        #-------------------------------
        # 상수
        self.n_class = n_class
        self.img_width = img_width
        self.max_sample_count = max_sample_count  # true, false 각 샘플의 최대개수
        self.batch_size = batch_size
        self.max_epoch_count = max_epoch_count

        self.real_row_count_dict = None

        #-------------------------------
        # 모델 이름
        self.name = name

        #-------------------------------
        # model file path 결정
        self.model_path = MODEL_PATH.replace('/models/', '/models/{}/'.format(self.name))
        self.model_weights_path = MODEL_WEIGHTS_PATH.replace('/models/', '/models/{}/'.format(self.name))

        check_or_create_folder_from_filepath(self.model_path)

        self._prepare()

        pass


    #---------------------------------------------
    # _prepare
    def _prepare(self):
        log_info('>> _prepare')
        self._load_model()
        self._load_weights()
        pass


    #---------------------------------------------
    # train
    def train(self):
        log_info('>> train')
        self._train_model()
        pass


    #---------------------------------------------
    # predict
    def predict(self, arr_imgs):

        # 모델이 없거나, 학습이 안되어 있으면 -> False를 리턴 (에러아님으로 판단)
        if (self.model is None) or (not self.trained):
            result = [0.0] * len(arr_imgs)
            result = np.array(result, dtype=np.float32)
            return result

        # 모델이 있고, 학습도 되었다면
        else:
            resized_imgs = self._resize_and_float_imgs(arr_imgs)
            # 1d np.array로 predict된 label return
            return self.model.predict_classes(resized_imgs)



    #---------------------------------------------
    # _resize_and_float_imgs
    def _resize_and_float_imgs(self, arr_imgs):

        count = len(arr_imgs)

        resized_imgs = []

        for i in range(count):

            np_img = arr_imgs[i]

            #----------------------------
            # resize image
            h, w = np_img.shape[:2]
            max_w = max(w, h)

            resized_img = np.zeros((max_w, max_w, 3), np.uint8)
            resized_img[:h,:w] = np_img[:h,:w]


            resized_img = cv2.resize(resized_img, dsize = (self.img_width, self.img_width), interpolation=cv2.INTER_NEAREST)
            #----------------------------

            resized_imgs.append(resized_img)

        #----------------------------
        # convert byte image to floating image : 0~255 -> 0.0~1.0
        resized_imgs = np.array(resized_imgs, dtype=np.float32)
        resized_imgs = resized_imgs / 255.0

        return resized_imgs


    #---------------------------------------------
    # _load_model
    def _load_model(self):

        #---------------------------------------
        # 기존 모델파일이 있으면, 모델파일을 로딩
        if os.path.exists(self.model_path):

            json_model = file_to_json(self.model_path)
            self.model = tf.keras.models.model_from_json(json_to_str(json_model))

            self.model.compile(loss='sparse_categorical_crossentropy',
                          optimizer='sgd',
                          metrics=['accuracy'])

            self.model.summary()

            log_info('>> model loaded: {}'.format(self.model_path))

            return


        #---------------------------------------
        # 기존 모델파일이 없으면, 모델만들기

        if True:
            input_shape = (self.img_width, self.img_width, 3)

            model = Sequential([
                Conv2D(16, kernel_size=(3,3), padding='same', activation='relu', input_shape = input_shape),
                MaxPooling2D(pool_size=(2,2)),
                Conv2D(16, kernel_size=(3,3), padding='same', activation='relu'),
                MaxPooling2D(pool_size=(2,2)),
                Conv2D(16, kernel_size=(3,3), padding='same', activation='relu'),
                MaxPooling2D(pool_size=(2,2)),
                Flatten(),
                Dense(512, activation='relu'),
                Dropout(0.25),
                Dense(self.n_class, activation='softmax')
            ])

            model.compile(loss='sparse_categorical_crossentropy',
                          optimizer='sgd',
                          metrics=['accuracy'])

            model.summary()

            pprint('>> create model.')


        self.model = model

        self._save_model()


        pass


    #---------------------------------------------
    # _save_model
    def _save_model(self):

        if self.model is not None:
            json_to_file(
                self.model_path,
                str_to_json(
                    self.model.to_json()
                )
            )

            log_info('>> model saved: {}'.format(self.model_path))
        pass


    #---------------------------------------------
    # _load_weights
    def _load_weights(self):
        log_info('>> _load_weights')
        # TODO

        if (self.model is not None) and os.path.exists(self.model_weights_path):
            self.model.load_weights(self.model_weights_path)
            log_info('>> loaded weights: {}'.format(self.model_weights_path))
            self.trained = True

        pass



    # #---------------------------------------------
    # # _save_weights
    # def _save_weights(self):
    #     log_info('>> _save_weights')
    #     # TODO
    #     if self.model is not None:
    #         self.model.save(self.model_weights_path)
    #     pass


    #---------------------------------------------
    # save_weights
    def save_weights(self, logs=None):
        log_info('>> save_weights')

        if self.model is not None:

            # rename_file(self.model_weights_path, 'old_'+self.model_weights_path)

            self.model.save(self.model_weights_path)
            log_info('>> weights saved: {}'.format(self.model_weights_path))

            if logs is not None:
                meta_path = self.model_weights_path.replace('.h5', '.meta')

                json_meta = {
                    '_processed_time': get_current_time_string(),
                    'epoch': logs['epoch'],
                    'loss': float(logs['loss']),
                    'acc': float(logs['acc']),
                    'val_loss': float(logs['val_loss']),
                    'val_acc': float(logs['val_acc']),
                    '_count_category': self.real_row_count_dict,
                }

                # rename_file(meta_path, 'old_'+meta_path)

                json_to_file(meta_path, json_meta)

                log_info('>> meta saved: {}'.format(meta_path))

            self.trained = True

        pass


    def get_trained_weights(self):
        if self.trained:
            return self.model.get_weights()
        else:
            return None



    #---------------------------------------------
    # _train_model
    def _train_model(self):
        pprint('>> _train_model')

        # image generator . flow_from_dataframe 다음을 참조할것
        # https://taeguu.tistory.com/27
        # https://ballentain.tistory.com/4

        def get_prev_best():

            meta_path = self.model_weights_path.replace('.h5', '.meta')

            # 만약 weight가 있고, meta파일도 있으면, 일단 읽어온다
            if self.trained and os.path.exists(meta_path):
                json_prev_best = file_to_json(meta_path)

                # if not ('epoch' in json_prev_best):
                #     json_prev_best['epoch'] = 0

                json_prev_best['epoch'] = 0

                # 현재 weight의 모델을 평가해서 loss, acc를 가져온다
                loss, acc = self.evaluate()

                # 만약 best의 값을 현재 샘플에 맞게 현실화...
                if json_prev_best['val_loss'] < loss and json_prev_best['val_acc'] > acc:
                    pprint('>> use UPDATED best')
                    json_prev_best['val_loss'] = loss + loss * 0.1
                    json_prev_best['val_acc'] = acc - acc * 0.1
                    json_prev_best['loss'] = loss + loss * 0.1
                    json_prev_best['acc'] = acc - acc * 0.1

                # 만약 evaluate값이 best보다 좋으면, best를 그대로 쓰기
                else:
                    pprint('>> use OLD best')

                return json_prev_best

            # 그외의 경우라면, best를 초기화한다
            pprint('>> use NEW best')
            json_prev_best = {
                '_processed_time': get_current_time_string(),
                'epoch': 0,
                'loss': np.Inf,
                'acc': 0.0,
                'val_loss': np.Inf,
                'val_acc': 0.0,
            }
            return json_prev_best


        def get_epoch_retry_count():
            # return max(10, self.batch_size*2)  # val_loss가 이전보다 더 커지면 몇번까지 더 시도를 해볼것인지
            return max(10, self.max_epoch_count // 4)  # val_loss가 이전보다 더 커지면 몇번까지 더 시도를 해볼것인지


        #-------------------------------------------
        # dataset generator 가져오기
        dataset_generator = DatasetGenerator(
            max_sample_count=self.max_sample_count,
            batch_size=self.batch_size,
            img_width=self.img_width)

        train_data_generator, val_data_generator, real_row_count_dict, _ = dataset_generator.get_data_generators(trainable=True)
        total_count = dataset_generator.get_row_count()

        self.real_row_count_dict = real_row_count_dict

        #-------------------------------------------
        # 학습
        train_count = int(total_count * 0.8)
        val_count = int(total_count * 0.2)

        train_steps = train_count // self.batch_size
        validation_steps = val_count // self.batch_size

        pprint('>> train_count: {}'.format(train_count))
        pprint('>> val_count: {}'.format(val_count))
        pprint('>> train_steps: {}'.format(train_steps))
        pprint('>> validation_steps: {}'.format(validation_steps))
        pprint('>> real_category_row_count: {}'.format(real_row_count_dict))

        history = self.model.fit(
            train_data_generator,
            steps_per_epoch = train_steps,
            epochs=self.max_epoch_count,
            validation_data=val_data_generator,
            validation_steps=validation_steps,
            verbose=1,
            callbacks=[
                LossAndErrorPrintingCallback(name=self.name),
                EarlyStoppingAtMinValLoss(
                    model_handler=self,
                    prev_best=get_prev_best(),
                    patience=get_epoch_retry_count()
                )
            ],
        )


        # #-------------------------------------------
        # # test
        # sample_val_images, sample_val_ys = next(val_data_generator)
        #
        # pprint('{}'.format(sample_val_images.shape))
        # pprint('{}'.format(sample_val_ys.shape))
        #
        #
        # res = self.model.predict(sample_val_images)
        # log_info(res)
        # log_info(sample_val_ys)

        pass

    #---------------------------------------------
    # evaluate
    def evaluate(self):

        dataset_generator = DatasetGenerator(
            max_sample_count=self.max_sample_count,
            batch_size=self.batch_size,
            img_width=self.img_width)

        eval_data_generator, _, _, _ = dataset_generator.get_data_generators(trainable=False)

        loss, acc = self.model.evaluate_generator(eval_data_generator, steps=50*self.batch_size)

        pprint('>> EVALUATED: loss[{:.4f}], acc[{:.4f}]'.format(loss, acc))

        return float(loss), float(acc)
