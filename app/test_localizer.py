import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from PIL import Image

img = Image.open('test.jpg')
np_array = np.array(img)
tf_img = tf.convert_to_tensor(np_array, dtype=tf.float32)
tf_img = tf_img[tf.newaxis, ...]

localizer = hub.load("https://tfhub.dev/google/object_detection/mobile_object_localizer_v1/1")

print(localizer.signatures['default'](tf_img))
