import streamlit as st
import numpy as np
import joblib
import re
import os

from url_feature_extractor import extract_url_features, normalize_url
from genai_explainer import generate_explanation

# ============================================================
# TRUSTED DOMAIN ALLOW-LIST
# ============================================================
# The URL model only sees the URL's lexical shape (length, character
# counts, etc.), never the domain name's real-world identity. Legit
# e-commerce/marketing links with heavy UTM tracking (many "&"/"="
# characters, long length) can share the same shape as phishing URLs,
# which is a known limitation of URL-only lexical models. This
# allow-list catches well-known, unambiguously legitimate domains
# before the model runs, so a trusted brand's tracking link never
# gets flagged as phishing. It does NOT make anything "safe" that
# isn't already a known-good domain -- unrecognized domains still go
# through the full model as normal.

TRUSTED_DOMAINS = {
    "google.com", "youtube.com", "wikipedia.org", "amazon.com", "amazon.in",
    "flipkart.com", "myntra.com", "microsoft.com", "apple.com", "github.com",
    "linkedin.com", "facebook.com", "instagram.com", "twitter.com", "x.com",
    "netflix.com", "paypal.com", "irctc.co.in", "gov.in", "nic.in",
}


def _registered_host_for_trust_check(hostname):
    parts = hostname.lower().split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else hostname.lower()

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ScamShield AI",
    page_icon="🛡️",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.hero {
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 25px;
    border: 1px solid rgba(128,128,128,0.25);
}

.hero h1 {
    font-size: 42px;
    margin-bottom: 5px;
}

.hero p {
    font-size: 18px;
    opacity: 0.8;
}

.indicator {
    padding: 10px;
    margin: 7px 0;
    border-radius: 8px;
    border: 1px solid rgba(128,128,128,0.2);
}

.footer {
    text-align: center;
    opacity: 0.6;
    padding: 30px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# MODEL PATHS
# ============================================================

JOB_MODEL_PATH = "models/scam_model.pkl"
JOB_TFIDF_PATH = "models/tfidf_vectorizer.pkl"

SMS_MODEL_PATH = "models/sms_scam_model.pkl"
SMS_TFIDF_PATH = "models/sms_tfidf_vectorizer.pkl"

URL_PIPELINE_PATH = "models/url_phishing_pipeline.pkl"
URL_METADATA_PATH = "models/url_phishing_metadata.pkl"


# ============================================================
# CHECK MODEL FILES
# ============================================================

required_files = [
    JOB_MODEL_PATH,
    JOB_TFIDF_PATH,
    SMS_MODEL_PATH,
    SMS_TFIDF_PATH,
    URL_PIPELINE_PATH,
    URL_METADATA_PATH
]

for file in required_files:

    if not os.path.exists(file):

        st.error(
            f"Required model file not found: {file}"
        )

        st.stop()


# ============================================================
# LOAD MODELS
# ============================================================

@st.cache_resource

def load_models():
    job_model = joblib.load(JOB_MODEL_PATH)
    job_tfidf = joblib.load(JOB_TFIDF_PATH)
    sms_model = joblib.load(SMS_MODEL_PATH)
    sms_tfidf = joblib.load(SMS_TFIDF_PATH)
    url_pipeline = joblib.load(URL_PIPELINE_PATH)
    url_metadata = joblib.load(URL_METADATA_PATH)
    return job_model, job_tfidf, sms_model, sms_tfidf, url_pipeline, url_metadata


(job_model, job_tfidf, sms_model, sms_tfidf, url_pipeline, url_metadata) = load_models()


# ============================================================
# STOPWORDS
# ============================================================

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but",
    "if", "then", "this", "that", "these",
    "those", "is", "am", "are", "was", "were",
    "be", "been", "being", "to", "of", "in",
    "on", "for", "with", "at", "by", "from",
    "as", "it", "its", "we", "you", "your",
    "our", "they", "their", "he", "she",
    "his", "her", "i", "me", "my"
}


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):

    text = str(text).lower()

    words = re.findall(
        r"\b[a-zA-Z]+\b",
        text
    )

    words = [
        word
        for word in words
        if word not in STOP_WORDS
    ]

    return " ".join(words)


