import numpy as np
from sklearn.utils import shuffle
from sklearn.model_selection  import train_test_split
import tensorflow as tf
from tensorflow import keras


leaf = np.loadtxt("F:/studies/insa/projet/wine/input/leaf/feuille.csv",dtype=np.float, delimiter=",")
normal = np.loadtxt("F:/studies/insa/projet/wine/input/normal/normal.csv",dtype=np.float, delimiter=",")


lis = np.concatenate((leaf,normal))


total = lis.shape[0]

labels = np.ones((total,), dtype=int)

total_leaf = leaf.shape[0]

#normal = 0 leaf = 1
labels[0:total_leaf - 1] = 1
labels[total_leaf:] = 0

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

model = keras.Sequential([keras.layers.Flatten(input_shape=(360,)),keras.layers.Dense(128, activation=tf.nn.relu),keras.layers.Dense(2, activation=tf.nn.softmax)])

model.compile(optimizer=tf.train.AdamOptimizer(), loss='sparse_categorical_crossentropy',metrics=['accuracy'])

model.fit(X_train, y_train, epochs=10)

test_loss, test_acc = model.evaluate(X_test, y_test)

print('Test accuracy:', test_acc)

predictions = model.predict(X_test)

np.set_printoptions(suppress=True)
i = 0
for item in y_test:
    if i % 10 == 0:
        print(str(y_test[i]) + '->'+ str(predictions[i].argmax()))
    i += 1

non_existing_test = np.loadtxt("F:/studies/insa/projet/wine/input/test/test.csv",dtype=np.float, delimiter=",")
the_max = non_existing_test.max()

if train_max > the_max:
    the_max = train_max
    
#non_existing_test /= the_max

predictions = model.predict(non_existing_test)


