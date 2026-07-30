"""
Offline question bank - ready-made quizzes that need no AI/API key.

Hand-authored question sets for popular AI/ML topics. Used by the manual
builder so users can load a real quiz with one click when the AI is
unavailable, rate-limited, or when no API key is set.

Each question matches the app's standard schema:
    {question, type, options, correct_answer, concept, difficulty, explanation}
"""

from __future__ import annotations

import copy


BANK: dict[str, list[dict]] = {
    "Neural Network Fundamentals": [
        {
            "question": "What is the role of an activation function in a neural network?",
            "type": "mcq",
            "options": [
                "To introduce non-linearity so the network can model complex patterns",
                "To store the training data",
                "To reduce the number of layers",
                "To label the output classes",
            ],
            "correct_answer": "To introduce non-linearity so the network can model complex patterns",
            "concept": "Neural Network Fundamentals",
            "difficulty": "beginner",
            "explanation": "Without non-linear activations, stacked layers collapse into a single linear transform.",
        },
        {
            "question": "A neuron computes a weighted sum of its inputs plus a bias.",
            "type": "true_false",
            "options": ["True", "False"],
            "correct_answer": "True",
            "concept": "Neural Network Fundamentals",
            "difficulty": "beginner",
            "explanation": "Each neuron outputs activation(w.x + b).",
        },
        {
            "question": "The ___ activation outputs 0 for negative inputs and the input itself for positive inputs.",
            "type": "fill_blank",
            "options": [],
            "correct_answer": "ReLU",
            "concept": "Neural Network Fundamentals",
            "difficulty": "intermediate",
            "explanation": "ReLU (Rectified Linear Unit) is defined as max(0, x).",
        },
        {
            "question": "Which is NOT a common activation function?",
            "type": "mcq",
            "options": ["Sigmoid", "Tanh", "ReLU", "Gradient"],
            "correct_answer": "Gradient",
            "concept": "Neural Network Fundamentals",
            "difficulty": "beginner",
            "explanation": "Gradient is a derivative used in training, not an activation function.",
        },
    ],
}



BANK["Linear & Logistic Regression"] = [
    {
        "question": "What does linear regression predict?",
        "type": "mcq",
        "options": [
            "A continuous numeric value",
            "A discrete category label",
            "A cluster assignment",
            "A probability distribution over words",
        ],
        "correct_answer": "A continuous numeric value",
        "concept": "Linear & Logistic Regression",
        "difficulty": "beginner",
        "explanation": "Linear regression fits a line/plane to predict continuous outputs.",
    },
    {
        "question": "Logistic regression is used for classification, not regression, despite its name.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Linear & Logistic Regression",
        "difficulty": "beginner",
        "explanation": "It applies a sigmoid to model class probabilities.",
    },
    {
        "question": "The ___ function squashes any real number into the range (0, 1).",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "sigmoid",
        "concept": "Linear & Logistic Regression",
        "difficulty": "intermediate",
        "explanation": "The sigmoid (logistic) function maps values to (0, 1) for probabilities.",
    },
    {
        "question": "Which loss is typically used to train logistic regression?",
        "type": "mcq",
        "options": ["Cross-entropy (log loss)", "Mean squared error", "Hinge on raw output", "Silhouette score"],
        "correct_answer": "Cross-entropy (log loss)",
        "concept": "Linear & Logistic Regression",
        "difficulty": "intermediate",
        "explanation": "Log loss penalizes confident wrong probabilities and suits classification.",
    },
]