# ============================================================
# JOB RISK LEVEL
# ============================================================

def get_job_risk_level(score):

    if score < 30:
        return "LOW"

    elif score < 60:
        return "MEDIUM"

    elif score < 80:
        return "HIGH"

    else:
        return "CRITICAL"


# ============================================================
# SMS RISK SCORE
# ============================================================

def get_sms_risk(prediction, indicators):

    if prediction == 0:

        return 10, "LOW"

    indicator_count = len(indicators)

    if indicator_count >= 4:

        return 95, "CRITICAL"

    elif indicator_count >= 3:

        return 85, "HIGH"

    elif indicator_count >= 2:

        return 70, "HIGH"

    elif indicator_count >= 1:

        return 55, "MEDIUM"

    else:

        return 40, "MEDIUM"


# ============================================================
# JOB SUSPICIOUS INDICATORS
# ============================================================

def detect_job_indicators(text):

    text_lower = text.lower()

    indicators = []

    if any(word in text_lower for word in [
        "registration fee",
        "processing fee",
        "application fee",
        "pay fee",
        "payment required",
        "deposit fee",
        "send money"
    ]):

        indicators.append(
            "Requests an upfront payment or fee"
        )

    if any(word in text_lower for word in [
        "no experience",
        "no experience required",
        "without experience"
    ]):

        indicators.append(
            "Claims that no experience is required"
        )

    if any(word in text_lower for word in [
        "guaranteed income",
        "guaranteed salary",
        "earn money",
        "easy money",
        "make money fast",
        "high income"
    ]):

        indicators.append(
            "Contains potentially unrealistic earning claims"
        )

    if any(word in text_lower for word in [
        "urgent",
        "apply immediately",
        "limited time",
        "act now",
        "hurry",
        "immediately"
    ]):

        indicators.append(
            "Uses urgent or pressure-based language"
        )

    if any(word in text_lower for word in [
        "work from home",
        "work remotely",
        "remote job"
    ]):

        indicators.append(
            "Promotes a remote/work-from-home opportunity"
        )

    if any(word in text_lower for word in [
        "bank account",
        "bank details",
        "credit card",
        "send your id",
        "send your aadhaar",
        "send your passport"
    ]):

        indicators.append(
            "Requests potentially sensitive personal information"
        )

    return indicators


# ============================================================
# SMS SUSPICIOUS INDICATORS
# ============================================================

def detect_sms_indicators(text):

    text_lower = text.lower()

    indicators = []

    if any(word in text_lower for word in [
        "won",
        "winner",
        "prize",
        "lottery",
        "reward",
        "congratulations"
    ]):

        indicators.append(
            "Contains prize, lottery, or reward language"
        )

    if any(word in text_lower for word in [
        "click",
        "click here",
        "open link",
        "visit link"
    ]):

        indicators.append(
            "Contains a request to click or open a link"
        )

    if any(word in text_lower for word in [
        "urgent",
        "immediately",
        "act now",
        "limited time",
        "hurry"
    ]):

        indicators.append(
            "Uses urgent or pressure-based language"
        )

    if any(word in text_lower for word in [
        "bank",
        "account",
        "otp",
        "password",
        "pin",
        "credit card"
    ]):

        indicators.append(
            "Mentions potentially sensitive financial information"
        )

    if any(word in text_lower for word in [
        "money",
        "cash",
        "payment",
        "pay",
        "fee",
        "transfer"
    ]):

        indicators.append(
            "Contains payment or money-related language"
        )

    return indicators


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="hero">

<h1>🛡️ ScamShield AI</h1>

<p>
Global AI-Powered Scam Detection & Trust Intelligence
</p>

<p>
Analyze suspicious job postings and SMS messages.
</p>

