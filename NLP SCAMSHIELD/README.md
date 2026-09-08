# NLP SCAMSHIELD

## Project Overview

NLP SCAMSHIELD is a Streamlit application that provides machine-learning risk assessments for job postings, SMS messages, and website URLs. The existing job and SMS modules remain separate from the URL module and keep their original model files.

## Three Detection Modules

- **Job Scam Detection:** TF-IDF text features and the existing job scam model.
- **SMS Scam Detection:** TF-IDF text features and the existing SMS scam model.
- **Phishing Website Detection:** URL-derived features and a saved classification pipeline.

## Phishing Website Detection

The new module uses `data/Phishing_Websites_Data.csv`. The dataset has 11,055 rows and 31 columns, with `Result` as the target. Its labels are represented as `-1` for phishing/suspicious and `1` for legitimate/safe. Duplicate rows are removed before training.

A raw URL cannot reliably provide page-level values such as anchor behavior, DNS records, traffic, or page rank. Therefore, the URL model is trained on eight columns that can be derived from the entered URL:

`having_IP_Address`, `URL_Length`, `Shortining_Service`, `having_At_Symbol`, `double_slash_redirecting`, `Prefix_Suffix`, `having_Sub_Domain`, and `HTTPS_token`.

`url_feature_extractor.py` applies the same column names, order, and dataset encodings used during training. The saved `url_phishing_pipeline.pkl` includes scaling and the selected classifier.

## Machine Learning Algorithms

The training workflow compares:

- Logistic Regression
- Random Forest
- Support Vector Machine (SVM)

The selected model is chosen using phishing-class F1-score, with recall and precision as tie-breakers. The current trained model is SVM.

## Evaluation Metrics

The workflow reports accuracy, precision, recall, F1-score, classification reports, and confusion matrices. The current phishing-class test metrics are approximately:

- Accuracy: 74.53%
- Precision: 72.05%
- Recall: 82.78%
- F1-score: 77.04%

These metrics describe the held-out dataset split, not a guarantee for any real website.

## How to Run

Install dependencies and start Streamlit from the project directory:

```text
pip install -r requirements.txt
streamlit run app.py
```

Choose **Phishing Website Detection** in the sidebar, enter a URL, and select **Check Website**. URLs without a scheme are normalized to HTTPS for feature extraction. Invalid URLs are rejected with a user-friendly message.

## How to Test

The URL feature extractor and saved pipeline can be checked with:

```text
python -c "from url_feature_extractor import extract_url_features; print(extract_url_features('https://www.google.com'))"
python train_url_phishing_model.py
```

The notebook `notebooks/url_phishing_detection.ipynb` contains the complete inspection, EDA, comparison, training, saving, and prediction workflow.

## Limitations

This module analyzes URL structure only. It does not fetch or inspect a website, query external reputation services, resolve DNS, or verify domain ownership. A "Likely Legitimate" result is not a guarantee of safety, and a suspicious-looking test URL is not automatically malicious merely because it looks unusual.
