import numpy as np
import pandas as pd
from random import random
from math import exp

class Neuron:
    def __init__(self, x, y):
        self.input = x
        self.output = y


class NeuralNetwork:
    def __init__(self, input_vector_size, fx_hidden, dfx_hidden, fx_output, dfx_output, layer_sizes, num_layers=2):
        """
        :param input_size:
        :param fx_hidden:
        :param fx_output:
        :param num_layers:
        :param layer_sizes:
        """
        # Check if the number of provided sizes are the same as the numbers of layers in the network
        if layer_sizes is not None and len(layer_sizes) != num_layers:
            raise ValueError("Not all hidden layers where given a size. Make sure that the amount of hidden layer sizes"
                             " is the same as num_layers-1.\n"
                             f"Number of layers specified (including output layer): {num_layers}\n"
                             f"Number of hidden layer sizes specified: {len(layer_sizes)} - {layer_sizes}")

        # Note: The last element in layer_sizes is the output layer, which should have the same amount of
        # neurons as classes the ANN have to predict
        self.layer_sizes = layer_sizes
        self.input_vector_size = input_vector_size
        # Activation function and its derivative for the hidden layers
        self.fx_hidden = fx_hidden
        self.dfx_hidden = fx_hidden
        # Activation function and its derivative for the output layer
        self.fx_output = fx_output
        self.dfx_output = fx_hidden

        # Each index in layers is an array of neurons ([[input_1,...,input_n],output] lists), in the layer at that index
        self.layers = [[ [[],0] for _ in range(ls)] for ls in self.layer_sizes]

        # Array of arrays of weights from layer i-1 node j (or input j) to layer i node k, where i is
        # the index in the weights array, j is the node in layer i-1, and k is node in layer i.
        # E.g. Index i=0 and j=1 (weights[0][1]) in the weights array gives an array of length len(self.layers[i])
        # with all the weights from the second (since j=1) INPUT in the input layer to each of the neurons in
        # the first layer.
        # E.g. Index i=3 and j=0, gives an array of length len(self.layers[i]) with all the weights from the
        # first (j=0) neuron in the third (i=2) layer, to the neurons in the fourth layer (i=3)
        self.weights = [
            [random() for _ in range(self.input_vector_size)],  # Initialize weights from input vector to the first hidden layer
            [[random() for _ in range(ls)] for ls in self.layer_sizes]  # Initialize the weights for each of the remaining layers
        ]

        self.outputs = []

        # Biases and weights ([b,v] list) into node j in layer i.
        # E.g. The bias for the second node in the third layer is: self.biases[2][1][0]
        # E.g. The weight for the second node in the third layer is: self.biases[2][1][1]
        self.biases = [[[1.0,0.5] for _ in l] for l in self.layers]

        # Learning rate
        self.eta = 1

    def feed_forward(self, x):
        """
        :param x: The input vector used to calculate a predicted output in the ANN
        :return: Return the predicted output vector
        """
        if len(x) != self.input_vector_size:
            raise ValueError(f"The size of the input vector x (size {len(x)}) is not supported in "
                             f"the configuration of this neural network. Input vector must be of"
                             f" size {self.input_vector_size}.")
        # #  Calculate the input for the first hidden layer, which is based on the input layer
        # for neuron_index in range(len(self.layers[0])):
        #     bias_input = self.biases[0][neuron_index][0] * self.biases[0][neuron_index][1]
        #     inputs = []
        #     for i in range(len(x)):
        #         inputs.append((x[i] * self.weights[0][i]))
        #     # Set the input to the neuron (just for traceability)
        #     self.layers[0][neuron_index][0] = inputs
        #     # Set the output from the neuron
        #     self.layers[0][neuron_index][1] = self.fx_output(bias_input + sum(inputs))

        for i, layer in enumerate(self.layers[1:]):
            for neuron_index in range(len(layer)):
                bias_input = self.biases[i][neuron_index][0] * self.biases[i][neuron_index][1]
                inputs = []
                # Check if we should use the input layer as input to the first hidden layer
                if i == 0:
                    for j in range(len(x)):
                        inputs.append((x[j] * self.weights[i][j]))
                # Else we feed forward to the next layer based on the outputs from the previous layer
                else:
                    # For each neuron in the previous layer, take the output and multiply by the weight and store it
                    # as an input to the neuron self.layers[i][neuron_index]
                    for j in range(len(self.layers[i-1])):
                        inputs.append((self.layers[i-1][j][1] * self.weights[i][j]))

                # Set the input to the neuron (for traceability)
                self.layers[i][neuron_index][0] = inputs
                # Set the output from the neuron
                self.layers[i][neuron_index][1] = self.fx_output(bias_input + sum(inputs))

    def backpropagation(self):
        pass


def sigmoid(x):
    return 1 / (1 + exp(-x))


def d_sigmoid(x):
    fx = sigmoid(x)
    return fx*(1-fx)


def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)


def d_softmax(x):
    return 1


if __name__=="__main__":
    LAYER_SIZES = [500, 100]
    # HIDDEN_LAYERS = 2
    # LAYERS = []

    data = pd.read_csv("assignment5.csv").to_numpy()
    input_vectors = [np.div(row[1:], 255) for row in data]
    labels = [row[0] for row in data]

    big_brain = NeuralNetwork(28*28, sigmoid, d_sigmoid, softmax, d_softmax, LAYER_SIZES)
    print(input_vectors)

    # print(df.head(5))
    # print(df["label"][0])