</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🛡️ ScamShield AI")

    st.write(
        "AI-powered detection of potentially "
        "fraudulent job postings and SMS messages."
    )

    st.divider()

    st.subheader("🔍 Detection Modules")

    detection_type = st.radio(
        "Select analysis type:",
        [
            "💼 Job Scam Detection",
            "📱 SMS Scam Detection",
            "🌐 Phishing Website Detection"
        ]
    )

    st.divider()

    st.subheader("⚙️ How It Works")

    st.write("1. Enter suspicious content or a website URL")
    st.write("2. Extract or clean the input features")
    st.write("3. Analyze with the saved ML pipeline")
    st.write("4. Show the model risk assessment")

    st.divider()

    st.caption(
        "AI results are risk assessments and should "
        "not replace independent verification."
    )


# ============================================================
# JOB SCAM DETECTION
# ============================================================

if detection_type == "💼 Job Scam Detection":

    st.subheader("💼 Job Scam Detection")

    st.write(
        "Paste a job posting to check whether it "
        "may be fraudulent."
    )

    job_text = st.text_area(
        "Job Posting",
        height=280,
        placeholder=(
            "Paste the complete job description here..."
        )
    )

    analyze_job = st.button(
        "🔍 Analyze Job Posting",
        type="primary",
        use_container_width=True
    )

    if analyze_job:

        if not job_text.strip():

            st.warning(
                "Please enter a job posting."
            )

        elif len(job_text.strip()) < 20:

            st.warning(
                "Please provide a more detailed job posting."
            )

        else:

            with st.spinner(
                "Analyzing job posting..."
            ):

                cleaned_text = clean_text(
                    job_text
                )

                text_vector = job_tfidf.transform(
                    [cleaned_text]
                )

                prediction = job_model.predict(
                    text_vector
                )[0]

                fraud_probability = (
                    job_model.predict_proba(
                        text_vector
                    )[0][1]
                )

                risk_score = (
                    fraud_probability * 100
                )

                risk_level = get_job_risk_level(
                    risk_score
                )

                indicators = detect_job_indicators(
                    job_text
                )

            st.divider()

            if prediction == 1:

                st.error(
                    "🚨 FRAUDULENT JOB POSTING DETECTED"
                )

            else:

                st.success(
                    "✅ LIKELY LEGITIMATE JOB POSTING"
                )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Fraud Probability",
                    f"{risk_score:.2f}%"
                )

            with col2:

                st.metric(
                    "Risk Score",
                    f"{risk_score:.2f}/100"
                )

            with col3:

                st.metric(
                    "Risk Level",
                    risk_level
                )

            st.subheader(
                "📊 Risk Assessment"
            )

            st.progress(
                min(risk_score / 100, 1.0)
            )

            st.subheader(
                "⚠️ Suspicious Indicators"
            )

            if indicators:

                for indicator in indicators:

                    st.markdown(
                        f"""
                        <div class="indicator">
                        ⚠️ {indicator}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            else:

                st.success(
                    "No predefined suspicious indicators detected."
                )

            st.subheader(
                "🧠 AI Explanation"
            )

            with st.spinner("Generating explanation..."):

                job_explanation = generate_explanation(
                    module_type="Job Posting",
                    input_text=job_text,
                    prediction_label=(
                        "Fraudulent" if prediction == 1 else "Legitimate"
                    ),
                    risk_score=round(risk_score, 2),
                    indicators=indicators,
                )

            st.info(job_explanation)

            st.subheader(
                "🛡️ Recommendation"
            )

            if risk_level == "CRITICAL":

                st.error(
                    "Avoid sending money or sensitive "
                    "information. Verify the employer "
                    "independently."
                )

            elif risk_level == "HIGH":

                st.warning(
                    "Proceed with caution and verify "
                    "the employer before applying."
                )

            elif risk_level == "MEDIUM":

                st.warning(
                    "Perform additional verification "
                    "before applying."
                )

            else:

                st.success(
                    "The posting appears relatively "
                    "low risk, but verify the employer."
                )


# ============================================================
# SMS SCAM DETECTION
# ============================================================

elif detection_type == "📱 SMS Scam Detection":
    st.subheader("📱 SMS Scam Detection")

    st.write(
        "Paste an SMS message to check whether "
        "it may be spam or a scam."
    )

    sms_text = st.text_area(
        "SMS Message",
        height=220,
        placeholder=(
            "Example: Congratulations! You have won "
            "₹50,000. Click here to claim your prize."
        )
    )

    analyze_sms = st.button(
        "🔍 Analyze SMS",
        type="primary",
        use_container_width=True
    )

    if analyze_sms:

        if not sms_text.strip():

            st.warning(
                "Please enter an SMS message."
            )

        elif len(sms_text.strip()) < 5:

            st.warning(
                "Please enter a valid SMS message."
            )

        else:

            with st.spinner(
                "Analyzing SMS..."
            ):

                cleaned_sms = clean_text(
                    sms_text
                )

                sms_vector = sms_tfidf.transform(
                    [cleaned_sms]
                )

                prediction = sms_model.predict(
                    sms_vector
                )[0]

                indicators = detect_sms_indicators(
                    sms_text
                )

                risk_score, risk_level = get_sms_risk(
                    prediction,
                    indicators
                )

            st.divider()

            if prediction == 1:

                st.error(
                    "🚨 SPAM / SCAM SMS DETECTED"
                )

            else:

                st.success(
                    "✅ LIKELY LEGITIMATE SMS"
                )

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Risk Score",
                    f"{risk_score}/100"
                )

            with col2:

                st.metric(
                    "Risk Level",
                    risk_level
                )

            st.subheader(
                "📊 Risk Assessment"
            )

            st.progress(
                risk_score / 100
            )

            st.subheader(
                "⚠️ Suspicious Indicators"
            )

            if indicators:

                for indicator in indicators:

                    st.markdown(
                        f"""
                        <div class="indicator">
                        ⚠️ {indicator}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            else:

                st.success(
                    "No predefined suspicious indicators detected."
                )

            st.subheader(
                "🧠 AI Explanation"
            )

            with st.spinner("Generating explanation..."):

                sms_explanation = generate_explanation(
                    module_type="SMS Message",
                    input_text=sms_text,
                    prediction_label=(
                        "Spam" if prediction == 1 else "Legitimate"
                    ),
                    risk_score=risk_score,
                    indicators=indicators,
                )

            st.info(sms_explanation)

            st.subheader(
                "🛡️ Recommendation"
            )

            if risk_level == "CRITICAL":

                st.error(
                    "Do not click suspicious links, "
                    "send money, or provide OTPs, "
                    "passwords, or financial information."
                )

            elif risk_level == "HIGH":

                st.warning(
                    "Do not interact with the message "
                    "until the sender and request are verified."
                )

            elif risk_level == "MEDIUM":

                st.warning(
                    "Verify the sender before clicking "
                    "links or sharing information."
                )

            else:

                st.success(
                    "The message appears relatively "
                    "low risk, but remain cautious."
                )


# ============================================================
# PHISHING WEBSITE DETECTION
# ============================================================

elif detection_type == "🌐 Phishing Website Detection":
    st.subheader("🌐 Phishing Website Detection")

    st.write(
        "Enter a website URL to assess URL features associated with phishing."
    )

    website_url = st.text_input(
        "Website URL",
        placeholder="https://example.com"
    )

    check_website = st.button(
        "🔍 Check Website",
        type="primary",
        use_container_width=True
    )

    if check_website:
        if not website_url.strip():
            st.warning("Please enter a website URL.")
        else:
            try:
                normalized_url = normalize_url(website_url)
                url_features = extract_url_features(normalized_url)
                expected_features = url_metadata.get("feature_columns", [])
                actual_features = list(url_features.columns)
                if actual_features != expected_features:
                    raise ValueError(
                        "The URL feature order does not match the saved model."
                    )

                from urllib.parse import urlparse
                hostname = (urlparse(normalized_url).hostname or "").lower()
                registered_host = _registered_host_for_trust_check(hostname)
                is_trusted_domain = registered_host in TRUSTED_DOMAINS

                prediction = url_pipeline.predict(url_features)[0]
                probabilities = url_pipeline.predict_proba(url_features)[0]
                class_probabilities = dict(
                    zip(url_pipeline.classes_, probabilities)
                )
                confidence = class_probabilities[prediction] * 100

                if is_trusted_domain:
                    model_prediction = prediction
                    model_confidence = confidence
                    prediction = 1
                    confidence = 100.0

                st.divider()
                st.write(f"**Website:** {normalized_url}")
                if is_trusted_domain:
                    st.success("✅ LIKELY LEGITIMATE / SAFE")
                    st.write(
                        f"**{registered_host}** is a recognized, well-known domain, "
                        "so it's treated as trusted regardless of URL shape."
                    )
                    if model_prediction != 1:
                        st.caption(
                            f"Note: based on URL shape alone (tracking parameters, "
                            f"length, etc.), the underlying model would have flagged "
                            f"this link as phishing with {model_confidence:.2f}% "
                            f"confidence. This is a known false-positive pattern for "
                            f"heavily tracked marketing links, which is why the "
                            f"trusted-domain check overrides it here."
                        )
                elif prediction == -1:
                    st.error("⚠️ LIKELY PHISHING / SUSPICIOUS")
                    st.write(
                        "Based on the URL features analyzed, this website appears suspicious. "
                        "Verify it independently before sharing information."
                    )
                elif prediction == 1:
                    st.success("✅ LIKELY LEGITIMATE / SAFE")
                    st.write(
                        "The analyzed URL features appear more consistent with legitimate websites. "
                        "This is not a guarantee of safety."
                    )
                else:
                    raise ValueError("The saved model returned an unknown label.")

                st.metric("Model Confidence", f"{confidence:.2f}%")

                st.subheader("🧠 AI Explanation")

                url_feature_notes = [
                    f"{column} = {url_features.iloc[0][column]}"
                    for column in url_features.columns
                ]

                with st.spinner("Generating explanation..."):
                    url_explanation = generate_explanation(
                        module_type="Website URL",
                        input_text=normalized_url,
                        prediction_label=(
                            "Likely Phishing" if prediction == -1
                            else "Likely Legitimate"
                        ),
                        risk_score=round(confidence, 2),
                        indicators=url_feature_notes,
                    )

                st.info(url_explanation)

                st.caption(
                    "This assessment uses URL-derived features only and does not inspect the website content."
                )
            except ValueError as error:
                st.warning(str(error))
            except Exception:
                st.error(
                    "The URL could not be analyzed. Check that the phishing model files are available."
                )


# ============================================================
# MODEL INFORMATION
# ============================================================

st.divider()

with st.expander("🤖 Model Information"):

    st.write(
        "**Job Detection:** Logistic Regression + TF-IDF"
    )

    st.write(
        "**SMS Detection:** SVM + TF-IDF"
    )

    st.write(
        "**Job Classes:** Legitimate / Fraudulent"
    )

    st.write(
        "**SMS Classes:** Ham / Spam"
    )

    st.write(
        f"**URL Detection:** {url_metadata.get('selected_model', 'Saved ML pipeline')}"
    )

    st.write(
        "**URL Classes:** Phishing / Suspicious and Legitimate / Safe"
    )

    st.write(
        "**NLP Techniques:** Text Cleaning, "
        "Stopword Removal, Lemmatization and TF-IDF"
    )

    st.write(
        "**GenAI Explanation Layer:** Groq-hosted Llama 3.1 generates "
        "the plain-English explanation shown under each result. It "
        "does not influence the model's verdict, risk score, or "
        "indicators — those come entirely from the trained ML "
        "pipelines above."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">

🛡️ <b>ScamShield AI</b><br>

AI-powered scam detection prototype<br>

Always verify suspicious online content independently.

</div>
""", unsafe_allow_html=True)