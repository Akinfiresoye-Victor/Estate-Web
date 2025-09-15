# Estate-Web

Estate-Web is a simple Django-based website that helps users find properties without the stress of going through an estate agent. Properties are listed (with pictures, descriptions, etc.), and users can browse/list view, see details, and contact via the site.

---

## 📋 Features

- Listing of properties (e.g. houses, flats) for rent or sale  
- Property detail pages with media/images  
- Contact forms / member/inquiry support (allows interaction with property owners or agents)  
- User/member signup/authentication (if included)  
- Media handling (uploading / managing property photos)  
- Search/filter (if implemented) by location, price, etc.

---

## 💻 Tech Stack & Dependencies

- Python & Django as the web framework  
- Templates with HTML/CSS (and possibly Bootstrap or similar for styling)  
- Database (SQLite in development or your chosen DB in production)  
- Media storage (local or cloud) for property photos  
- Requirements listed in `requirements.txt`

---

## 🚀 Getting Started

1. Clone the repo  
   ```bash
   git clone https://github.com/Akinfiresoye-Victor/Estate-Web.git
   cd Estate-Web
## ✔Setting Environment
* python -m venv env
* env/Scripts/activate(windows)
* pip install -r requirements
* python manage.py makemigrations
* python manage.py migrate
