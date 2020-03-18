import numpy as np
import pandas as pd


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def d_sigmoid(x):
    fx = sigmoid(x)
    return fx*(1-fx)


def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)


def d_softmax(x):
    return np.ones(len(x))


def create_expected_output_from_label(num_classes, label):
    v = [0]*num_classes
    v[int(label)] = 1
    return v


def classify(output):
    highest_prob = 0
    guess = 0
    # Select the number with highest probability
    for j in range(len(output)):
        if output[j] > highest_prob:
            highest_prob = output[j]
            guess = j

    return guess


if __name__ == "__main__":
    LAYER_SIZES = [256, 10]
    INPUT_SIZE = 28*28
    LEARNING_RATE = 0.01
    # HIDDEN_LAYERS = 2
    # LAYERS = []

    data = pd.read_csv("assignment5.csv").to_numpy()
    input_vectors = [np.divide(row[1:], 255) for row in data]
    labels = [row[0] for row in data]

    train_index = int(len(input_vectors)*0.1*7)
    validation_index = int(len(input_vectors)*0.1*8)
    testing_index = len(input_vectors)-1

    np.random.seed(1)
    synapses = []
    biases = []
    # Insert the input vector as a "layer" so we get the correct amount of weights
    LAYER_SIZES.insert(0, INPUT_SIZE)
    # Create the synapses with random weight (-1 to 1) for all layers
    for i in range(len(LAYER_SIZES)-1):
        synapses.append(2*np.random.rand(LAYER_SIZES[i], LAYER_SIZES[i+1]) - 1)
        biases.append(2*np.random.random(LAYER_SIZES[i+1])-1)

    batch_size = 10
    batch_deltas = np.copy(synapses) * 0
    batch_biases = np.copy(biases) * 0
    accuracy = 0
    epochs = 0
    # One epoch
    while accuracy < 0.85:
        correct_guesses_training = 0
        # Feed training dataset through network
        for i in range(train_index):
            # Fetch the input
            x = input_vectors[i]

            # Set the first "layer" to be the input vector
            layers = [x]
            # Feed forward all hidden layers
            for j, syn in enumerate(synapses[:-1]):
                layers.append(sigmoid(np.add(np.dot(layers[-1], syn), biases[j])))
            # Feed forward through the output layer
            layers.append(softmax(np.add(np.dot(layers[-1], synapses[-1]), biases[-1])))

            if classify(layers[-1]) == labels[i]:
                correct_guesses_training += 1

            # Create the target vector
            target = np.zeros(10)
            target[labels[i]] = 1
            # Calculate error for output layer
            error_terms = [(target - layers[-1]) * d_softmax(layers[-1])]
            # Create the error terms for remaining layers
            for l in range(len(layers)-2, 0, -1):
                error_terms.insert(0,  np.dot(error_terms[0], synapses[l].T) * d_sigmoid(layers[l]))

            # For each set of synapses connecting the layers
            for s in range(len(synapses)):
                # Update the weight based on error term of target node and input of source node
                # synapses[s] += (np.dot(error_terms[s][:,None], layers[s][None,:])).T
                # synapses[s] += (np.dot(layers[s][:,None], error_terms[s][None,:]) * LEARNING_RATE)
                batch_deltas[s] += (np.dot(layers[s][:,None], error_terms[s][None,:]) * LEARNING_RATE)
                # Also update the biases based on the error term
                batch_biases[s] += error_terms[s] * LEARNING_RATE
                # biases[s] += error_terms[s] * LEARNING_RATE

            # Batch update biases and weights
            if (i % batch_size == 0 and i != 0) or i == train_index-1:
                # print(f"Performing batch update.")
                synapses += batch_deltas
                biases += batch_biases
                batch_deltas = batch_deltas * 0
                batch_biases = batch_biases * 0

            if i % 1000 == 0 and i != 0:
                print(f"Accuracy after {i} iterations: {correct_guesses_training / i}")

        correct_classifications = 0
        # Validate results
        for i in range(train_index, validation_index):
            # Fetch the input
            x = input_vectors[i]
            # Set the first "layer" to be the input vector
            layers = [x]
            # Feed forward all hidden layers
            for j, syn in enumerate(synapses[:-1]):
                layers.append(sigmoid(np.dot(layers[-1], syn) + biases[j]))
            # Feed forward through the output layer
            layers.append(softmax(np.dot(layers[-1], synapses[-1]) + biases[-1]))

            highest_prob = 0
            # Check if the classifier guessed right
            if labels[i] == classify(layers[-1]):
                correct_classifications += 1

        # Update the accuracy of the network
        accuracy = correct_classifications / (validation_index - train_index)
        epochs += 1
        print(f"Epochs: {epochs}, accuracy: {accuracy}")

    # Training finished, now test on the testing data
    correct_classifications = 0
    for i in range(validation_index, testing_index):
        # Fetch the input
        x = input_vectors[i]
        # Set the first "layer" to be the input vector
        layers = [x]
        # Feed forward all hidden layers
        for j, syn in enumerate(synapses[:-1]):
            layers.append(sigmoid(np.dot(layers[-1], syn) + biases[j]))
        # Feed forward through the output layer
        layers.append(softmax(np.dot(layers[-1], synapses[-1]) + biases[-1]))

        highest_prob = 0
        # Check if the classifier guessed right
        if labels[i] == classify(layers[-1]):
            correct_classifications += 1

    # Update the accuracy of the network
    accuracy = correct_classifications / (testing_index - validation_index)
    print(f"Testing data accuracy: {accuracy}")
