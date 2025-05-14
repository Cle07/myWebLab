from flask import Flask, Response, jsonify, render_template
from urllib.parse import unquote
from markupsafe import Markup
from flask_cors import CORS
import markdown
import os
import re


app = Flask(__name__, template_folder="components", static_folder="static")
# Enable CORS for all routes
CORS(app)


##############################################
# COMPONENTS
##############################################


@app.route("/components/navbar", methods=["GET"])
def navbar_component() -> str:
    # Render the navbar component
    return render_template("navbar.html")


@app.route("/components/article/<path:article_id>", methods=["GET"])
def article_component(article_id) -> str:
    try:
        # URL decode the article_id to handle special characters
        decoded_article_id = unquote(article_id)

        try:
            with open(f"articles/{decoded_article_id}.md", "r") as file:
                md_content = file.read()
        except FileNotFoundError:
            return f"Article {article_id} not found"

        html_content = markdown.markdown(md_content, extensions=["tables"])
        html_content = parse_obsidian_links(html_content)

        return render_template("article.html", content=Markup(html_content))
    except TimeoutError as e:
        return f"Fatal Error : {e}"


##############################################
# API
##############################################


@app.route("/api/hello", methods=["GET"])
def hello_api() -> Response:
    return jsonify({"message": "Hello from the API!"})


##############################################
# ROUTER
##############################################


@app.route("/", methods=["GET"])
def index() -> str:
    return render_template("index.html")


@app.route("/about", methods=["GET"])
def about() -> str:
    try:
        with open("articles/about.md", "r") as file:
            md_content = file.read()
    except FileNotFoundError:
        return "About page not found"

    html_content = markdown.markdown(md_content, extensions=["tables"])
    html_content = parse_obsidian_links(html_content)

    return render_template("article.html", content=Markup(html_content))


##############################################
# UTILITIES
##############################################


def parse_obsidian_links(html_content) -> str:
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


##############################################
##############################################
##############################################

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
