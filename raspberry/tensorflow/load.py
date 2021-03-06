'''
this is a test class where we load the model and do a dummy predicition 
it's explained in the raspy code 
'''

import numpy as np
import tensorflow as tf
from tensorflow import keras

x_model = keras.Sequential([
        keras.layers.Flatten(input_shape=(360,)),
        keras.layers.Dense(128, activation=tf.nn.relu),
        keras.layers.Dense(2, activation=tf.nn.softmax)
        ])

path = "F:/studies/insa/projet/wine/"

checkpoint_path = path+"cp.ckpt"
x_model.load_weights(checkpoint_path)

x_model.summary()


non_existing_test = np.loadtxt(path+"input/test/test.csv",dtype=np.float, delimiter=",")

x_predictions = x_model.predict(non_existing_test)

print(str(x_predictions))