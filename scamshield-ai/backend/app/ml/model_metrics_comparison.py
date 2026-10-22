# import matplotlib.pyplot as plt

# # Your actual model evaluation results
# metrics = {
#     "Accuracy": 90.15,
#     "Precision": 92.61,
#     "Recall": 88.52,
#     "F1-score": 90.52
# }

# # Create figure
# plt.figure(figsize=(10, 6))

# # Create bar chart
# bars = plt.bar(
#     metrics.keys(),
#     metrics.values(),
#     width=0.58
# )

# # Title and axis labels
# plt.title(
#     "Performance Evaluation of the Random Forest Model",
#     fontsize=16,
#     fontweight="bold"
# )

# plt.ylabel("Score (%)", fontsize=12)
# plt.ylim(0, 100)

# # Grid
# plt.grid(
#     axis="y",
#     linestyle="--",
#     alpha=0.35
# )

# plt.gca().set_axisbelow(True)

# # Add percentage values above bars
# for bar, value in zip(bars, metrics.values()):
#     plt.text(
#         bar.get_x() + bar.get_width() / 2,
#         value + 1.2,
#         f"{value:.2f}%",
#         ha="center",
#         va="bottom",
#         fontsize=11,
#         fontweight="bold"
#     )

# # Subtitle / experiment information
# plt.figtext(
#     0.5,
#     0.01,
#     "Random Forest | 20 lexical URL features | Held-out test set",
#     ha="center",
#     fontsize=9
# )

# # Adjust layout
# plt.tight_layout(rect=[0, 0.04, 1, 1])

# # Save the figure
# plt.savefig(
#     "phishing_url_detection_metrics.png",
#     dpi=300,
#     bbox_inches="tight"
# )

# # Save research-paper PDF
# plt.savefig(
#     "phishing_url_detection_metrics.pdf",
#     bbox_inches="tight"
# )

# # Save vector SVG
# plt.savefig(
#     "phishing_url_detection_metrics.svg",
#     bbox_inches="tight"
# )

# # Display
# plt.show() 
import matplotlib.pyplot as plt
import numpy as np

# Metrics
metrics = ["Accuracy", "Precision", "Recall", "F1-score"]

# Values from the graph
linear_svc = [0.81, 0.71, 0.60, 0.61]
lstm = [0.41, 0.29, 0.33, 0.24]

# X-axis positions
x = np.arange(len(metrics))

# Width of each bar
width = 0.32

# Create figure
plt.figure(figsize=(10, 6))

# Create bars
bars1 = plt.bar(
    x - width / 2,
    linear_svc,
    width,
    label="LinearSVC (SVM)"
)

bars2 = plt.bar(
    x + width / 2,
    lstm,
    width,
    label="LSTM"
)

# Labels
plt.ylabel("Score", fontsize=14)
plt.xlabel("Evaluation Metrics", fontsize=13)

# Title
plt.title(
    "Performance Comparison of LinearSVC (SVM) and LSTM",
    fontsize=16,
    pad=15
)

# X-axis
plt.xticks(x, metrics, fontsize=11)

# Y-axis
plt.ylim(0, 1.0)

# Grid
plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.25
)

plt.gca().set_axisbelow(True)

# Remove top and right borders
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)

# Add values above bars
for bar in bars1:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.02,
        f"{height:.2f}",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold"
    )

for bar in bars2:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.02,
        f"{height:.2f}",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold"
    )

# Legend
plt.legend(
    loc="upper right",
    fontsize=11,
    frameon=False
)

# Adjust layout
plt.tight_layout()

# Save image
plt.savefig(
    "model_metrics_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

# Save PDF for research paper
plt.savefig(
    "model_metrics_comparison.pdf",
    bbox_inches="tight"
)

# Save SVG
plt.savefig(
    "model_metrics_comparison.svg",
    bbox_inches="tight"
)

# Show graph
plt.show()