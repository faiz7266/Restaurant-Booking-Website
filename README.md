
# EcoFinds — Sustainable Second‑Hand Marketplace (Flask + JSON)

## Features (matches the PDF spec)
- User Authentication (Signup/Login with email + password)
- Profile Dashboard (edit username, avatar URL, and bio)
- Product Listing Creation (title, description, category, price, image placeholder)
- Product Management (view, edit, delete your listings)
- Product Browsing feed with search and category filter
- Product Detail view
- Cart (add/remove, total, checkout)
- Previous Purchases
- Mobile‑friendly responsive UI

## Run Locally
```bash
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Recommended VS Code Extensions
- **Python** (ms-python.python) — language support and debugger
- **Pylance** (ms-python.vscode-pylance) — faster IntelliSense
- **Jinja** (wholroyd.jinja) — syntax highlight for HTML templates
- **Live Server** (ritwickdey.liveserver) — optional for static previews

## Notes
- This is an MVP using JSON files as storage (no SQL). For production, add password hashing and real image uploads.
