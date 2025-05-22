# Tentative de faire un blog perso

Ce projet est un blog / digital garden construit avec :

- **Robyn** ([Robyn](https://robyn.tech/), API Python utilisant [Actix](https://actix.rs/))
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
   uv run app.py
   ```
   
   ou

   ```bash
   uv run robyn app.py --help # Pour le développement
   ```
3. Ouvrir [http://localhost:5000](http://localhost:5000)

## Structure du projet

- `app.py` : API Robyn
- `components/` : Composants HTMX
- `articles/` : Contient les articles markdown servis
- `static/` : Assets statiques (icônes, images)

## Déploiement

- Dockerfile et fly.toml inclus pour déploiement sur Fly.io
