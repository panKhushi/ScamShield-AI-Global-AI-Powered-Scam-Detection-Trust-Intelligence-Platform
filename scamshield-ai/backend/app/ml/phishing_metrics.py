import matplotlib.pyplot as plt

# Your actual model evaluation results
metrics = {
    "Accuracy": 90.15,
    "Precision": 92.61,
    "Recall": 88.52,
    "F1-score": 90.52
}

# Create figure
plt.figure(figsize=(10, 6))

# Create bar chart
bars = plt.bar(
    metrics.keys(),
    metrics.values(),
    width=0.58
)

# Title and axis labels
plt.title(
    "Performance Evaluation of the Random Forest Model",
    fontsize=16,
    fontweight="bold"
)

plt.ylabel("Score (%)", fontsize=12)
plt.ylim(0, 100)

# Grid
plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.35
)

plt.gca().set_axisbelow(True)

# Add percentage values above bars
for bar, value in zip(bars, metrics.values()):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value + 1.2,
        f"{value:.2f}%",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold"
    )

# Subtitle / experiment information
plt.figtext(
    0.5,
    0.01,
    "Random Forest | 20 lexical URL features | Held-out test set",
    ha="center",
    fontsize=9
)

# Adjust layout
plt.tight_layout(rect=[0, 0.04, 1, 1])

# Save the figure
plt.savefig(
    "phishing_url_detection_metrics.png",
    dpi=300,
    bbox_inches="tight"
)

# Save research-paper PDF
plt.savefig(
    "phishing_url_detection_metrics.pdf",
    bbox_inches="tight"
)

# Save vector SVG
plt.savefig(
    "phishing_url_detection_metrics.svg",
    bbox_inches="tight"
)

# Display
plt.show()