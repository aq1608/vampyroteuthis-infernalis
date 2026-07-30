"""
AI/ML Curriculum - Pre-loaded learning paths and topics.

Provides a structured curriculum of AI/ML topics organized into
learning paths, so students can pick a ready-made topic instead of
typing their own. Each topic includes a rich prompt seed that guides
the AI to generate a focused, high-quality quiz.
"""

from __future__ import annotations


# Each learning path contains ordered topics (beginner -> advanced).
# Each topic has:
#   - name: short label shown in the dropdown
#   - level: difficulty tier for ordering/labeling
#   - description: the seed used to generate study content + quiz
CURRICULUM: dict[str, dict] = {
    "Foundations & Math": {
        "icon": "abacus",
        "blurb": "The math and stats backbone every ML practitioner needs.",
        "topics": [
            {
                "name": "Linear Algebra for ML",
                "level": "beginner",
                "description": (
                    "Linear algebra fundamentals for machine learning: vectors, "
                    "matrices, matrix multiplication, dot products, transpose, "
                    "identity and inverse matrices, eigenvalues and eigenvectors, "
                    "and why these operations matter for representing data and "
                    "transformations in ML models."
                ),
            },
            {
                "name": "Probability & Statistics",
                "level": "beginner",
                "description": (
                    "Probability and statistics for machine learning: random "
                    "variables, probability distributions (normal, Bernoulli, "
                    "binomial), expectation and variance, conditional probability, "
                    "Bayes' theorem, sampling, and hypothesis testing basics."
                ),
            },
            {
                "name": "Calculus & Gradients",
                "level": "intermediate",
                "description": (
                    "Calculus for machine learning: derivatives, partial "
                    "derivatives, the gradient, the chain rule, and how gradients "
                    "are used to minimize loss functions during model training."
                ),
            },
            {
                "name": "Information Theory Basics",
                "level": "intermediate",
                "description": (
                    "Information theory concepts used in ML: entropy, "
                    "cross-entropy, Kullback-Leibler (KL) divergence, mutual "
                    "information, and how these quantify uncertainty and are used "
                    "in loss functions and decision trees."
                ),
            },
        ],
    },
    "Classical Machine Learning": {
        "icon": "chart_with_upwards_trend",
        "blurb": "Core supervised and unsupervised algorithms.",
        "topics": [
            {
                "name": "Linear & Logistic Regression",
                "level": "beginner",
                "description": (
                    "Linear regression and logistic regression: the linear model, "
                    "cost functions (mean squared error, log loss), fitting with "
                    "gradient descent, the sigmoid function, decision boundaries, "
                    "and the difference between regression and classification."
                ),
            },
            {
                "name": "Decision Trees & Random Forests",
                "level": "beginner",
                "description": (
                    "Decision trees and random forests: how trees split on "
                    "features using Gini impurity or entropy, overfitting in trees, "
                    "ensemble learning, bagging, and how random forests combine "
                    "many trees to improve generalization."
                ),
            },
            {
                "name": "Support Vector Machines",
                "level": "intermediate",
                "description": (
                    "Support vector machines (SVMs): the maximum-margin "
                    "hyperplane, support vectors, the kernel trick, linear vs "
                    "non-linear kernels (RBF, polynomial), and soft-margin "
                    "classification with the C parameter."
                ),
            },
            {
                "name": "Clustering (k-Means, DBSCAN)",
                "level": "intermediate",
                "description": (
                    "Unsupervised clustering: k-means algorithm and centroid "
                    "updates, choosing k with the elbow method, DBSCAN "
                    "density-based clustering, and comparing clustering approaches "
                    "for different data shapes."
                ),
            },
            {
                "name": "Dimensionality Reduction (PCA)",
                "level": "intermediate",
                "description": (
                    "Dimensionality reduction: the curse of dimensionality, "
                    "Principal Component Analysis (PCA), explained variance, "
                    "principal components as eigenvectors of the covariance "
                    "matrix, and t-SNE for visualization."
                ),
            },
        ],
    },
    "Model Training & Evaluation": {
        "icon": "straight_ruler",
        "blurb": "How to train models well and measure them honestly.",
        "topics": [
            {
                "name": "Gradient Descent & Optimizers",
                "level": "intermediate",
                "description": (
                    "Optimization for ML: batch, stochastic, and mini-batch "
                    "gradient descent, learning rate, momentum, and modern "
                    "optimizers like RMSProp and Adam, plus how they speed up "
                    "and stabilize training."
                ),
            },
            {
                "name": "Overfitting & Regularization",
                "level": "beginner",
                "description": (
                    "The bias-variance tradeoff, overfitting vs underfitting, "
                    "L1 (Lasso) and L2 (Ridge) regularization, dropout, and early "
                    "stopping as techniques to improve generalization."
                ),
            },
            {
                "name": "Evaluation Metrics",
                "level": "beginner",
                "description": (
                    "Model evaluation metrics: accuracy, precision, recall, "
                    "F1-score, the confusion matrix, ROC curves and AUC, and when "
                    "to prefer each metric depending on class imbalance and the "
                    "cost of errors."
                ),
            },
            {
                "name": "Cross-Validation & Data Splits",
                "level": "beginner",
                "description": (
                    "Validation strategy: train/validation/test splits, k-fold "
                    "cross-validation, stratified sampling, data leakage, and how "
                    "to tune hyperparameters without overfitting the test set."
                ),
            },
        ],
    },
    "Deep Learning": {
        "icon": "brain",
        "blurb": "Neural networks and the architectures that power modern AI.",
        "topics": [
            {
                "name": "Neural Network Fundamentals",
                "level": "intermediate",
                "description": (
                    "Neural network basics: the perceptron, layers and neurons, "
                    "weights and biases, activation functions (ReLU, sigmoid, "
                    "tanh), forward propagation, and how networks approximate "
                    "complex functions."
                ),
            },
            {
                "name": "Backpropagation",
                "level": "advanced",
                "description": (
                    "Backpropagation: how neural networks learn by propagating "
                    "error gradients backward using the chain rule, updating "
                    "weights via gradient descent, and the role of the loss "
                    "function and learning rate."
                ),
            },
            {
                "name": "Convolutional Neural Networks",
                "level": "advanced",
                "description": (
                    "Convolutional Neural Networks (CNNs): convolution and "
                    "filters/kernels, feature maps, pooling layers, stride and "
                    "padding, and why CNNs excel at image and spatial data."
                ),
            },
            {
                "name": "Recurrent Networks & LSTMs",
                "level": "advanced",
                "description": (
                    "Recurrent Neural Networks (RNNs) and LSTMs: modeling "
                    "sequences, hidden states, the vanishing gradient problem, "
                    "and how LSTM gates (input, forget, output) preserve "
                    "long-term dependencies."
                ),
            },
            {
                "name": "Regularization in Deep Nets",
                "level": "advanced",
                "description": (
                    "Deep learning regularization: dropout, batch normalization, "
                    "data augmentation, weight decay, and gradient clipping, and "
                    "how each stabilizes training and reduces overfitting."
                ),
            },
        ],
    },
    "NLP & Large Language Models": {
        "icon": "speech_balloon",
        "blurb": "From word embeddings to transformers and modern LLMs.",
        "topics": [
            {
                "name": "Text Preprocessing & Embeddings",
                "level": "intermediate",
                "description": (
                    "NLP foundations: tokenization, stemming and lemmatization, "
                    "bag-of-words, TF-IDF, and word embeddings like Word2Vec and "
                    "GloVe that capture semantic meaning as vectors."
                ),
            },
            {
                "name": "Attention & Transformers",
                "level": "advanced",
                "description": (
                    "The Transformer architecture: self-attention, query-key-"
                    "value, multi-head attention, positional encoding, and why "
                    "transformers replaced RNNs for most NLP tasks."
                ),
            },
            {
                "name": "How LLMs Work",
                "level": "advanced",
                "description": (
                    "Large Language Models: pretraining on next-token "
                    "prediction, tokens and context windows, parameters and "
                    "scale, fine-tuning, and the difference between base and "
                    "instruction-tuned models."
                ),
            },
            {
                "name": "Prompt Engineering",
                "level": "beginner",
                "description": (
                    "Prompt engineering for LLMs: zero-shot vs few-shot "
                    "prompting, chain-of-thought reasoning, system prompts, "
                    "temperature and sampling, and techniques to get reliable "
                    "outputs."
                ),
            },
            {
                "name": "RAG & Fine-Tuning",
                "level": "advanced",
                "description": (
                    "Adapting LLMs: Retrieval-Augmented Generation (RAG) with "
                    "vector databases and embeddings, when to fine-tune vs use "
                    "RAG, and parameter-efficient methods like LoRA."
                ),
            },
        ],
    },
    "Applied AI & MLOps": {
        "icon": "gear",
        "blurb": "Putting models into the real world responsibly.",
        "topics": [
            {
                "name": "Feature Engineering",
                "level": "intermediate",
                "description": (
                    "Feature engineering: encoding categorical variables, "
                    "scaling and normalization, handling missing values, feature "
                    "selection, and creating informative features that improve "
                    "model performance."
                ),
            },
            {
                "name": "Model Deployment & MLOps",
                "level": "intermediate",
                "description": (
                    "MLOps basics: serving models via APIs, containerization, "
                    "model versioning, monitoring for data and concept drift, and "
                    "CI/CD pipelines for machine learning."
                ),
            },
            {
                "name": "Reinforcement Learning Basics",
                "level": "advanced",
                "description": (
                    "Reinforcement learning: agents, environments, states, "
                    "actions, rewards, the exploration-exploitation tradeoff, "
                    "Q-learning, and the policy vs value function distinction."
                ),
            },
            {
                "name": "AI Ethics & Bias",
                "level": "beginner",
                "description": (
                    "Responsible AI: sources of bias in data and models, "
                    "fairness metrics, model interpretability and explainability, "
                    "privacy, and the societal impact of deploying AI systems."
                ),
            },
        ],
    },
}


