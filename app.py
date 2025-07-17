from flask import Flask, request, jsonify
from flask_cors import CORS  # นำเข้า CORS
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
CORS(app)

@app.route('/check_seo', methods=['POST'])
def check_seo():
    url = request.json.get('url')
    if not url.startswith('http'):
        url = 'https://' + url
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        robots_url = urljoin(url, '/robots.txt')
        robots_exists = requests.get(robots_url).status_code == 200

        sitemap_url = urljoin(url, '/sitemap.xml')
        sitemap_exists = requests.get(sitemap_url).status_code == 200

        images = soup.find_all('img')
        images_missing_alt = [img.get('src') for img in images if not img.get('alt')]

        canonical_tag = soup.find('link', rel='canonical')
        canonical = canonical_tag['href'] if canonical_tag else None

        https_used = urlparse(url).scheme == 'https'
        viewport_tag = soup.find('meta', attrs={'name': 'viewport'})
        mobile_friendly = viewport_tag is not None

        og_tags = {
            tag.get('property'): tag.get('content')
            for tag in soup.find_all('meta')
            if tag.get('property', '').startswith('og:')
        }

        twitter_tags = {
            tag.get('name'): tag.get('content')
            for tag in soup.find_all('meta')
            if tag.get('name', '').startswith('twitter:')
        }

        return jsonify({
            'robots_txt_found': robots_exists,
            'sitemap_xml_found': sitemap_exists,
            'images_without_alt': images_missing_alt,
            'canonical_tag': canonical or "Not Found",
            'https': https_used,
            'mobile_friendly': mobile_friendly,
            'open_graph_tags': og_tags,
            'twitter_card_tags': twitter_tags,
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