BANK["Overfitting & Regularization"] = [
    {
        "question": "What is overfitting?",
        "type": "mcq",
        "options": [
            "The model learns noise in training data and generalizes poorly",
            "The model is too simple to fit the data",
            "The model trains too slowly",
            "The dataset is too large",
        ],
        "correct_answer": "The model learns noise in training data and generalizes poorly",
        "concept": "Overfitting & Regularization",
        "difficulty": "beginner",
        "explanation": "Overfit models memorize training data but fail on unseen data.",
    },
    {
        "question": "Adding L2 regularization penalizes large weights.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Overfitting & Regularization",
        "difficulty": "intermediate",
        "explanation": "L2 (ridge) adds a squared-weight penalty, discouraging large weights.",
    },
    {
        "question": "The technique that randomly disables neurons during training is called ___.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "dropout",
        "concept": "Overfitting & Regularization",
        "difficulty": "intermediate",
        "explanation": "Dropout randomly zeroes activations to prevent co-adaptation.",
    },
    {
        "question": "Which signals overfitting?",
        "type": "mcq",
        "options": [
            "Low training error but high validation error",
            "High training and high validation error",
            "Low training and low validation error",
            "Equal training and validation error near zero",
        ],
        "correct_answer": "Low training error but high validation error",
        "concept": "Overfitting & Regularization",
        "difficulty": "beginner",
        "explanation": "A widening train/validation gap is the classic overfitting sign.",
    },
]

BANK["Attention & Transformers"] = [
    {
        "question": "What does self-attention let a model do?",
        "type": "mcq",
        "options": [
            "Weigh the relevance of other tokens when encoding each token",
            "Reduce the vocabulary size",
            "Convert text to images",
            "Eliminate the need for training data",
        ],
        "correct_answer": "Weigh the relevance of other tokens when encoding each token",
        "concept": "Attention & Transformers",
        "difficulty": "intermediate",
        "explanation": "Self-attention computes context-aware representations by attending to all tokens.",
    },
    {
        "question": "Transformers process sequence tokens in parallel rather than strictly one-by-one like RNNs.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Attention & Transformers",
        "difficulty": "intermediate",
        "explanation": "Parallelism over the sequence is a key transformer advantage over RNNs.",
    },
    {
        "question": "Attention scores are computed from queries, keys, and ___.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "values",
        "concept": "Attention & Transformers",
        "difficulty": "advanced",
        "explanation": "Attention uses Query-Key-Value: scores from Q.K weight the V vectors.",
    },
    {
        "question": "Why do transformers add positional encodings?",
        "type": "mcq",
        "options": [
            "Self-attention alone has no inherent notion of token order",
            "To compress the model",
            "To translate between languages",
            "To label the training data",
        ],
        "correct_answer": "Self-attention alone has no inherent notion of token order",
        "concept": "Attention & Transformers",
        "difficulty": "advanced",
        "explanation": "Positional encodings inject order information the attention mechanism lacks.",
    },
]

BANK["Evaluation Metrics"] = [
    {
        "question": "When classes are highly imbalanced, why can accuracy be misleading?",
        "type": "mcq",
        "options": [
            "A model can score high by always predicting the majority class",
            "Accuracy cannot be computed",
            "Accuracy always equals recall",
            "Accuracy ignores the training set",
        ],
        "correct_answer": "A model can score high by always predicting the majority class",
        "concept": "Evaluation Metrics",
        "difficulty": "intermediate",
        "explanation": "With 95% negatives, predicting 'negative' always gives 95% accuracy but is useless.",
    },
    {
        "question": "Recall measures the fraction of actual positives that were correctly identified.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Evaluation Metrics",
        "difficulty": "beginner",
        "explanation": "Recall = TP / (TP + FN).",
    },
    {
        "question": "The harmonic mean of precision and recall is the ___ score.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "F1",
        "concept": "Evaluation Metrics",
        "difficulty": "intermediate",
        "explanation": "F1 balances precision and recall via their harmonic mean.",
    },
]


def list_bank_topics() -> list[str]:
    """Return the available ready-made question set names."""
    return list(BANK.keys())


def get_bank_questions(topic: str) -> list[dict]:
    """
    Return a deep copy of the questions for a topic (empty list if unknown).

    A copy is returned so the caller can edit them without mutating the bank.
    """
    return copy.deepcopy(BANK.get(topic, []))


def total_bank_questions() -> int:
    """Total number of questions across all sets."""
    return sum(len(v) for v in BANK.values())



# --- Additional ready-made sets (appended; BANK is read at call time) ---

