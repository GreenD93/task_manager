# coding: utf-8

import numpy as np
from pprint import pprint

from tensorflow.keras.callbacks import Callback, EarlyStopping

from utils.util import *


#-------------------------------------------
# LossAndErrorPrintingCallback

class LossAndErrorPrintingCallback(Callback):

    #---------------------------------------
    # constructor
    def __init__(self, name):
        super(Callback, self).__init__()
        self.name = name
        self.epoch_count = 1
        pass

    #---------------------------------------
    # on_train_batch_end
    def on_train_batch_end(self, batch, logs=None):
        # print('\rbatch:{}, loss:{:.2f}'.format(batch, logs['loss']), end='')
        if batch % 4 == 0:
            pprint(
                '[{}][TRAIN] epoch:{}, batch:{}, loss:{:.4f}, acc:{:.4f}'.format(
                    self.name, self.epoch_count, batch, logs['loss'], logs['accuracy']
                )
            )
        pass

    #---------------------------------------
    # on_test_batch_end
    def on_test_batch_end(self, batch, logs=None):
        # print('\rbatch:{}, loss:{:.2f}'.format(batch, logs['loss']), end='')
        if batch % 4 == 0:
            pprint(
                '[{}][TEST] epoch:{}, batch:{}, loss:{:.4f}, acc:{:.4f}'.format(
                    self.name, self.epoch_count, batch, logs['loss'], logs['accuracy']
                )
            )
        pass

    #---------------------------------------
    # on_epoch_end
    def on_epoch_end(self, epoch, logs=None):
        # print()
        self.epoch_count += 1
        pass


#-------------------------------------------
# EarlyStoppingAtMinLoss

class EarlyStoppingAtMinValLoss(Callback):

    #---------------------------------------
    # constructor
    def __init__(self, model_handler, prev_best, patience=0):
        super(EarlyStoppingAtMinValLoss, self).__init__()

        self.model_handler = model_handler
        self.patience = patience

        self.best = prev_best
        self.best_epoch = -1
        self.best_weights = self.model_handler.get_trained_weights()

        self.epoch_count = 1

        if self.best_weights is not None:
            pprint('loaded pretrained weight')
        else:
            pprint('not loaded pretrained weight')

        pprint('\n'+json_to_str(self.best, pretty=True))

        pass

    #---------------------------------------
    # on_train_begin
    def on_train_begin(self, logs=None):

        # The number of epoch it has waited when loss is no longer minimum.
        self.wait = 0

        # The epoch the training stops at.
        self.stopped_epoch = 0

        pprint('>> prev best val_loss: {:.4f}'.format(self.best['val_loss']))
        pprint('>> prev best weights: {}'.format(type(self.best_weights)))

        pass


    #---------------------------------------
    # on_epoch_end
    def on_epoch_end(self, epoch, logs=None):

        pprint('--------------------------------------------------------')
        pprint('>>> model: [{}]'.format(self.model_handler.name))

        pprint('>>>[{}] best: epoch[{}], loss[{:.4f}], acc[{:.4f}], val_loss[{:.4f}], val_acc[{:.4f}]'.format(
            self.model_handler.name,
            self.best['epoch'],
            self.best['loss'],
            self.best['acc'],
            self.best['val_loss'],
            self.best['val_acc']))

        pprint('>>>[{}] curr: epoch[{}], loss[{:.4f}], acc[{:.4f}], val_loss[{:.4f}], val_acc[{:.4f}]'.format(
            self.model_handler.name,
            self.epoch_count,
            logs['loss'],
            logs['accuracy'],
            logs['val_loss'],
            logs['val_accuracy']))

        #------------------------------
        # 만약 현재가 best보다 좋다면

        # 만약 val_loss, val_acc, loss, acc 모두 최소일때
        if False:
            is_best = ((self.best['acc'] < logs['accuracy']) and
                (self.best['val_acc'] < logs['val_accuracy']) and
                (self.best['loss'] > logs['loss']) and
                (self.best['val_loss'] > logs['val_loss']))

        # 만약 val_loss + abs(val_acc - acc)가 최소일때
        elif False:
            old_v = self.best['val_loss'] + np.abs(self.best['val_acc'] - self.best['acc'])
            new_v = logs['val_loss'] + np.abs(logs['val_accuracy'] - logs['accuracy'])
            is_best = (old_v > new_v)
            pprint('>>> old:{:.4f}, new:{:.4f}'.format(old_v, new_v))

        # 만약 val_loss가 최소일때
        else:
            is_best = (self.best['val_loss'] > logs['val_loss'])



        if is_best:

            self.best = {
                'epoch': epoch,
                'acc': logs['accuracy'],
                'loss': logs['loss'],
                'val_acc': logs['val_accuracy'],
                'val_loss': logs['val_loss'],
            }

            # Record the best weights if current results is better (less).
            self.wait = 0
            self.best_weights = self.model.get_weights()
            self.best_epoch = epoch

            self.model_handler.save_weights(logs=self.best)


        #------------------------------
        # 만약 best가 아니고, 일정횟수 이상 try했으면
        else:
            self.wait += 1
            if self.wait >= self.patience:
                self.stopped_epoch = epoch
                self.model.stop_training = True

                pprint('Restore weights -> best epoch:{}, val_loss:{:.4f}'.format(
                    self.best_epoch, self.best['val_loss']))

                self.model.set_weights(self.best_weights)


        self.epoch_count += 1

        pass


    #---------------------------------------
    # on_train_end
    def on_train_end(self, logs=None):
        pprint('>> on_train_end')
        if self.stopped_epoch > 0:
            pprint('Epoch %05d: early stopping' % (self.stopped_epoch + 1))

        # 그냥 epoch를 다 돌고 끝났다면, best로 세팅
        else:
            self.model.set_weights(self.best_weights)
