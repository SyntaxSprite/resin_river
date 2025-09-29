# 🌊 Resin River

> A modern e-commerce platform for custom resin-inspired furniture and art pieces

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.0+-092E20?style=flat-square&logo=django&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)

## 📋 Overview

Resin River is a full-featured e-commerce web application built with Django that allows customers to browse, purchase, and wishlist custom resin furniture pieces. The platform provides an intuitive shopping experience with features like detailed product views, shopping cart management, and wishlist functionality.

## ✨ Key Features

- 🛍️ **Product Catalog** - Browse through a curated collection of resin furniture
- 🔍 **Detailed Product Views** - Multiple images and comprehensive descriptions
- 🛒 **Shopping Cart** - Session-based cart management
- ❤️ **Wishlist** - Save favorite items for later
- 🏷️ **Tag System** - Categorize products for easy navigation
- 📱 **Responsive Design** - Optimized for all devices
- 🔐 **Session Management** - Secure user session handling

## 🛠️ Tech Stack

**Backend:**
- Python 3.8+
- Django 4.0+
- Django ORM for database management

**Frontend:**
- HTML5
- CSS3
- JavaScript

**Database:**
- SQLite (Development)
- PostgreSQL (Production ready)

## 🚀 Getting Started

### Prerequisites

```bash
Python 3.8 or higher
pip (Python package manager)
virtualenv (recommended)
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/SyntaxSprite/resin_river.git
cd resin_river
```

2. **Create and activate virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up the database**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create a superuser (admin)**
```bash
python manage.py createsuperuser
```

6. **Run the development server**
```bash
python manage.py runserver
```

7. **Access the application**
```
Open your browser and navigate to: http://127.0.0.1:8000/
Admin panel: http://127.0.0.1:8000/admin/
```

## 📁 Project Structure

```
resin_river/
├── manage.py
├── requirements.txt
├── resin_river/           # Project configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── store/                 # Main app
│   ├── models.py         # Database models
│   ├── views.py          # View logic
│   ├── urls.py           # URL routing
│   └── templates/        # HTML templates
├── static/               # CSS, JS, Images
└── media/                # User uploaded content
```

## 💡 Core Functionality

### Product Management

The `Items` model handles all product-related data:
- Multiple image support (up to 3 images per product)
- Rich text descriptions
- Price management
- Tag-based categorization
- SEO-friendly slugs

### Shopping Cart

Session-based cart implementation:
- Add/remove items
- Persistent across sessions
- No login required
- Lightweight and fast

### Wishlist

Save items for future reference:
- Quick add/remove functionality
- Session-based storage
- Easy cart conversion

## 🎯 Key Views

| View | Purpose | Method |
|------|---------|--------|
| `ItemDetails` | Display product information | GET, POST |
| `AddToCart` | Add products to cart | POST |
| `WishList` | Manage wishlist items | GET, POST |
| `Cart` | View and manage cart | GET, POST |

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=your-database-url
```

### Settings

Key settings to configure in `settings.py`:
- `MEDIA_ROOT` and `MEDIA_URL` for image uploads
- `STATIC_ROOT` and `STATIC_URL` for static files
- Database configuration for production

## 📸 Screenshots

*Coming soon - Add screenshots of your application here*

## 🚧 Roadmap

- [ ] User authentication and profiles
- [ ] Payment gateway integration
- [ ] Order management system
- [ ] Email notifications
- [ ] Product reviews and ratings
- [ ] Advanced search and filtering
- [ ] Inventory management

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**SyntaxSprite**
- GitHub: [@SyntaxSprite](https://github.com/SyntaxSprite)
- Company: Craftit Hub

## 🙏 Acknowledgments

- Django Documentation
- Django Community
- All contributors and supporters

---

<div align="center">
  
**⭐ Star this repo if you find it helpful!**

Made with ❤️ by [SyntaxSprite](https://github.com/SyntaxSprite)

</div>