BANK["Linear Algebra for ML"] = [
    {
        "question": "What does the dot product of two vectors measure?",
        "type": "mcq",
        "options": ["How aligned they are", "Their total length", "The number of elements", "Their average"],
        "correct_answer": "How aligned they are",
        "concept": "Linear Algebra for ML",
        "difficulty": "beginner",
        "explanation": "The dot product relates to the cosine of the angle between vectors (alignment).",
    },
    {
        "question": "Multiplying a matrix by the identity matrix leaves it unchanged.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Linear Algebra for ML",
        "difficulty": "beginner",
        "explanation": "The identity matrix is the multiplicative identity: A.I = A.",
    },
    {
        "question": "A vector's special directions preserved (only scaled) by a matrix are its ___.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "eigenvectors",
        "concept": "Linear Algebra for ML",
        "difficulty": "advanced",
        "explanation": "Eigenvectors are scaled by their eigenvalues under the transformation.",
    },
]

BANK["Probability & Statistics"] = [
    {
        "question": "What does Bayes' theorem let you compute?",
        "type": "mcq",
        "options": ["A posterior probability from a prior and likelihood", "The mean of a dataset",
                    "The maximum of a function", "A matrix inverse"],
        "correct_answer": "A posterior probability from a prior and likelihood",
        "concept": "Probability & Statistics",
        "difficulty": "intermediate",
        "explanation": "Bayes updates beliefs: posterior is proportional to likelihood times prior.",
    },
    {
        "question": "Variance measures how spread out a distribution is.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Probability & Statistics",
        "difficulty": "beginner",
        "explanation": "Variance is the expected squared deviation from the mean.",
    },
    {
        "question": "The bell-shaped distribution defined by a mean and variance is the ___ distribution.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "normal",
        "concept": "Probability & Statistics",
        "difficulty": "beginner",
        "explanation": "Also called the Gaussian distribution.",
    },
]



BANK["Calculus & Gradients"] = [
    {
        "question": "What does a gradient point toward?",
        "type": "mcq",
        "options": ["The direction of steepest increase", "The minimum of the function",
                    "The origin", "A random direction"],
        "correct_answer": "The direction of steepest increase",
        "concept": "Calculus & Gradients",
        "difficulty": "intermediate",
        "explanation": "Gradient descent steps in the OPPOSITE direction to reduce the loss.",
    },
    {
        "question": "The chain rule is used to differentiate composed functions.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Calculus & Gradients",
        "difficulty": "intermediate",
        "explanation": "It underlies backpropagation through layered networks.",
    },
    {
        "question": "A derivative of a function with respect to one variable (holding others fixed) is a ___ derivative.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "partial",
        "concept": "Calculus & Gradients",
        "difficulty": "beginner",
        "explanation": "Partial derivatives make up the gradient vector.",
    },
]

BANK["Information Theory Basics"] = [
    {
        "question": "What does entropy quantify?",
        "type": "mcq",
        "options": ["Uncertainty in a distribution", "The size of a dataset",
                    "The learning rate", "The number of layers"],
        "correct_answer": "Uncertainty in a distribution",
        "concept": "Information Theory Basics",
        "difficulty": "intermediate",
        "explanation": "Higher entropy means more unpredictability.",
    },
    {
        "question": "Cross-entropy is commonly used as a classification loss function.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Information Theory Basics",
        "difficulty": "intermediate",
        "explanation": "It measures the gap between predicted and true label distributions.",
    },
    {
        "question": "The measure of how one probability distribution differs from another is the ___ divergence.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "KL",
        "concept": "Information Theory Basics",
        "difficulty": "advanced",
        "explanation": "Kullback-Leibler (KL) divergence; note it is not symmetric.",
    },
]



BANK["Decision Trees & Random Forests"] = [
    {
        "question": "How does a decision tree decide where to split?",
        "type": "mcq",
        "options": ["By maximizing purity (e.g. reducing Gini/entropy)", "Randomly",
                    "By sorting the labels", "By minimizing the tree depth only"],
        "correct_answer": "By maximizing purity (e.g. reducing Gini/entropy)",
        "concept": "Decision Trees & Random Forests",
        "difficulty": "intermediate",
        "explanation": "Splits are chosen to make child nodes as class-pure as possible.",
    },
    {
        "question": "A random forest combines many decision trees to reduce overfitting.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Decision Trees & Random Forests",
        "difficulty": "beginner",
        "explanation": "Averaging many de-correlated trees lowers variance.",
    },
    {
        "question": "Training each tree on a random sample of the data (with replacement) is called ___.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "bagging",
        "concept": "Decision Trees & Random Forests",
        "difficulty": "advanced",
        "explanation": "Bagging = bootstrap aggregating.",
    },
]

