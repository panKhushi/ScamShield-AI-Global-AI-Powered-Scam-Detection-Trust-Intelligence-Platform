from scraper import fetch_page_html, get_anchor_url_score, get_links_in_script_tags_score, get_website_traffic_score

test_urls = ["google.com", "wikipedia.org", "github.com"]

for url in test_urls:
    html = fetch_page_html(url)
    traffic_score = get_website_traffic_score(url)
    if html:
        anchor_score = get_anchor_url_score(html, url)
        script_score = get_links_in_script_tags_score(html, url)
        print(f"{url}: AnchorURL={anchor_score}, LinksInScriptTags={script_score}, WebsiteTraffic={traffic_score}")
    else:
        print(f"{url}: failed to fetch, WebsiteTraffic={traffic_score}")

from scraper import (
    fetch_page_html, get_anchor_url_score, get_links_in_script_tags_score,
    get_website_traffic_score, get_https_score, get_prefix_suffix_score,
    get_subdomains_score, get_domain_reg_len_score
)

test_urls = ["google.com", "wikipedia.org", "github.com"]

for url in test_urls:
    full_url = f"https://{url}"
    html = fetch_page_html(url)

    anchor = get_anchor_url_score(html, url) if html else 0
    script = get_links_in_script_tags_score(html, url) if html else 0
    traffic = get_website_traffic_score(url)
    https = get_https_score(full_url)
    prefix = get_prefix_suffix_score(url)
    subdomains = get_subdomains_score(url)

    print(f"{url}: Anchor={anchor}, Script={script}, Traffic={traffic}, HTTPS={https}, PrefixSuffix={prefix}, SubDomains={subdomains}")