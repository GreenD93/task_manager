from tqdm import tqdm
from utils.settings import *
from test_data_collect import EtlDataCollecter
from test_data_save import EtlDataSaver

labels = ['food', 'shoes', 'inte', 'pet', 'kitc', 'child']


savor = EtlDataSaver()

for label in tqdm(labels):

    collector = EtlDataCollecter(label)

    # get items
    for items in collector.get_items():

        # save data
        savor.save_items(items)