BANK["Support Vector Machines"] = [
    {
        "question": "What does an SVM try to maximize?",
        "type": "mcq",
        "options": ["The margin between classes", "The number of support vectors",
                    "The tree depth", "The learning rate"],
        "correct_answer": "The margin between classes",
        "concept": "Support Vector Machines",
        "difficulty": "intermediate",
        "explanation": "SVMs find the maximum-margin separating hyperplane.",
    },
    {
        "question": "The kernel trick lets SVMs separate data that isn't linearly separable.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Support Vector Machines",
        "difficulty": "advanced",
        "explanation": "Kernels implicitly map inputs to a higher-dimensional space.",
    },
    {
        "question": "The data points closest to the decision boundary are called ___ vectors.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "support",
        "concept": "Support Vector Machines",
        "difficulty": "beginner",
        "explanation": "Only support vectors determine the boundary.",
    },
]



BANK["Clustering (k-Means, DBSCAN)"] = [
    {
        "question": "What must you specify in advance for k-means?",
        "type": "mcq",
        "options": ["The number of clusters k", "The class labels",
                    "The learning rate", "The tree depth"],
        "correct_answer": "The number of clusters k",
        "concept": "Clustering (k-Means, DBSCAN)",
        "difficulty": "beginner",
        "explanation": "k-means needs k up front; DBSCAN does not.",
    },
    {
        "question": "DBSCAN can find clusters of arbitrary shape and label outliers as noise.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Clustering (k-Means, DBSCAN)",
        "difficulty": "intermediate",
        "explanation": "DBSCAN is density-based, unlike k-means' spherical clusters.",
    },
    {
        "question": "Clustering is an example of ___ learning (no labels).",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "unsupervised",
        "concept": "Clustering (k-Means, DBSCAN)",
        "difficulty": "beginner",
        "explanation": "No target labels are used.",
    },
]

BANK["Dimensionality Reduction (PCA)"] = [
    {
        "question": "What does PCA do?",
        "type": "mcq",
        "options": ["Projects data onto directions of maximum variance", "Adds new features",
                    "Labels the data", "Increases dimensionality"],
        "correct_answer": "Projects data onto directions of maximum variance",
        "concept": "Dimensionality Reduction (PCA)",
        "difficulty": "intermediate",
        "explanation": "Principal components capture the most variance in fewer dimensions.",
    },
    {
        "question": "PCA components are the eigenvectors of the data's covariance matrix.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Dimensionality Reduction (PCA)",
        "difficulty": "advanced",
        "explanation": "Eigenvalues indicate the variance captured by each component.",
    },
    {
        "question": "As the number of features grows, models suffer from the curse of ___.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "dimensionality",
        "concept": "Dimensionality Reduction (PCA)",
        "difficulty": "intermediate",
        "explanation": "High dimensions make data sparse and distances less meaningful.",
    },
]



BANK["Gradient Descent & Optimizers"] = [
    {
        "question": "What does the learning rate control?",
        "type": "mcq",
        "options": ["The step size of each parameter update", "The number of layers",
                    "The batch size", "The number of classes"],
        "correct_answer": "The step size of each parameter update",
        "concept": "Gradient Descent & Optimizers",
        "difficulty": "beginner",
        "explanation": "Too high overshoots; too low trains slowly.",
    },
    {
        "question": "Stochastic gradient descent updates weights using mini-batches instead of the full dataset.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Gradient Descent & Optimizers",
        "difficulty": "intermediate",
        "explanation": "Mini-batches speed up and regularize training.",
    },
    {
        "question": "The popular optimizer combining momentum and adaptive rates is ___.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "Adam",
        "concept": "Gradient Descent & Optimizers",
        "difficulty": "intermediate",
        "explanation": "Adam = Adaptive Moment Estimation.",
    },
]

