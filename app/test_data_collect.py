import requests
import time

from utils.settings import *

UNIT = 30
ITER = 100

#------------------------------------------------------
# EtlDataCollecter

class EtlDataCollecter():

    #---------------------------------------------
    # constructor
    def __init__(self, label):

        self.label = label
        self.cat = LABEL[self.label]


    def get_items(self):

        if self.label == 'outfit':
            origin = 1581465549

        else:
            origin = 1581497229


        request_url = 'http://m.sat.wemakeprice.com/api/v1.0/review?reviewCateId={0}&unit={1}'.format(self.cat, UNIT)

        for i in range(0, ITER):

            time.sleep(0.001)

            arr_items = []
            contents, search_after = self._get_response(request_url)

            for data in self._get_data_from_response(contents):
                arr_items.append(data)

            request_url = 'http://m.sat.wemakeprice.com/api/v1.0/review?reviewCateId={0}&unit={1}&cursor=%7B%22origin%22:{2},%22search_after%22:[0,{3}]%7D'.format(
                self.cat, UNIT, origin, search_after)

            yield arr_items

    def _get_response(self, request_url):
        response = requests.get(request_url).json()

        search_after = response['cursor']['search_after'][1]
        contents = response['list']

        return contents, search_after

    def _get_data_from_response(self, contents):

        for content in contents:

            reviewId = content['reviewId']
            message = content['message']
            image_url = content['image']['uri'][45:]
            score = content['score']
            label = self.label

            data = {
                'reviewId' : reviewId,
                'message': message,
                'image_url': image_url,
                'score': score,
                'label': label,
                'err1': -1,
                'err2': -1
            }

            yield data