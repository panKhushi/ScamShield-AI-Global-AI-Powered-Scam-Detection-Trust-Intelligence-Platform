from urllib.parse import urlparse
from app.ml.scraper import (
    fetch_page_html, get_anchor_url_score, get_links_in_script_tags_score,
    get_website_traffic_score, get_https_score, get_prefix_suffix_score,
    get_subdomains_score, get_domain_reg_len_score
)

def collect_ml_features(url: str, domain_age_days: int | None) -> dict:
    """
    Runs all available scrapers/checks and maps results to the exact
    column names the trained model expects (from the Kaggle dataset).
    """
    if not url.startswith(("http://", "https://")):
        full_url = "https://" + url
    else:
        full_url = url

    domain = urlparse(full_url).netloc

    html = fetch_page_html(url)

    return {
        "HTTPS": get_https_score(full_url),
        "PrefixSuffix-": get_prefix_suffix_score(domain),
        "SubDomains": get_subdomains_score(domain),
        "DomainRegLen": get_domain_reg_len_score(domain_age_days),
        "AnchorURL": get_anchor_url_score(html, domain) if html else 0,
        "LinksInScriptTags": get_links_in_script_tags_score(html, domain) if html else 0,
        "WebsiteTraffic": get_website_traffic_score(domain),
    }