BANK["Cross-Validation & Data Splits"] = [
    {
        "question": "Why hold out a separate test set?",
        "type": "mcq",
        "options": ["To estimate performance on unseen data", "To train faster",
                    "To increase accuracy", "To reduce the model size"],
        "correct_answer": "To estimate performance on unseen data",
        "concept": "Cross-Validation & Data Splits",
        "difficulty": "beginner",
        "explanation": "The test set must not influence training or tuning.",
    },
    {
        "question": "Tuning hyperparameters on the test set causes data leakage.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Cross-Validation & Data Splits",
        "difficulty": "intermediate",
        "explanation": "Use a validation set (or cross-validation) for tuning instead.",
    },
    {
        "question": "Splitting data into k parts and rotating the validation fold is called k-fold ___.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "cross-validation",
        "concept": "Cross-Validation & Data Splits",
        "difficulty": "intermediate",
        "explanation": "Each fold serves as validation once; results are averaged.",
    },
]



BANK["Backpropagation"] = [
    {
        "question": "What does backpropagation compute?",
        "type": "mcq",
        "options": ["Gradients of the loss w.r.t. each weight", "The learning rate",
                    "The number of epochs", "The activation function"],
        "correct_answer": "Gradients of the loss w.r.t. each weight",
        "concept": "Backpropagation",
        "difficulty": "advanced",
        "explanation": "It propagates error backward using the chain rule.",
    },
    {
        "question": "Backpropagation relies on the chain rule of calculus.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Backpropagation",
        "difficulty": "intermediate",
        "explanation": "Gradients are chained layer by layer from output to input.",
    },
    {
        "question": "The forward pass computes predictions; the ___ pass computes gradients.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "backward",
        "concept": "Backpropagation",
        "difficulty": "beginner",
        "explanation": "Backward pass = backpropagation of error.",
    },
]

BANK["Convolutional Neural Networks"] = [
    {
        "question": "Why are CNNs well suited to images?",
        "type": "mcq",
        "options": ["Filters detect local spatial patterns and share weights", "They need no training",
                    "They ignore pixel positions", "They only work on text"],
        "correct_answer": "Filters detect local spatial patterns and share weights",
        "concept": "Convolutional Neural Networks",
        "difficulty": "intermediate",
        "explanation": "Weight sharing and locality make CNNs efficient for images.",
    },
    {
        "question": "Pooling layers reduce the spatial size of feature maps.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Convolutional Neural Networks",
        "difficulty": "beginner",
        "explanation": "Max/average pooling downsamples and adds invariance.",
    },
    {
        "question": "The small weight matrix slid across an image in a CNN is called a filter or ___.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "kernel",
        "concept": "Convolutional Neural Networks",
        "difficulty": "beginner",
        "explanation": "Kernel and filter are used interchangeably.",
    },
]



BANK["Recurrent Networks & LSTMs"] = [
    {
        "question": "What are RNNs designed to process?",
        "type": "mcq",
        "options": ["Sequential data", "Only images", "Only tabular data", "Static single inputs"],
        "correct_answer": "Sequential data",
        "concept": "Recurrent Networks & LSTMs",
        "difficulty": "beginner",
        "explanation": "RNNs maintain a hidden state across time steps.",
    },
    {
        "question": "LSTMs use gates to help preserve long-term dependencies.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Recurrent Networks & LSTMs",
        "difficulty": "intermediate",
        "explanation": "Input, forget, and output gates control the cell state.",
    },
    {
        "question": "Plain RNNs struggle to learn long sequences due to the ___ gradient problem.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "vanishing",
        "concept": "Recurrent Networks & LSTMs",
        "difficulty": "advanced",
        "explanation": "Gradients shrink over many time steps; LSTMs mitigate this.",
    },
]

