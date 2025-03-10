# -*- coding: utf-8 -*-
"""MLP_Project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1go8-XCWuoOm8GwvsB6KkufumfI42Js_8
"""

import numpy as np
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from typing import Tuple


def batch_generator(train_x, train_y, batch_size):
    """
    Generator that yields batches of train_x and train_y.

    :param train_x (np.ndarray): Input features of shape (n, f).
    :param train_y (np.ndarray): Target values of shape (n, q).
    :param batch_size (int): The size of each batch.

    :return tuple: (batch_x, batch_y) where batch_x has shape (B, f) and batch_y has shape (B, q). The last batch may be smaller.
    """

#come back for improvement to shuffle the datasets for randomness. - point for improvement.

    for i in range(0, len(train_x), batch_size):
        batch_x = train_x[i:i+batch_size]
        batch_y = train_y[i:i+batch_size]
        yield batch_x, batch_y





class ActivationFunction(ABC):
    @abstractmethod
    def forward(self, x: np.ndarray) -> np.ndarray:
        """
        Computes the output of the activation function, evaluated on x

        Input args may differ in the case of softmax

        :param x (np.ndarray): input
        :return: output of the activation function
        """
        pass

    @abstractmethod
    def derivative(self, x: np.ndarray) -> np.ndarray:
        """
        Computes the derivative of the activation function, evaluated on x
        :param x (np.ndarray): input
        :return: activation function's derivative at x
        """
        pass


class Sigmoid(ActivationFunction):
    def forward(self, x: np.ndarray) -> np.ndarray:
        return 1 / (1 + np.exp(-x))

    def derivative(self, x: np.ndarray) -> np.ndarray:
        return self.forward(x) * (1 - self.forward(x))


class Tanh(ActivationFunction):
    pass


class Relu(ActivationFunction):
  def forward(self, x: np.ndarray) -> np.ndarray:
    return np.maximum(0, x)  # ReLU function: max(0, x)

  def derivative(self, x: np.ndarray) -> np.ndarray:
    return (x > 0).astype(float)  # Derivative: 1 for x > 0, else 0



class Softmax(ActivationFunction):
    pass


class Linear(ActivationFunction):
    pass


