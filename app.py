from robyn import Robyn, ALLOW_CORS
from robyn.templating import JinjaTemplate
from urllib.parse import unquote
from markupsafe import Markup
import markdown as md
import pathlib
import os
import re

# Initialisation
app = Robyn(__file__)
ALLOW_CORS(app, origins=["http://localhost:0.0.0.0/"])
current_file_path = pathlib.Path(__file__).parent.resolve()
jinja = JinjaTemplate(os.path.join(current_file_path, "components"))
app.serve_directory("/static", "static")

##############################################
# COMPONENTS
##############################################


@app.get("/components/navbar")
def navbar_component():
    # Render the navbar component
    return jinja.render_template("navbar.html")


@app.get("/components/palette")
def palette_component():
    # Render the palette component
    return jinja.render_template("palette.html")


@app.get("/components/login")
def login_component():
    # Render the login component
    return jinja.render_template("hey")


@app.get("/components/user-card")
def user_card_component():
    # Render the user card component
    return jinja.render_template("user-card.html")


@app.get("/components/search/:query")
def palette_search_component(request):
    query = request.path_params.get("query")
    ### SEARCH FUNCTIONALITY ###
    if query == "suggestions":
        results = [
            {
                "title": f"Result for '{query}'",
                "description": f"This is a match for your search: {query}",
            },
            {
                "title": "Another result",
                "description": f"Another description related to '{query}'",
            },
            {"title": "Third match", "description": f"More content about '{query}'"},
        ]
    else:
        results = [
            {
                "title": f"Result for '{query}'",
                "description": f"This is a match for your search: {query}",
            },
            {
                "title": "Another result",
                "description": f"Another description related to '{query}'",
            },
            {"title": "Third match", "description": f"More content about '{query}'"},
        ]
    return jinja.render_template("search-results.html", results=results)


@app.get("/components/article/:article_id")
def article_component(request):
    article_id = request.path_params.get("article_id")
    try:
        # URL decode the article_id to handle special characters
        decoded_article_id = unquote(article_id)

        try:
            with open(f"articles/{decoded_article_id}.md", "r") as file:
                md_content = file.read()
        except FileNotFoundError:
            return f"Article {article_id} not found"

        html_content = md.markdown(md_content, extensions=["tables"])
        html_content = parse_obsidian_links(html_content)

        return jinja.render_template("article.html", content=Markup(html_content))
    except TimeoutError as e:
        return {"Fatal Error ": f"{e}"}


##############################################
# API
##############################################


@app.get("/api/v1/hello")
def hello_world():
    return {"response": "Hello World!"}


##############################################
# ROUTER
##############################################


@app.get("/")
def index():
    return jinja.render_template("index.html")


@app.get("/about")
def about():
    try:
        with open("articles/about.md", "r") as file:
            md_content = file.read()
    except FileNotFoundError:
        return "About page not found"

    html_content = md.markdown(md_content, extensions=["tables"])
    html_content = parse_obsidian_links(html_content)

    return jinja.render_template("article.html", content=Markup(html_content))


@app.get("/lab")
def lab():
    return jinja.render_template("lab.html")


##############################################
# UTILITIES
##############################################


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


##############################################
##############################################


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.start(host="0.0.0.0", port=port)