BANK["Regularization in Deep Nets"] = [
    {
        "question": "What does batch normalization help with?",
        "type": "mcq",
        "options": ["Stabilizing and speeding up training", "Labeling data",
                    "Reducing the dataset size", "Choosing the learning rate automatically"],
        "correct_answer": "Stabilizing and speeding up training",
        "concept": "Regularization in Deep Nets",
        "difficulty": "intermediate",
        "explanation": "It normalizes layer inputs, smoothing optimization.",
    },
    {
        "question": "Data augmentation increases effective training data by transforming examples.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Regularization in Deep Nets",
        "difficulty": "beginner",
        "explanation": "E.g. flips, crops, and rotations for images.",
    },
    {
        "question": "Randomly zeroing neurons during training to prevent co-adaptation is called ___.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "dropout",
        "concept": "Regularization in Deep Nets",
        "difficulty": "intermediate",
        "explanation": "Dropout is a widely used deep-net regularizer.",
    },
]



BANK["Text Preprocessing & Embeddings"] = [
    {
        "question": "What is a word embedding?",
        "type": "mcq",
        "options": ["A dense vector capturing a word's meaning", "A count of letters",
                    "A grammar rule", "A translation table"],
        "correct_answer": "A dense vector capturing a word's meaning",
        "concept": "Text Preprocessing & Embeddings",
        "difficulty": "intermediate",
        "explanation": "Embeddings place similar words near each other in vector space.",
    },
    {
        "question": "Tokenization splits text into smaller units like words or subwords.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Text Preprocessing & Embeddings",
        "difficulty": "beginner",
        "explanation": "Tokens are the model's input units.",
    },
    {
        "question": "The weighting scheme that boosts rare, informative words is ___.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "TF-IDF",
        "concept": "Text Preprocessing & Embeddings",
        "difficulty": "intermediate",
        "explanation": "Term Frequency-Inverse Document Frequency.",
    },
]

BANK["How LLMs Work"] = [
    {
        "question": "What core task are most LLMs pretrained on?",
        "type": "mcq",
        "options": ["Predicting the next token", "Sorting numbers",
                    "Classifying images", "Clustering documents"],
        "correct_answer": "Predicting the next token",
        "concept": "How LLMs Work",
        "difficulty": "intermediate",
        "explanation": "Next-token prediction over huge text corpora.",
    },
    {
        "question": "The context window limits how much text an LLM can consider at once.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "How LLMs Work",
        "difficulty": "beginner",
        "explanation": "Measured in tokens; longer context costs more compute.",
    },
    {
        "question": "Adapting a pretrained model to a specific task with more training is called ___.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "fine-tuning",
        "concept": "How LLMs Work",
        "difficulty": "intermediate",
        "explanation": "Fine-tuning specializes a base model.",
    },
]



BANK["Prompt Engineering"] = [
    {
        "question": "What is few-shot prompting?",
        "type": "mcq",
        "options": ["Giving the model a few examples in the prompt", "Training on few images",
                    "Using a small model", "Asking very short questions"],
        "correct_answer": "Giving the model a few examples in the prompt",
        "concept": "Prompt Engineering",
        "difficulty": "beginner",
        "explanation": "Examples in-context guide the model's output format and behavior.",
    },
    {
        "question": "Asking a model to 'think step by step' is an example of chain-of-thought prompting.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Prompt Engineering",
        "difficulty": "intermediate",
        "explanation": "It encourages intermediate reasoning, often improving accuracy.",
    },
    {
        "question": "The sampling parameter that controls output randomness is ___.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "temperature",
        "concept": "Prompt Engineering",
        "difficulty": "intermediate",
        "explanation": "Lower is more deterministic; higher is more creative.",
    },
]

BANK["RAG & Fine-Tuning"] = [
    {
        "question": "What does Retrieval-Augmented Generation (RAG) do?",
        "type": "mcq",
        "options": ["Fetches relevant documents to ground the model's answer", "Retrains the model each query",
                    "Removes the need for a model", "Compresses the prompt"],
        "correct_answer": "Fetches relevant documents to ground the model's answer",
        "concept": "RAG & Fine-Tuning",
        "difficulty": "advanced",
        "explanation": "RAG retrieves context (often via embeddings) to reduce hallucination.",
    },
    {
        "question": "RAG can add up-to-date knowledge without retraining the model.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "RAG & Fine-Tuning",
        "difficulty": "intermediate",
        "explanation": "You update the knowledge base, not the model weights.",
    },
    {
        "question": "RAG typically searches a ___ database of embeddings to find relevant text.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "vector",
        "concept": "RAG & Fine-Tuning",
        "difficulty": "advanced",
        "explanation": "Vector databases enable semantic similarity search.",
    },
]



