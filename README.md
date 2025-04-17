# Pharmacy Management System

A comprehensive web-based Pharmacy Management System built with Flask, SQLite, and SQLAlchemy. This system helps manage medicines, customers, prescriptions, sales, and employees in a pharmacy setting.

## Features

- **User Authentication**
  - Secure login system
  - Admin dashboard
  - Password hashing
  - Session management

- **Medicine Management**
  - Add/Edit/Delete medicines
  - Track stock levels
  - Expiry date monitoring
  - Category-based organization
  - Stock alerts for low inventory

- **Customer Management**
  - Customer registration
  - Customer history
  - Contact information
  - Prescription tracking

- **Sales Management**
  - Record sales transactions
  - Generate invoices
  - Track daily/monthly sales
  - Sales history

- **Prescription Management**
  - Digital prescription records
  - Medicine dosage tracking
  - Doctor information
  - Prescription history

- **Employee Management**
  - Employee records
  - Role management
  - Contact information
  - Sales attribution

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF
- **Database Migrations**: Flask-Migrate

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- Git

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pharmacy_project
```

2. Create a virtual environment:
```bash
python -m venv .venv
```

3. Activate the virtual environment:
- Windows:
```bash
.venv\Scripts\activate
```
- Unix or MacOS:
```bash
source .venv/bin/activate
```

4. Install required packages:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the project root:
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/pharmacy.db
```

6. Initialize the database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

7. Create an admin user:
```bash
python reset_db.py
```

## Running the Application

1. Start the Flask development server:
```bash
flask run
```

2. Access the application at `http://127.0.0.1:5000`

3. Login with default admin credentials:
- Username: admin
- Password: admin123

## Project Structure 