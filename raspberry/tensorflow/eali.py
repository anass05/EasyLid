'''
this is the machine learning algorithm training algorithm,
it should be ran in a PC or a server, tthen you copy the checkpoint files into the rRaspberry to do classifications 
change this: checkpoint_path
'''

import os
import numpy as np
from sklearn.utils import shuffle
from sklearn.model_selection  import train_test_split
import tensorflow as tf
from tensorflow import keras


#read the csv files and store them in numpy arrays
mirror = np.loadtxt("F:/studies/insa/projet/wine/input/mirror/mirror.csv",dtype=np.float, delimiter=",")
normal = np.loadtxt("F:/studies/insa/projet/wine/input/normal/normal.csv",dtype=np.float, delimiter=",")
feuille = np.loadtxt("F:/studies/insa/projet/wine/input/feuille/feuille.csv",dtype=np.float, delimiter=",")
feuilleLoin = np.loadtxt("F:/studies/insa/projet/wine/input/feuilleloin/feuilleloin.csv",dtype=np.float, delimiter=",")

#SHUFFLE those arrays 
np.random.shuffle(mirror)
np.random.shuffle(normal)
np.random.shuffle(feuilleLoin)
np.random.shuffle(feuille)

#RESIZE them to the smallest so we have same amount of data everywhere
minSize = np.array([mirror.shape[0],normal.shape[0],feuille.shape[0],feuilleLoin.shape[0]]).min()
normal = normal[:minSize]
mirror = mirror[:minSize]
feuille = feuille[:minSize]
feuilleLoin = feuilleLoin[:minSize]

#gather everything in a single numpy array
lis = np.concatenate((normal,mirror,feuille,feuilleLoin))

total = lis.shape[0]

labels = np.ones((total,), dtype=int)

#ONE-HOT ENCODING: each anomaly is associated with a number
#normal = 0 mirror = 1 feuille = 2 feuilleLoin = 3
labels[0:minSize - 1] = 0
labels[minSize: 2*minSize - 1] = 1
labels[2*minSize: 3*minSize - 1] = 2
labels[3*minSize:] = 3

out_data, out_labels = shuffle(lis,labels, random_state=2)
train_data = [out_data, out_labels]

#normalizing data
train_max = train_data[0].max()
train_data[0] /= train_max

#deviding data
(X, y) = (train_data[0],train_data[1])


# STEP 1: split X and y into training and testing sets

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=4)


#X_train = X_train.reshape(X_train.shape[0], 1, img_rows, img_cols)
#X_test = X_test.reshape(X_test.shape[0], 1, img_rows, img_cols)

X_train = X_train.astype('float32')
X_test = X_test.astype('float32')

print('X_train shape:', X_train.shape)
print(X_train.shape[0], 'train samples')
print(X_test.shape[0], 'test samples')

model = keras.Sequential([
        keras.layers.Flatten(input_shape=(360,)),
        keras.layers.Dense(128, activation=tf.nn.relu),
        keras.layers.Dense(4, activation=tf.nn.softmax)
        ])



#model.compile(optimizer=tf.train.AdamOptimizer(), loss='sparse_categorical_crossentropy',metrics=['accuracy'])
model.compile(optimizer=tf.keras.optimizers.Adam(lr=0.001), loss='sparse_categorical_crossentropy',metrics=['accuracy'])

#where the model will be saved
checkpoint_path = "F:/studies/insa/projet/wine/cp.ckpt"
checkpoint_dir = os.path.dirname(checkpoint_path)

# Create checkpoint callback
cp_callback = tf.keras.callbacks.ModelCheckpoint(checkpoint_path, 
                                                 save_weights_only=True,
                                                 verbose=1)


#start training 
model.fit(X_train, y_train, epochs=250,callbacks = [cp_callback])
#model.fit(X_train, y_train, epochs=500)

test_loss, test_acc = model.evaluate(X_test, y_test)
#display test accuracy
print('Test accuracy:', test_acc)


#to predict something
#predictions = model.predict(X_test)