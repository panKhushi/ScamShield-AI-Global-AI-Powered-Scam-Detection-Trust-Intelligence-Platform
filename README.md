# NLP SCAMSHIELD

## Project Overview

NLP SCAMSHIELD is a Streamlit application that provides machine-learning risk assessments for job postings, SMS messages, and website URLs. The existing job and SMS modules remain separate from the URL module and keep their original model files.

## Three Detection Modules

- **Job Scam Detection:** TF-IDF text features and the existing job scam model.
- **SMS Scam Detection:** TF-IDF text features and the existing SMS scam model.
- **Phishing Website Detection:** URL-derived features and a saved classification pipeline.

## Generative AI Explanation Layer

Each module's verdict, risk score, and rule-based indicators are passed to a
Large Language Model (Groq-hosted Llama 3.1) which generates a short,
plain-English explanation of the result. This layer is purely explanatory:
it never overrides or influences the trained ML model's prediction, which
remains the sole decision-maker and the component that was evaluated
against the held-out test set.

This is implemented in `genai_explainer.py`. If no API key is configured,
the app falls back to a static message instead of failing, so the core ML
functionality always works even without GenAI access.

### Setup

1. Get a free API key at https://console.groq.com/keys
2. Copy `.env.example` to `.env` and paste your key in:
   ```text
   cp .env.example .env
   ```
3. Install the extra dependencies (already in `requirements.txt`):
   ```text
   pip install -r requirements.txt
   ```

## Phishing Website Detection (v2)

The module was originally trained on `data/Phishing_Websites_Data.csv` (11,055 rows, 8 usable URL-only columns). That 8-feature set was too coarse: many genuinely different websites collapse to the exact same feature vector, producing identical risk scores for unrelated URLs.

v2 retrains on `data/Phishing_Lexical_Dataset.csv` (Vrbancic, Fister Jr. & Podgorelec, *Data in Brief*, 2020), using 20 finer-grained lexical features -- character counts and structural counts computed purely from the URL string, its domain, and its query string:

`length_url`, `qty_dot_url`, `qty_hyphen_url`, `qty_underline_url`, `qty_slash_url`, `qty_questionmark_url`, `qty_equal_url`, `qty_at_url`, `qty_and_url`, `qty_percent_url`, `domain_length`, `qty_dot_domain`, `qty_hyphen_domain`, `qty_vowels_domain`, `domain_in_ip`, `qty_slash_directory`, `qty_params`, `params_length`, `email_in_url`, `url_shortened`.

As with v1, only columns derivable from the URL text alone are used -- no live DNS/WHOIS/SSL/web-traffic lookups, since this app only ever receives a URL string typed by the user. `url_feature_extractor.py` computes these 20 columns identically to how they're defined in the training dataset, in the exact order the saved pipeline expects.

### Known limitation: trusted-domain allow-list

URL-only lexical models cannot see a domain's real-world identity, only its shape. Legitimate marketing links with heavy UTM/ad tracking (long URLs, many `&`/`=` characters) share the same lexical shape as phishing URLs, so the model alone can flag well-known brands as suspicious. `app.py` includes a small `TRUSTED_DOMAINS` allow-list that overrides the model's verdict for recognized major domains, while still surfacing the model's raw verdict as a caption for transparency. Unrecognized domains still go through the model as normal -- this does not make anything "safe" beyond the listed domains.

## Machine Learning Algorithms

The training workflow compares:

- Logistic Regression
- Random Forest
- Support Vector Machine (SVM)

The selected model is chosen using phishing-class F1-score, with recall and precision as tie-breakers. The current trained model (v2, 20-feature lexical set) is Random Forest.

## Evaluation Metrics

The workflow reports accuracy, precision, recall, F1-score, and classification reports. The current phishing-class test metrics (v2) are approximately:

- Accuracy: 90.15%
- Precision: 92.61%
- Recall: 88.52%
- F1-score: 90.52%

(v1's 8-feature model scored approximately 74.53% accuracy / 77.04% F1 on its own dataset -- not directly comparable since the datasets differ, but indicative of why the richer feature set was adopted.)

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

The notebook `notebooks/url_phishing_detection.ipynb` reflects the original v1 (8-feature) workflow; it has not been updated for v2 and is kept for reference on the earlier approach.

## Limitations

This module analyzes URL structure only. It does not fetch or inspect a website, query external reputation services, resolve DNS, or verify domain ownership. A "Likely Legitimate" result is not a guarantee of safety, and a suspicious-looking test URL is not automatically malicious merely because it looks unusual. Unrecognized domains with unusual-but-legitimate URL shapes (long query strings, hyphens, etc.) may still be flagged, which is why the trusted-domain allow-list exists for well-known brands specifically.

