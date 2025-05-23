# Tentative de faire un blog perso

Ce projet est un blog / digital garden construit avec :

- **Robyn** ([Robyn](https://robyn.tech/), API Python utilisant [Actix](https://actix.rs/) et intégrant [pyo3](https://pyo3.rs/main/getting-started.html?))
- **Jinja2** (templates HTML)
- **HTMX** (chargement dynamique côté client)
- **Alpine.js** (réactivité légère côté client)
- **Markdown** (contenu des articles)

## Fonctionnalités principales

- Navigation entre articles markdown
- Composants UI modulaires (navbar, palette, user-card, etc.)
- Prise en charge des liens Obsidian et notes de bas de page
- Palette de recherche dynamique (EN COURS)

## Lancer en local
1. Installer [uv](https://docs.astral.sh/uv/)

2. Lancer le serveur :

   ```bash
   uv run robyn app.py --log-level=WARN --compile-rust-path="." --fast    # Pour serveur production
   ```
   
   ou

   ```bash
   uv run robyn app.py --log-level=DEBUG --compile-rust-path="." --dev # Pour le développement
   ```
3. Ouvrir [http://localhost:5000](http://localhost:5000)

## Structure du projet

- `app.py` : API Robyn.
- `backend.rs` : Certaines fonctions backend en Rust utilisée par Python.
- `components/` : Composants HTMX+Alpine.
- `articles/` : Contient les articles markdown servis.
- `static/` : Assets statiques (icônes, images).

## Déploiement

- Dockerfile et fly.toml inclus pour déploiement sur Fly.io