def get_learning_paths() -> list[str]:
    """Return the list of learning path names."""
    return list(CURRICULUM.keys())


def get_path_info(path_name: str) -> dict:
    """Return the full info dict for a learning path."""
    return CURRICULUM.get(path_name, {})


def get_topics(path_name: str) -> list[dict]:
    """Return the list of topic dicts for a learning path."""
    return CURRICULUM.get(path_name, {}).get("topics", [])


def get_topic(path_name: str, topic_name: str) -> dict | None:
    """Return a single topic dict by path and topic name."""
    for topic in get_topics(path_name):
        if topic["name"] == topic_name:
            return topic
    return None


def build_topic_prompt(topic: dict, language: str = "English") -> str:
    """
    Build the content-generation prompt for a curriculum topic.

    Args:
        topic: A topic dict from the curriculum.
        language: Target language for the study material.

    Returns:
        A prompt string suitable for generating study content.
    """
    lang_instruction = f" Write in {language}." if language != "English" else ""
    return (
        f"Write a comprehensive educational summary (500-800 words) suitable for a "
        f"student studying machine learning at the {topic['level']} level. "
        f"Topic: {topic['name']}. "
        f"Cover the following: {topic['description']} "
        f"Explain the key concepts clearly, include intuition and simple examples, "
        f"and highlight how the ideas connect. Write in a clear, textbook-like "
        f"style suitable for active studying.{lang_instruction}"
    )


