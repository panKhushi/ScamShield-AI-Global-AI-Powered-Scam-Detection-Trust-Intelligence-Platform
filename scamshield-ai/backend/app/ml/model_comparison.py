# import matplotlib.pyplot as plt
# import numpy as np

# # Metrics
# metrics = ["Accuracy", "Precision", "Recall", "F1-score"]

# # Model results from your graph
# logistic_regression = [86.3, 86.9, 86.8, 86.8]
# random_forest = [90.2, 91.8, 89.1, 90.5]
# svm = [87.7, 88.3, 88.3, 88.3]

# # X-axis positions
# x = np.arange(len(metrics))

# # Bar width
# width = 0.24

# # Create figure
# plt.figure(figsize=(12, 7))

# # Create bars
# bars_lr = plt.bar(
#     x - width,
#     logistic_regression,
#     width,
#     label="Logistic Regression"
# )

# bars_rf = plt.bar(
#     x,
#     random_forest,
#     width,
#     label="Random Forest"
# )

# bars_svm = plt.bar(
#     x + width,
#     svm,
#     width,
#     label="SVM"
# )

# # Title
# plt.title(
#     "ScamShield: Phishing Website Detection - Model Comparison",
#     fontsize=18
# )

# # Axis labels
# plt.xlabel("")
# plt.ylabel("Score (%)", fontsize=14)

# # X-axis
# plt.xticks(x, metrics, fontsize=13)

# # Y-axis
# plt.ylim(0, 105)
# plt.yticks(fontsize=12)

# # Grid
# plt.grid(
#     axis="y",
#     linestyle="-",
#     alpha=0.25
# )

# # Put grid behind bars
# plt.gca().set_axisbelow(True)

# # Add legend
# plt.legend(
#     fontsize=12,
#     loc="upper left"
# )

# # Add values above bars
# def add_values(bars):
#     for bar in bars:
#         height = bar.get_height()

#         plt.text(
#             bar.get_x() + bar.get_width() / 2,
#             height + 0.8,
#             f"{height:.1f}",
#             ha="center",
#             va="bottom",
#             fontsize=11
#         )

# add_values(bars_lr)
# add_values(bars_rf)
# add_values(bars_svm)

# # Layout
# plt.tight_layout()

# # Save high-resolution PNG
# plt.savefig(
#     "scamshield_model_comparison.png",
#     dpi=300,
#     bbox_inches="tight"
# )

# # Save PDF for research paper
# plt.savefig(
#     "scamshield_model_comparison.pdf",
#     bbox_inches="tight"
# )

# # Save SVG vector figure
# plt.savefig(
#     "scamshield_model_comparison.svg",
#     bbox_inches="tight"
# )

# # Display
# plt.show()

import matplotlib.pyplot as plt

# Model names
models = [
    "Majority-class\nbaseline",
    "LSTM",
    "LinearSVC\n(SVM)"
]

# Accuracy values from your graph
accuracy = [0.487, 0.415, 0.813]

# Create figure
plt.figure(figsize=(10, 6))

# Create bars
bars = plt.bar(
    models,
    accuracy,
    width=0.55
)

# Y-axis
plt.ylabel("Accuracy", fontsize=14)
plt.ylim(0, 1.0)

# Title
plt.title(
    "Model Comparison Based on Accuracy",
    fontsize=16,
    pad=15
)

# Add grid
plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.25
)

# Put grid behind bars
plt.gca().set_axisbelow(True)

# Remove top and right borders
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)

# Add accuracy values above bars
for bar, value in zip(bars, accuracy):

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value + 0.02,
        f"{value:.3f}",
        ha="center",
        va="bottom",
        fontsize=12,
        fontweight="bold"
    )

# Improve layout
plt.tight_layout()

# Save image
plt.savefig(
    "model_accuracy_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

# Save PDF for research paper
plt.savefig(
    "model_accuracy_comparison.pdf",
    bbox_inches="tight"
)

# Display graph
plt.show()