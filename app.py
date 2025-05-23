from robyn import Robyn, ALLOW_CORS, AuthenticationHandler, Request
from robyn.templating import JinjaTemplate
from robyn.authentication import BearerGetter, Identity
from urllib.parse import unquote
from markupsafe import Markup
import markdown as md
import pathlib
import os
import re

# Initialisation du backend Rust
try:
    from backend import square

    assert square(5) == 25, "Square function is not working correctly"
    print(f"Square imported successfully. Square(5) = {square(5)}")
except ImportError as e:
    print(f"Failed to import square: {e}")

# Initialisation du serveur Robyn
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
    """
    Render the palette search results component based on the query.
    """
    query = request.path_params.get("query")
    ### SEARCH FUNCTIONALITY ###

    return jinja.render_template(
        "search-results.html", results=palette_search_router(query)
    )


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
    return jinja.render_template("lab.html")


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
    return jinja.render_template("index.html")


@app.get("/auth", auth_required=True)
def auth(request: Request):
    # This route method will only be executed if the user is authenticated
    # Otherwise, a 401 response will be returned
    return "Hello, world"


##############################################
# UTILITIES
##############################################


# Hardcoded secret key for testing
TEST_SECRET_KEY = "cleosupersecretkey-2025"


class BasicAuthHandler(AuthenticationHandler):
    def authenticate(self, request: Request):
        token = self.token_getter.get_token(request)
        # Accept the hardcoded key as a Bearer token
        if token == TEST_SECRET_KEY:
            return Identity(claims={"user": "cleo"})
        return None


app.configure_authentication(BasicAuthHandler(token_getter=BearerGetter()))


def parse_obsidian_links(html_content: str) -> str:
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


def palette_search_router(query: str) -> list[dict]:
    """
    Search for a query in the palette.
    This function should return a JSON that look like :
    [
        {
            "type": "article",
            "title": "Result 1",
            "description": "Description for result 1"
        },
        {
            "type": "other",
            "title": "Result 2",
            "description": "Description for result 2"
        }
    ]

    It includes the types articles and commands.
    """

    if query.startswith(":"):
        return handle_palette_commands(query)
    else:
        return handle_palette_articles(query)


def handle_palette_commands(query: str) -> list[dict]:
    command = query[1:]
    # Handle command search
    return [
        {
            "type": "command",
            "title": f"First Command: {command}",
            "description": f"Description for command {command}",
        },
        {
            "type": "command",
            "title": f"Second Command: {command}",
            "description": f"Description for command {command}",
        },
        {
            "type": "command",
            "title": f"Third Command: {command}",
            "description": f"Description for command {command}",
        },
    ]


def handle_palette_articles(query: str) -> list[dict]:
    return [
        {
            "type": "article",
            "title": f"Article: {query}",
            "description": f"Description for article {query}",
        }
    ]


##############################################
##############################################


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.start(host="0.0.0.0", port=port)

# In order to test:
# curl -H "Authorization: Bearer cleosupersecretkey-2025" http://localhost:5000/auth
