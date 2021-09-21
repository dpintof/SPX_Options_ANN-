#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 09:29:12 2021

@author: Diogo
"""

# from keras.models import Sequential
# from keras.layers import Dense, LeakyReLU, BatchNormalization
# from keras.optimizers import Adam
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
from os import path
# from tensorflow.keras.callbacks import TensorBoard


# tboard_log_dir = path.join("Saved_models", "mlp2_call_1")
# tensorboard = TensorBoard(log_dir = tboard_log_dir)


# Hyperparameters
n_hidden_layers = 4
n_units = 400 # Number of neurons of the hidden layers.
n_batch = 4096 # Number of observations used per gradient update.
n_epochs = 50
learning_rate = 0.001


# Create DataFrame (df) for calls
basepath = path.dirname(__file__)
filepath = path.abspath(path.join(basepath, "..", 
                                  "Processed data/options_phase3_final.csv"))
df = pd.read_csv(filepath)
# df = df.dropna(axis=0)
df = df.drop(columns=['Option_Average_Price', "QuoteDate"])
call_df = df[df.OptionType == 'c'].drop(['OptionType'], axis=1)


# Split call_df into random train and test subsets, for inputs (X) and output (y)
call_X_train, call_X_test, call_y_train, call_y_test = train_test_split(
    call_df.drop(["bid_eod", "ask_eod"], axis = 1), 
    call_df[["bid_eod", "ask_eod"]], test_size = 0.01)


# Create model using Keras' functional API
def mlp2_call(n_units, n_hidden_layers):
    
    # Create input layer
    inputs = keras.Input(shape = (call_X_train.shape[1],))
    x = layers.LeakyReLU()(inputs)
    # x = layers.LeakyReLU(0.1)(inputs)

    """Function that creates a hidden layer by taking a tensor as input and 
    applying Batch Normalization and the LeakyReLU activation."""
    def hl(tensor, n_units):
        # initializer = tf.keras.initializers.GlorotUniform() 
        # initializer = tf.keras.initializers.Constant()
        # initializer = tf.keras.initializers.he_normal()
        # initializer = tf.keras.initializers.RandomNormal(
            # stddev = math.sqrt(4 / (32 + 32)))
        dense_layer = layers.Dense(n_units)
        # dense = layers.Dense(n_units, kernel_initializer = initializer, 
                    # kernel_regularizer = regularizers.l1_l2(l1=1e-5, l2 = 1e-4))
        # dense = layers.Dense(n_units, kernel_initializer = initializer,
        #                                   bias_initializer = initializer)
        """Dense() creates a densely-connected NN layer, implementing the 
        following operation: output = activation(dot_product(input, kernel) + 
        bias) where activation is the element-wise activation function passed 
        as the activation argument, kernel is a weights matrix created by the 
        layer, and bias is a bias vector created by the layer (only applicable 
        if use_bias is True, which it is by default). In this case no 
        activation function was passed so there is "linear" activation: a(x) = 
        x."""
        x = dense_layer(tensor)
        bn = layers.BatchNormalization()(x)
        """
        Batch normalization scales the output of a layer by subtracting the batch
        mean and dividing by the batch standard deviation (so the output's mean 
        will be close to 0 and it's standard deviation close to 1). Theoretically 
        this can speed up the training of the neural network.
        """
        leaky = layers.LeakyReLU()(bn)
        # leaky = layers.LeakyReLU(0.1)(bn)
        return leaky

    # Create hidden layers
    for _ in range(n_hidden_layers):
        x = hl(x, n_units)
    
    # Create output layer
    outputs = layers.Dense(2, activation='relu')(x)
    
    # Actually create the model
    model = keras.Model(inputs = inputs, outputs = outputs)

    return model


# # Create model using Keras' functional API
# # Create input layer
# inputs = keras.Input(shape = (call_X_train.shape[1],))
# x = layers.LeakyReLU()(inputs)

# # Create function that creates a hidden layer by taking a tensor as input and 
#     # applying Batch Normalization and the LeakyReLU activation.
# def hl(tensor):
#     dense = layers.Dense(n_units)
#     # Dense() creates a densely-connected NN layer, implementing the following 
#         # operation: output = activation(dot_product(input, kernel) + bias) 
#         # where activation is the element-wise activation function passed as the 
#         # activation argument, kernel is a weights matrix created by the layer, 
#         # and bias is a bias vector created by the layer (only applicable if 
#         # use_bias is True, which it is by default). In this case no activation 
#         # function was passed so there is "linear" activation: a(x) = x.
#     x = dense(tensor)
#     bn = layers.BatchNormalization()(x)
#     # Batch normalization scales the output of a layer by subtracting the batch
#         # mean and dividing by the batch standard deviation (so it maintains 
#         # the output's mean close to 0 and it's standard deviation close to 1).
#         # Theoretically this can speed up the training of the neural network.
#     lr = layers.LeakyReLU()(bn)
#     return lr

# # Create hidden layers
# for _ in range(n_hidden_layers):
#     x = hl(x)

# # Create output layer
# outputs = layers.Dense(2, activation='relu')(x)

# # Actually create the model
# model = keras.Model(inputs=inputs, outputs=outputs)


# # Create a Sequential model that is a linear stack of layers
# model = Sequential()

# # Adds layers incrementally
# model.add(Dense(n_units, input_dim=call_X_train.shape[1]))
# model.add(LeakyReLU())

# for _ in range(layers - 1):
#     model.add(Dense(n_units))
#     model.add(BatchNormalization())
#     model.add(LeakyReLU())

# model.add(Dense(2, activation='relu'))


"""Configure the learning process, train the model, save model and it's losses, 
with different learning rates, batch sizes and number of epochs.
"""
# Learning_rate = learning_rate as defined in the hyperparameters section
model = mlp2_call(n_units, n_hidden_layers)
model.compile(loss='mse', optimizer = keras.optimizers.Adam(
                                                learning_rate=learning_rate))
history = model.fit(call_X_train, call_y_train, 
                    batch_size=n_batch, epochs=n_epochs, 
                    validation_split = 0.01, verbose=1)

# Introduced "directory" to prevent an error when running the code on Windows
directory = path.join("Saved_models", "mlp2_call_1")
model.save(directory)
# model.save("Saved_models/mlp2_call_1")
train_loss = history.history["loss"]
validation_loss = history.history["val_loss"]
numpy__train_loss = np.array(train_loss)
numpy_validation_loss = np.array(validation_loss)
np.savetxt("Saved_models/mlp2_call_1_train_losses.txt", 
            numpy__train_loss, delimiter=",")
np.savetxt("Saved_models/mlp2_call_1_validation_losses.txt", 
            numpy_validation_loss, delimiter=",")


# Learning rate changes with the number of epochs, as in Ke and Yang (2019)
step = tf.Variable(0, trainable = False)
boundaries = [10, 20]
values = [1e-3, 1e-4, 1e-5]
learning_rate_fn = keras.optimizers.schedules.PiecewiseConstantDecay(
    boundaries, values)

learning_rate = learning_rate_fn(step)

model = mlp2_call(n_units, n_hidden_layers)
model.compile(loss='mse', optimizer = keras.optimizers.Adam(
                                                learning_rate=learning_rate))
history = model.fit(call_X_train, call_y_train, 
                    batch_size=n_batch, epochs=n_epochs, 
                    validation_split = 0.01, verbose=1)
directory = path.join("Saved_models", "mlp2_call_2")
model.save(directory)
train_loss = history.history["loss"]
validation_loss = history.history["val_loss"]
numpy__train_loss = np.array(train_loss)
numpy_validation_loss = np.array(validation_loss)
np.savetxt("Saved_models/mlp2_call_2_train_losses.txt", 
            numpy__train_loss, delimiter=",")
np.savetxt("Saved_models/mlp2_call_2_validation_losses.txt", 
            numpy_validation_loss, delimiter=",")


# model.compile(loss='mse', optimizer = keras.optimizers.Adam(lr=1e-4))
# history = model.fit(call_X_train, call_y_train, 
#                     batch_size=n_batch, epochs=n_epochs, 
#                     validation_split = 0.01, verbose=1)
# model.save('Saved_models/mlp2_call_2')
# train_loss = history.history["loss"]
# validation_loss = history.history["val_loss"]
# numpy__train_loss = np.array(train_loss)
# numpy_validation_loss = np.array(validation_loss)
# np.savetxt("Saved_models/mlp2_call_2_train_losses.txt", 
#             numpy__train_loss, delimiter=",")
# np.savetxt("Saved_models/mlp2_call_2_validation_losses.txt", 
#             numpy_validation_loss, delimiter=",")

# model.compile(loss='mse', optimizer = keras.optimizers.Adam(1e-5))
# history = model.fit(call_X_train, call_y_train, 
#                     batch_size=n_batch, epochs=n_epochs, 
#                     validation_split = 0.01, verbose=1)
# model.save('Saved_models/mlp2_call_3')
# train_loss = history.history["loss"]
# validation_loss = history.history["val_loss"]
# numpy__train_loss = np.array(train_loss)
# numpy_validation_loss = np.array(validation_loss)
# np.savetxt("Saved_models/mlp2_call_3_train_losses.txt", 
#             numpy__train_loss, delimiter=",")
# np.savetxt("Saved_models/mlp2_call_3_validation_losses.txt", 
#             numpy_validation_loss, delimiter=",")

# model.compile(loss='mse', optimizer = keras.optimizers.Adam(1e-6))
# history = model.fit(call_X_train, call_y_train, 
#                     batch_size=n_batch, epochs=10, 
#                     validation_split = 0.01, verbose=1)
# model.save('Saved_models/mlp2_call_4')
# train_loss = history.history["loss"]
# validation_loss = history.history["val_loss"]
# numpy__train_loss = np.array(train_loss)
# numpy_validation_loss = np.array(validation_loss)
# np.savetxt("Saved_models/mlp2_call_4_train_losses.txt", 
#             numpy__train_loss, delimiter=",")
# np.savetxt("Saved_models/mlp2_call_4_validation_losses.txt", 
#             numpy_validation_loss, delimiter=",")

# # SHORT TEST
# model.compile(loss='mse', optimizer = keras.optimizers.Adam(lr=1e-6))
# history = model.fit(call_X_train, call_y_train, 
#                 batch_size=4096, epochs=1, validation_split = 0.01, verbose=1)
# model.save('Saved_models/mlp2_call_5')
# train_loss = history.history["loss"]
# validation_loss = history.history["val_loss"]
# numpy__train_loss = np.array(train_loss)
# numpy_validation_loss = np.array(validation_loss)
# np.savetxt("Saved_models/mlp2_call_5_train_losses.txt", 
#             numpy__train_loss, delimiter=",")
# np.savetxt("Saved_models/mlp2_call_5_validation_losses.txt", 
#             numpy_validation_loss, delimiter=",")

