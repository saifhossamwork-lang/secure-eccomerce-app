# Secure E-Commerce Application

A security-focused e-commerce web application built with Flask and SQLite, designed to demonstrate secure software development practices and mitigation of common web vulnerabilities.

## Overview

This project implements a role-based online shopping platform with secure authentication and protection against common attack vectors outlined in the OWASP Top 10.

The objective was to design and develop a functional web application while applying real-world security controls at both the application and database levels.

---

## Key Security Features

- Role-Based Access Control (RBAC) for Customers, Sellers, and Administrators
- Secure authentication with salted password hashing (bcrypt)
- Two-Factor Authentication (2FA)
- Protection against:
  - SQL Injection
  - Cross-Site Scripting (XSS)
  - Cross-Site Request Forgery (CSRF)
- Input validation and secure session handling

---

## Technologies Used

- **Backend:** Python, Flask
- **Database:** SQLite
- **Frontend:** HTML, CSS, Bootstrap
- **Security Controls:** RBAC, CSRF Protection, Password Hashing
- **Environment:** Linux

---

## Application Features

- User registration and login system
- Product listing and management
- Shopping cart functionality
- Order processing
- Admin dashboard for user and product control

---

## Running the Application

```bash
git clone https://github.com/saifhossamwork-lang/secure-eccomerce-app.git
cd secure-eccomerce-app
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