def count_total_topics() -> int:
    """Return the total number of topics across all paths."""
    return sum(len(info["topics"]) for info in CURRICULUM.values())



def get_topic_index(path_name: str, topic_name: str) -> int:
    """
    Return the 0-based index of a topic within its path.

    Returns -1 if the topic is not found.
    """
    topics = get_topics(path_name)
    for i, topic in enumerate(topics):
        if topic["name"] == topic_name:
            return i
    return -1


def get_next_topic(path_name: str, topic_name: str) -> dict | None:
    """
    Return the next topic in the path after the given topic.

    Returns None if the given topic is the last one (or not found).
    """
    idx = get_topic_index(path_name, topic_name)
    if idx == -1:
        return None
    topics = get_topics(path_name)
    if idx + 1 < len(topics):
        return topics[idx + 1]
    return None


def is_last_topic_in_path(path_name: str, topic_name: str) -> bool:
    """Return True if the given topic is the final topic in its path."""
    idx = get_topic_index(path_name, topic_name)
    topics = get_topics(path_name)
    return idx != -1 and idx == len(topics) - 1


def get_path_progress(path_name: str, completed_topics: set[str] | list[str]) -> dict:
    """
    Compute progress through a learning path.

    Args:
        path_name: The learning path name.
        completed_topics: Set/list of topic names the student has completed.

    Returns:
        Dict with total, completed count, percentage, and per-topic status.
    """
    topics = get_topics(path_name)
    completed_set = set(completed_topics)

    total = len(topics)
    completed = sum(1 for t in topics if t["name"] in completed_set)
    percentage = (completed / total * 100) if total > 0 else 0.0

    topic_status = [
        {
            "name": t["name"],
            "level": t["level"],
            "completed": t["name"] in completed_set,
        }
        for t in topics
    ]

    return {
        "path": path_name,
        "total": total,
        "completed": completed,
        "percentage": percentage,
        "is_complete": completed == total and total > 0,
        "topics": topic_status,
    }


def get_first_incomplete_topic(
    path_name: str, completed_topics: set[str] | list[str]
) -> dict | None:
    """
    Return the first topic in a path that has not been completed yet.

    Useful for resuming a guided path. Returns None if all complete.
    """
    completed_set = set(completed_topics)
    for topic in get_topics(path_name):
        if topic["name"] not in completed_set:
            return topic
    return None
