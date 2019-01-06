import numpy as np
import tensorflow as tf
from tensorflow import keras

x_model = keras.Sequential([
        keras.layers.Flatten(input_shape=(360,)),
        keras.layers.Dense(128, activation=tf.nn.relu),
        keras.layers.Dense(2, activation=tf.nn.softmax)
        ])

checkpoint_path = "F:/studies/insa/projet/wine/cp.ckpt"
x_model.load_weights(checkpoint_path)

x_model.summary()


non_existing_test = np.loadtxt("F:/studies/insa/projet/wine/input/test/test.csv",dtype=np.float, delimiter=",")

x_predictions = x_model.predict(non_existing_test)