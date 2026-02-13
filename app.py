from flask import Flask, request, jsonify
import requests
import re
from urllib.parse import urljoin

app = Flask(__name__)

def extract_emails_from_url(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=8)
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", r.text)
        return list(set(emails)), r.text
    except:
        return [], ""

def find_contact_links(base_url, html):
    links = re.findall(r'href=["\'](.*?)["\']', html)
    keywords = ["contact", "about", "support", "media", "team", "press"]
    final_links = []

    for link in links:
        for k in keywords:
            if k in link.lower():
                full = urljoin(base_url, link)
                final_links.append(full)

    return list(set(final_links))

@app.route("/scrape", methods=["POST"])
def scrape():
    data = request.json
    domain = data.get("domain")

    base_url = f"https://{domain}"
    all_emails = []

    emails, html = extract_emails_from_url(base_url)
    all_emails.extend(emails)

    contact_links = find_contact_links(base_url, html)

    for link in contact_links[:5]:
        emails, _ = extract_emails_from_url(link)
        all_emails.extend(emails)

    return jsonify({
        "domain": domain,
        "emails": list(set(all_emails))
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
