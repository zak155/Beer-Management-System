# 🍺 Beer Sales & Distribution Management System

A full-stack Beer Sales & Distribution Management System built with Django. The system manages the complete workflow of beer distribution, including agents, stores, finance approval, inventory management, order processing, and payment integration.

---

## 📌 Features

### Authentication & Authorization

- User Login
- Role-Based Access Control
- Admin Dashboard
- Agent Dashboard
- Store Manager Dashboard
- Finance Dashboard
- Email Verification
- Password Management

---

### Agent Management

- Register Agents
- Agent Profile
- Region Assignment
- Contract Management
- License Upload
- Activate/Deactivate Agents

---

### Store Management

- Create Stores
- Assign Store Managers
- Store Inventory
- Product Refill
- Store Reports

---

### Product Management

- Add Products
- Update Products
- Delete Products
- Product Images
- Pricing Management

---

### Order Management

- Agent Orders
- Transaction History
- Finance Approval
- Store Approval
- Delivery Workflow

---

### Inventory Management

- Store Stock
- Product Quantity Tracking
- Inventory Refill
- Product Movement Logs

---

### Finance

- Transaction Approval
- Payment Tracking
- Invoice Generation
- Financial Reports

---

### Reports

- Agent Reports
- Store Reports
- Finance Reports
- Transaction Reports

---

## 🛠 Tech Stack

### Backend

- Python
- Django
- Django ORM

### Database

- SQLite (Development)
- PostgreSQL (Production Ready)

### Frontend

- HTML
- CSS
- Bootstrap
- JavaScript

### Authentication

- Django Authentication
- Django Groups
- Email Verification

### Payment

- Yenepay (Legacy)
- Telebirr (Planned)

---

## Project Architecture

```
Agent
   │
   ▼
Create Order
   │
   ▼
Finance Approval
   │
   ▼
Store Approval
   │
   ▼
Inventory Update
   │
   ▼
Delivery
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/yourusername/Beer-Sales-Distribution-System.git
```

Go to project directory

```bash
cd Beer-Sales-Distribution-System
```

Create virtual environment

```bash
python -m venv venv
```

Activate environment

Windows

```bash
venv\Scripts\activate
```

Linux

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run migrations

```bash
python manage.py migrate
```

Run server

```bash
python manage.py runserver
```

---

## Future Improvements

- ✅ Telebirr Payment Integration
- Docker Deployment
- REST API
- JWT Authentication
- SMS Notifications
- Email Notifications
- Dashboard Analytics
- Inventory Forecasting
- PDF Invoice Generation
- Celery Background Tasks

---

## License

This project is developed for educational and portfolio purposes.

---

## Author

**Robel Amare**

Software Engineer | Django Developer