class LossFunction(ABC):
    @abstractmethod
    def loss(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def derivative(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        pass


class SquaredError(LossFunction):
    def loss(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        return 1/2 * np.square(y_pred-y_true)

    def derivative(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        return (y_pred - y_true)/y_pred.shape[0]


class CrossEntropy(LossFunction):
    def loss(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:

        y_pred = np.clip(y_pred, 1e-15, 1 - 1e-15)
        return -np.mean(np.sum(y_true * np.log(y_pred), axis=1))

    def derivative(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:

        y_pred = np.clip(y_pred, 1e-15, 1 - 1e-15)
        return -y_true / y_pred


class Layer:
    def __init__(self, fan_in: int, fan_out: int, activation_function: ActivationFunction):
        """
        Initializes a layer of neurons

        :param fan_in: number of neurons in previous (presynpatic) layer
        :param fan_out: number of neurons in this layer
        :param activation_function: instance of an ActivationFunction
        """
        self.fan_in = fan_in
        self.fan_out = fan_out
        self.activation_function = activation_function

        # this will store the activations (forward prop)
        self.activations = None
        # this will store the delta term (dL_dPhi, backward prop)
        self.delta = None

        # Initialize weights and biaes
        # self.W = None  # weights
        # self.b = None  # biases

        #note to self. looks like He initialization will help relu function
        #come back later

        #self.W = np.random.randn(fan_in, fan_out) * 0.01
        self.W = np.random.randn(fan_in, fan_out) * np.sqrt(2.0 / fan_in)  # He_init for Relu

        self.b = np.zeros((fan_out,))

    def forward(self, h: np.ndarray):
        """
        Computes the activations for this layer

        :param h: input to layer
        :return: layer activations
        """
        #Z calculation

        Z = np.dot(h, self.W) + self.b
        #self.activations = None
        self.activations = self.activation_function.forward(Z)
        return self.activations




    def backward(self, h: np.ndarray, delta: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply backpropagation to this layer and return the weight and bias gradients

        :param h: input to this layer
        :param delta: delta term from layer above
        :return: (weight gradients, bias gradients)
        """

        #compute dZ
        dZ = delta * self.activation_function.derivative(self.activations)
        #compute dW, db

        dL_dW = np.dot(h.T, dZ) / h.shape[0]
        dL_db = np.sum(dZ, axis=0) / h.shape[0]


        self.delta = dZ
        return dL_dW, dL_db


class MultilayerPerceptron:
    def __init__(self, layers: Tuple[Layer]):
        """
        Create a multilayer perceptron (densely connected multilayer neural network)
        :param layers: list or Tuple of layers
        """
        self.layers = layers

    def forward(self, x: np.ndarray) -> np.ndarray:
        """
        This takes the network input and computes the network output (forward propagation)
        :param x: network input
        :return: network output
        """

        for layer in self.layers:
            x = layer.forward(x)
        return x

    def backward(self, loss_grad: np.ndarray, input_data: np.ndarray) -> Tuple[list, list]:


      """
      Applies backpropagation to compute gradients of weights and biases for all layers in the network.

      :param loss_grad: Gradient of loss w.r.t. final layer output (dL/dA).
      :param input_data: The input data to the network (train_x for the first layer).
      :return: (List of weight gradients for all layers, List of bias gradients for all layers).
      """

      dl_dw_all = []
      dl_db_all = []

      dL_dA = loss_grad  # Start with gradient from the loss function

    # Iterate backward through layers
      for i in reversed(range(len(self.layers))):
        layer = self.layers[i]

        # Get the correct input for this layer
        if i == 0:
            h = input_data  # First layer gets train_x
        else:
            h = self.layers[i - 1].activations  # Other layers get activations from previous layer

        # Compute backpropagation step for this layer
        dL_dW, dL_db = layer.backward(h, dL_dA)

        # Store gradients
        dl_dw_all.append(dL_dW)
        dl_db_all.append(dL_db)

        dL_dA = layer.delta

    # Reverse lists to match layer order
      dl_dw_all.reverse()
      dl_db_all.reverse()

      return dl_dw_all, dl_db_all













    def train(self, train_x: np.ndarray, train_y: np.ndarray, val_x: np.ndarray, val_y: np.ndarray, loss_func: LossFunction, learning_rate: float=1E-3, batch_size: int=16, epochs: int=32) -> Tuple[np.ndarray, np.ndarray]:
        """
        Train the multilayer perceptron

        :param train_x: full training set input of shape (n x d) n = number of samples, d = number of features
        :param train_y: full training set output of shape (n x q) n = number of samples, q = number of outputs per sample
        :param val_x: full validation set input
        :param val_y: full validation set output
        :param loss_func: instance of a LossFunction
        :param learning_rate: learning rate for parameter updates
        :param batch_size: size of each batch
        :param epochs: number of epochs
        :return:
        """

        #define the epoch loop

        training_losses = []
        validation_losses = []


        #defin epoch loop

        for epoch in range(epochs):

          #define batch loop
          total_loss = 0

          for batch_x, batch_y in batch_generator(train_x, train_y, batch_size):


            #forward pass
            y_pred = self.forward(batch_x)

            #compute loss

            batchloss = loss_func.loss(batch_y, y_pred)
            total_loss = total_loss + np.mean(batchloss)

            #print(total_loss)


            #backward pass and compute gradianet
            #dL_dW, dL_db  = self.backward(loss_func.derivative(batch_y, output), batch_x)
            dL_dW, dL_db  = self.backward(loss_func.derivative(batch_y[:len(y_pred)], y_pred), batch_x)


            #update weights

            for i in range(len(self.layers)):
              self.layers[i].W -= learning_rate * dL_dW[i]
              self.layers[i].b -= learning_rate * dL_db[i]


          training_losses.append(total_loss / len(train_x))

          # ✅ Compute Validation Loss
          val_output = self.forward(val_x)
          val_loss = loss_func.loss(val_y, val_output)
          validation_losses.append(np.mean(val_loss))








          #printing progress
          print(f"Epoch {epoch+1}/{epochs} - Training Loss: {training_losses[-1]:.4f} - Validation Loss: {validation_losses[-1]:.4f}")



        return training_losses, validation_losses

#using test data and running full function

import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Create 1000 samples, each with 10 features
train_x = np.random.randn(1000, 10)  # Shape: (1000, 10)

# Create 1000 binary labels (0 or 1)
train_y = np.random.randint(0, 2, size=(1000, 1))  # Shape: (1000, 1)

# Print dataset shape
print("train_x shape:", train_x.shape)  # Expected: (1000, 10)
print("train_y shape:", train_y.shape)  # Expected: (1000, 1)

# Layers = (Layer(10,10,Relu()),
#           Layer(10,10,Relu()),
#           Layer(10,10,Relu()),
#           Layer(10,1,Sigmoid()))

#adding more nuerons

Layers = (
    Layer(10, 32, Relu()),
    Layer(32, 32, Relu()),
    Layer(32, 32, Relu()),
    Layer(32, 1, Sigmoid())
)


MLP = MultilayerPerceptron(Layers)

# Loss Function
loss_function = CrossEntropy()


# Split into Train & Validation Sets
split = int(0.8 * len(train_x))  # 80% Training, 20% Validation
val_x, val_y = train_x[split:], train_y[split:]  # Validation Set
train_x, train_y = train_x[:split], train_y[:split]  # Training Set



training_losses, validation_losses = MLP.train(
    train_x, train_y,
    val_x, val_y,
    loss_func=loss_function,
    learning_rate=0.0001,
    batch_size=32,
    epochs=300
)

import matplotlib.pyplot as plt

plt.plot(training_losses, label="Training Loss")
plt.plot(validation_losses, label="Validation Loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.title("Training vs. Validation Loss with Sigmoid")
plt.legend()
plt.show()

# ✅ Compute Accuracy Function
def compute_accuracy(model, X, y):
    """
    Computes accuracy for a given dataset.

    :param model: Trained MLP model
    :param X: Input features
    :param y: True labels
    :return: Accuracy percentage
    """
    predictions = model.forward(X)  # Forward pass to get predicted probabilities
    predictions = (predictions > 0.5).astype(int)  # Convert probabilities to binary class (0 or 1)
    accuracy = np.mean(predictions == y)  # Compare with true labels
    return accuracy * 100  # Convert to percentage

# Compute Accuracy After Training
train_acc = compute_accuracy(MLP, train_x, train_y)
val_acc = compute_accuracy(MLP, val_x, val_y)

# Print Accuracy Results
print(f"\nFinal Training Accuracy: {train_acc:.2f}%")
print(f"Final Validation Accuracy: {val_acc:.2f}%")

"""manual testing"""

# batch_size = 32  # Mini-batch size
# loss_function = CrossEntropy()  # Use Cross-Entropy for binary classification

# # Pass one mini-batch through MLP
# for batch_x, batch_y in batch_generator(train_x, train_y, batch_size):

#   print("Beginning Batch")
#   output = MLP.forward(batch_x)  # Run forward pass

#   # print("Batch Input Shape:", batch_x.shape)  # Expected: (32, 10)
#   # print("Batch Labels Shape:", batch_y.shape)  # Expected: (32, 1)
#   # print("MLP Output Shape:", output.shape)  # Expected: (32, 1)
#   # print("First few output values:\n", output[:5])  # Check first few predictions
#   batchloss = loss_function.loss(batch_y, output)
#   print(np.mean(batchloss))

#   test_delta = loss_function.derivative(batch_y, output)

#    # Perform Backward Pass Through Entire MLP
#   dL_dW, dL_db = MLP.backward(test_delta, batch_x)

#     #  Print Gradient Shapes
#   # print("First Layer Weight Gradient Shape:", dL_dW[0].shape)  # Should match first layer's weight shape
#   # print("First Layer Bias Gradient Shape:", dL_db[0].shape)  # Should match first layer's bias shape
#   # print("First Few Weight Gradients:\n", dL_dW[0][:3])  # Check weight updates
#   # print("First Few Bias Gradients:\n", dL_db[0][:3])  # Check bias updates
#   print('Ending Batch')
#   #break  # Stop after the first batch for testing