from app.models import ScoreFactor

# Maps a factor NAME (or keyword within it) to specific recommended actions.
# Order matters: more specific/severe recommendations should appear first.
EVIDENCE_RECOMMENDATIONS = {
    "Upfront Payment Request": [
        "Do not transfer money or make any payment before verifying legitimacy through official channels.",
        "Legitimate employers never require payment from candidates.",
    ],
    "Sensitive Info Requested Early": [
        "Do not share banking details, ID copies, or OTPs with this contact.",
        "Verify identity through the company's official website before sharing any personal information.",
    ],
    "Credential / Payment Request": [
        "Do not enter your password, card details, or OTP on this page or in reply to this message.",
        "Navigate to the official site directly by typing the URL yourself, rather than clicking any link.",
    ],
    "Urgency / Pressure Tactics": [
        "Treat any 'act immediately' or 'limited time' pressure as a red flag — take time to verify independently.",
    ],
    "Urgency / Threat Language": [
        "Do not act on threats of account suspension without verifying directly through the official app or website.",
    ],
    "Unrealistic Compensation": [
        "Research typical pay for this role and location — offers significantly above market rate warrant scrutiny.",
    ],
    "Suspicious Communication Channel": [
        "Be cautious of employers who only communicate via personal messaging apps rather than official channels.",
    ],
    "Suspicious Link Language": [
        "Do not click embedded links — navigate to the service directly instead.",
    ],
    "Generic Greeting": [
        "Generic greetings ('Dear Customer') instead of your name can indicate a mass phishing attempt.",
    ],
    "Sender Impersonation Language": [
        "Verify the sender's actual email domain matches the organization they claim to represent.",
    ],
    "Unexpected Attachment/Prize": [
        "Do not open unexpected attachments or claim unsolicited prizes — these often carry malware or lead to phishing pages.",
    ],
    "Urgency / Threats": [
        "Ignore urgent SMS threats and verify account issues through the organization's official app or website.",
    ],
    "Suspicious / Shortened Link": [
        "Do not open links from unexpected SMS messages; visit the official service directly instead.",
    ],
    "Prize / Refund Claim": [
        "Do not pay fees or provide details to claim an unexpected prize or refund.",
    ],
    "OTP / PIN / Bank Details Request": [
        "Never share an OTP, PIN, or bank details in response to an SMS.",
    ],
    "Impersonation": [
        "Contact the bank, delivery service, or government department using a trusted official number.",
    ],
    "Unknown Sender Pattern": [
        "Treat unexpected messages from unknown senders as suspicious and avoid replying.",
    ],
    "Domain Age": [
        "Newly registered domains are statistically more likely to be used for scams — proceed with extra caution.",
    ],
    "Google Safe Browsing": [
        "This domain has been flagged by Google's threat database — avoid entering any information on this site.",
    ],
    "VirusTotal": [
        "Multiple security vendors have flagged this URL as malicious — do not proceed.",
    ],
    "Community Reports": [
        "Other users have reported this target as suspicious — review their reports before proceeding.",
    ],
    "Vague Job Details": [
        "Ask for specific job responsibilities and company details before proceeding with any application.",
    ],
}

GENERIC_SAFE_RECOMMENDATION = [
    "No significant red flags were detected, but always remain cautious with unfamiliar contacts and offers.",
]

GENERIC_CRITICAL_RECOMMENDATION = [
    "Report this to the relevant platform or authority.",
    "Do not proceed with this transaction, application, or communication.",
]


def generate_recommendations(factors: list[ScoreFactor], verdict: str) -> list[str]:
    """
    Builds a de-duplicated, evidence-specific list of recommended actions
    based on which factors were flagged bad/warning in this particular scan.
    """
    recommendations: list[str] = []

    for factor in factors:
        if factor.status in ("bad", "warning"):
            matched = EVIDENCE_RECOMMENDATIONS.get(factor.name)
            if matched:
                for rec in matched:
                    if rec not in recommendations:
                        recommendations.append(rec)

    if not recommendations:
        return GENERIC_SAFE_RECOMMENDATION

    if verdict == "dangerous":
        for rec in GENERIC_CRITICAL_RECOMMENDATION:
            if rec not in recommendations:
                recommendations.append(rec)

    return recommendations