BANK["Feature Engineering"] = [
    {
        "question": "Why scale/normalize features before training many models?",
        "type": "mcq",
        "options": ["So features on different ranges contribute fairly", "To add more data",
                    "To reduce accuracy", "To label the data"],
        "correct_answer": "So features on different ranges contribute fairly",
        "concept": "Feature Engineering",
        "difficulty": "beginner",
        "explanation": "Unscaled features can dominate distance- and gradient-based methods.",
    },
    {
        "question": "One-hot encoding converts categorical variables into binary columns.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Feature Engineering",
        "difficulty": "beginner",
        "explanation": "Each category becomes its own 0/1 feature.",
    },
    {
        "question": "Filling in absent values in a dataset is called handling ___ values.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "missing",
        "concept": "Feature Engineering",
        "difficulty": "beginner",
        "explanation": "Via imputation (mean, median, model-based, etc.).",
    },
]

BANK["Model Deployment & MLOps"] = [
    {
        "question": "What is model drift?",
        "type": "mcq",
        "options": ["Performance degrading as real-world data changes over time", "A faster training method",
                    "A type of neural layer", "A data labeling tool"],
        "correct_answer": "Performance degrading as real-world data changes over time",
        "concept": "Model Deployment & MLOps",
        "difficulty": "intermediate",
        "explanation": "Data/concept drift means the live distribution diverges from training.",
    },
    {
        "question": "Monitoring a deployed model in production is an important MLOps practice.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Model Deployment & MLOps",
        "difficulty": "beginner",
        "explanation": "You track latency, errors, and prediction quality/drift.",
    },
    {
        "question": "Packaging a model and its dependencies into a portable unit often uses ___.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "containers",
        "concept": "Model Deployment & MLOps",
        "difficulty": "intermediate",
        "explanation": "E.g. Docker containers for reproducible deployment.",
    },
]



BANK["Reinforcement Learning Basics"] = [
    {
        "question": "In reinforcement learning, what does an agent try to maximize?",
        "type": "mcq",
        "options": ["Cumulative reward", "Training loss",
                    "The number of states", "The learning rate"],
        "correct_answer": "Cumulative reward",
        "concept": "Reinforcement Learning Basics",
        "difficulty": "intermediate",
        "explanation": "The agent learns a policy that maximizes long-term reward.",
    },
    {
        "question": "The tension between trying new actions and using known good ones is the exploration-exploitation tradeoff.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "Reinforcement Learning Basics",
        "difficulty": "intermediate",
        "explanation": "Too little exploration can trap the agent in suboptimal behavior.",
    },
    {
        "question": "The signal an environment gives an agent after an action is called the ___.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "reward",
        "concept": "Reinforcement Learning Basics",
        "difficulty": "beginner",
        "explanation": "Rewards guide which behaviors the agent reinforces.",
    },
]

BANK["AI Ethics & Bias"] = [
    {
        "question": "Where does model bias most often originate?",
        "type": "mcq",
        "options": ["Biased or unrepresentative training data", "Using a GPU",
                    "Too many layers", "A high learning rate"],
        "correct_answer": "Biased or unrepresentative training data",
        "concept": "AI Ethics & Bias",
        "difficulty": "beginner",
        "explanation": "Models learn and can amplify patterns present in their data.",
    },
    {
        "question": "Model interpretability helps stakeholders understand why a model made a decision.",
        "type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "concept": "AI Ethics & Bias",
        "difficulty": "intermediate",
        "explanation": "Important for trust, debugging, and accountability.",
    },
    {
        "question": "Protecting individuals' personal data in ML systems concerns their ___.",
        "type": "fill_blank",
        "options": [],
        "correct_answer": "privacy",
        "concept": "AI Ethics & Bias",
        "difficulty": "beginner",
        "explanation": "Privacy-preserving techniques limit exposure of personal data.",
    },
]
