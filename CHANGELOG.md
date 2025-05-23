# 0.1.0

- Initial structure using HTMX, Alpine.js, Python.
- Implemented Obsidian Markdown style blog article view.

# 0.1.1

- Switched from `flask` to `robyn`, transfer to `FastAPI` will be easier if `robyn` is not maintained.
- Added /lab endpoint with new design.
- Added the Search Palette component.

# 0.1.1.1

- Added the skeleton for importing Rust module in `app.py`.

# 0.1.2

- Added `fuzzy_search` in `backend.rs`.
- Now serving results for `palette_search_component`, for both articles and commands.
- Updated `Dockerfile` to permit Rust compilation during deployment.
- Added tests for `fuzzy_search`.

