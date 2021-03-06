from dataLoader import *
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import metrics
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Dropout, Dense, Activation
from tensorflow.keras.callbacks import ModelCheckpoint
import sys

import matplotlib.pyplot as plt
from sklearn import manifold, datasets

os.environ['CUDA_VISIBLE_DEVICES'] = '1'
tf.config.experimental.set_memory_growth(tf.config.experimental.list_physical_devices('GPU')[0], True)
DATA_NAME = sys.argv[1] if len(sys.argv) > 1 else "CIFAR"
TARGET_MODEL_GENRE = sys.argv[2] if len(sys.argv) > 2 else "ResNet50"
SHADOW_MODEL_GENRE = sys.argv[3] if len(sys.argv) > 3 else "VGG16"
EPOCHS = 40
BATCH_SIZE = 64
NUM_CLASSES = 1
LEARNING_RATE = 2e-4
NN_ATTACK_WEIGHTS_PATH = "weights/NN_Attack/BlackBox/NN_Attack_{}_{}.hdf5".format(DATA_NAME, SHADOW_MODEL_GENRE)
TARGET_WEIGHTS_PATH = "weights/Target/{}_{}.hdf5".format(DATA_NAME, TARGET_MODEL_GENRE)
SHADOW_WEIGHTS_PATH = "weights/BlackShadow/{}_{}.hdf5".format(DATA_NAME, SHADOW_MODEL_GENRE)

(x_train_sha, y_train_sha), (x_test_sha, y_test_sha), m_train = globals()['load_' + DATA_NAME]('ShadowModel')
Shadow_Model = load_model(SHADOW_WEIGHTS_PATH)
c_train = np.sort(Shadow_Model.predict(np.r_[x_train_sha, x_test_sha]), axis=1)[:, ::-1]

(x_train_tar, y_train_tar), (x_test_tar, y_test_tar), m_test = globals()['load_' + DATA_NAME]('TargetModel')
Target_Model = load_model(TARGET_WEIGHTS_PATH)
c_test = np.sort(Target_Model.predict(np.r_[x_train_tar, x_test_tar]), axis=1)[:, ::-1]

'''

y = m_test.tolist()
print(c_test.shape, m_test.shape)

tsne = manifold.TSNE(n_components=2, init='pca', random_state=51)
X_tsne = tsne.fit_transform(c_test)
y = m_test

np.save('x_cifar10_target', X_tsne)

#X_tsne = np.load('x.npz.npy').tolist()
#print("Org data dimension is {}. \
    #Embedded data dimension is {}".format(target_attack_x.shape[-1], X_tsne.shape[-1]))

###嵌入空间可视化

x_min, x_max = np.min(X_tsne, 0), np.max(X_tsne, 0)
data = (X_tsne - x_min) / (x_max - x_min)
for i in range(data.shape[0]):
    plt.text(data[i, 0], data[i, 1], str(int(y[i])),
                color=plt.cm.Set1(int(y[i])),
                fontdict={'weight': 'bold', 'size': 3})
plt.xticks([])
plt.yticks([])
plt.title('T-SNE')
plt.savefig('tsne_target_cifar10.png', dpi=600, format='png')
plt.show() 

plt.close()
y = m_train.tolist()
print(c_train.shape, m_train.shape)

tsne = manifold.TSNE(n_components=2, init='pca', random_state=51)
X_tsne = tsne.fit_transform(c_train)
y = m_train

np.save('x_cifar10_shadow', X_tsne)

#X_tsne = np.load('x.npz.npy').tolist()
#print("Org data dimension is {}. \
    #Embedded data dimension is {}".format(target_attack_x.shape[-1], X_tsne.shape[-1]))

###嵌入空间可视化

x_min, x_max = np.min(X_tsne, 0), np.max(X_tsne, 0)
data = (X_tsne - x_min) / (x_max - x_min)
for i in range(data.shape[0]):
    plt.text(data[i, 0], data[i, 1], str(int(y[i])),
                color=plt.cm.Set1(int(y[i])),
                fontdict={'weight': 'bold', 'size': 3})
plt.xticks([])
plt.yticks([])
plt.title('T-SNE')
plt.savefig('tsne_shadow_cifar10.png', dpi=600, format='png')
plt.show() 
print(aaa)
'''


def create_attack_model(input_dim, num_classes=NUM_CLASSES):
    model = tf.keras.Sequential([
        Dense(512, input_dim=input_dim, activation='relu'),
        Dropout(0.2),
        Dense(256, activation='relu'),
        Dropout(0.2),
        Dense(128, activation='relu'),
        Dense(num_classes),
        Activation('sigmoid')
    ])
    model.summary()
    return model

def train(model, x_train, y_train):
    model.compile(loss='binary_crossentropy',
                  optimizer=keras.optimizers.Adam(lr=LEARNING_RATE),
                  metrics=[metrics.BinaryAccuracy(), metrics.Precision(), metrics.Recall()])
    checkpoint = ModelCheckpoint(NN_ATTACK_WEIGHTS_PATH, monitor='precision', verbose=1, save_best_only=True,
                                 mode='max')
    model.fit(x_train, y_train,
              epochs=EPOCHS,
              batch_size=BATCH_SIZE,
              callbacks=[checkpoint])


def evaluate(x_test, y_test):
    model = keras.models.load_model(NN_ATTACK_WEIGHTS_PATH)
    loss, accuracy, precision, recall = model.evaluate(x_test, y_test, verbose=1)
    F1_Score = 2 * (precision * recall) / (precision + recall)
    print('loss:%.4f accuracy:%.4f precision:%.4f recall:%.4f F1_Score:%.4f'
          % (loss, accuracy, precision, recall, F1_Score))


attackModel = create_attack_model(c_train.shape[1])
train(attackModel, c_train, m_train)
'''
print(c_train.shape, m_train.shape)
c_train = attackModel.predict(c_train)
print(c_train.shape, m_train.shape)
print(m_train)
temp_0 = []
temp_1 = []
for data,label in zip(c_train,m_train):
    if label == 1.:
        temp_1.append(data[0])
    elif label == 0.:
        temp_0.append(data[0])
print(np.mean(temp_1), np.mean(temp_0))
print(np.std(temp_1), np.std(temp_0))



#--------------------------------------------------------------

print(c_test.shape, m_test.shape)
c_test = attackModel.predict(c_test)
print(c_test.shape, m_test.shape)

temp_0 = []
temp_1 = []
for data,label in zip(c_test,m_test):
    if label == 1.:
        temp_1.append(data[0])
    elif label == 0.:
        temp_0.append(data[0])
print(np.mean(temp_1), np.mean(temp_0))
print(np.std(temp_1), np.std(temp_0))
#print(aaa)
'''

evaluate(c_test, m_test)