# GearByte

A full-featured e-commerce platform built with Django REST Framework, featuring product management, shopping cart functionality, order processing, and a PC rental system.

## Features

### Store Management
- Product catalog with categories
- Shopping cart functionality
- Order processing system
- Address management
- Payment integration with Chargily
- User authentication and authorization

### PC Rental System
- PC inventory management
- Rental requests and tracking
- Review and rating system
- Like/Dislike functionality for reviews


## Installation

1. Clone the repository:
```bash
git clone https://github.com/alicia-guechari/Project.git
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with the following variables:
```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

EMAIL_HOST=your-email-host
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-email-password

CHARGILI_PUBLIC_KEY=your-chargily-public-key
CHARGILI_SECRET_KEY=your-chargily-secret-key
```

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```
