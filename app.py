from flask import Flask, jsonify, render_template, request
from markupsafe import Markup
import os
from flask_cors import CORS
import markdown
import re
from urllib.parse import unquote

app = Flask(__name__, template_folder="components", static_folder="static")
# Enable CORS for all routes
CORS(app)


@app.route("/", methods=["GET"])
def hello_world():
    return render_template("index.html")


@app.route("/api/hello", methods=["GET"])
def hello_api():
    return jsonify({"message": "Hello from the API!"})


@app.route("/components/navbar", methods=["GET"])
def navbar_component():
    # Render the navbar component
    return render_template("navbar.html")


def parse_obsidian_links(html_content):
    """Parse Obsidian-style links in HTML content."""

    # Regular expressions for different Obsidian link types
    footnote_pattern = r"\^\[(.*?)\]"  # ^[footnote]
    image_pattern = r"!\[\[(.*?)\]\]"  # ![[image]]

    # Process image links first (to avoid conflict with regular links)
    def replace_images(match):
        image_path = match.group(1).strip()
        return f'<img src="/static/images/{image_path}" alt="{image_path}" class="obsidian-image">'

    html_content = re.sub(image_pattern, replace_images, html_content)

    # Wiki links will be processed on the client side with Alpine.js

    # Process footnotes
    footnotes = []

    def collect_footnotes(match):
        footnote_text = match.group(1).strip()
        footnote_id = len(footnotes) + 1
        footnotes.append(footnote_text)
        return (
            f'<sup class="footnote-ref"><a href="#footnote-{footnote_id}" '
            f'id="footnote-ref-{footnote_id}">[{footnote_id}]</a></sup>'
        )

    html_content = re.sub(footnote_pattern, collect_footnotes, html_content)

    # Add footnotes section if any exist
    if footnotes:
        footnote_section = '<hr><div class="footnotes"><ol>'
        for i, text in enumerate(footnotes, 1):
            footnote_section += (
                f'<li id="footnote-{i}">{text} <a href="#footnote-ref-{i}">↩</a></li>'
            )
        footnote_section += "</ol></div>"
        html_content += footnote_section

    return html_content


@app.route("/components/article/<path:article_id>", methods=["GET"])
def article_component(article_id):
    try:
        # URL decode the article_id to handle special characters
        decoded_article_id = unquote(article_id)

        # Read the markdown file
        with open(f"articles/{decoded_article_id}.md", "r") as file:
            md_content = file.read()

        # Convert markdown to HTML
        html_content = markdown.markdown(md_content)

        # Parse Obsidian-style links
        html_content = parse_obsidian_links(html_content)

        # Render the component with the content
        return render_template("article.html", content=Markup(html_content))
    except FileNotFoundError:
        return f"Article {article_id} not found", 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
