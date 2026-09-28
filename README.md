# Finova Bank — Django Banking Application

Educational banking management system built with Python, Django and SQLite.

## Included functionality

- Customer registration, login and logout
- **One bank account per customer** (database-enforced OneToOne relationship)
- Savings and Current accounts
- Minimum-balance rules
- Deposit and withdrawal
- Account-to-account money transfer
- Transaction history and unique transaction references
- **Maximum one Debit Card + one Credit Card per bank account**
- Loan applications
- Customer support tickets
- Notifications
- Customer profile
- Live dashboard balance/notification polling
- Django Admin for users, accounts, cards, transactions, loans, tickets and notifications
- Staff-only Bank Admin dashboard
- Responsive emerald/teal/gold UI
- CSRF protection on POST forms
- Atomic money operations using database transactions and row locking

## Demo accounts

Run:

    python manage.py setup_demo

Then use:

    Admin username: admin
    Admin password: Admin@12345

    Customer username: customer
    Customer password: Customer@12345

The admin account can access:

    http://127.0.0.1:8000/admin/

The custom staff dashboard is:

    http://127.0.0.1:8000/bank-admin/

## Windows setup

Open PowerShell in the folder containing `manage.py`:

    cd "C:\path\to\Finova_Bank_Django_New_UI\finova_bank_project"
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python manage.py check
    python manage.py migrate
    python manage.py setup_demo
    python manage.py runserver

Open:

    http://127.0.0.1:8000/

Customer login:

    http://127.0.0.1:8000/login/

Customer registration:

    http://127.0.0.1:8000/register/

Bank Admin:

    http://127.0.0.1:8000/bank-admin/

Django Admin:

    http://127.0.0.1:8000/admin/

## If PowerShell blocks activation

Run once:

    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Then:

    .\venv\Scripts\Activate.ps1

If PowerShell asks for confirmation, answer `Y` at that prompt. Do not type `Y` as a separate command afterward.

## Reset the classroom database

Stop the server with `Ctrl+C`, delete `db.sqlite3`, then run:

    python manage.py migrate
    python manage.py setup_demo

Do not delete migration files.

## Important

This is an educational banking simulation, not production banking software. A real banking platform requires additional controls such as MFA, encryption and key management, KYC/AML workflows, fraud monitoring, audit logging, payment-network integrations, secure card/token handling, rate limiting, penetration testing and regulatory controls.


## New loan and card controls

- Customer profiles may store monthly salary for general profile information.
- **Loan applications now ask for Monthly Salary directly on the loan application form.** The entered salary is used for that application's eligibility check and saved with the loan as a salary snapshot. A profile salary is not required to apply.
- Loan applications check a configurable minimum salary, salary-based maximum loan amount, and active card criteria.
- Each loan type has a configurable eligibility rule in **Django Admin → Loan Eligibility Rules**.
- Debit and credit cards have monthly transaction limits.
- The Transactions page has a card-payment form for active debit/credit cards.
- Card payments cannot exceed the card's monthly limit. Debit-card payments also require the account minimum balance to be maintained.
- Current-month card usage is displayed on the Transactions page.

### Demo eligibility defaults

| Loan | Minimum salary | Maximum amount | Minimum card monthly limit | Max card utilization |
|---|---:|---:|---:|---:|
| Personal | ₹15,000 | 10 × salary | ₹50,000 | 80% |
| Education | ₹10,000 | 20 × salary | ₹30,000 | 80% |
| Home | ₹25,000 | 30 × salary | ₹1,00,000 | 80% |

These values are **educational demo rules** and can be changed by the bank administrator. They are not a real lending/credit decision model.
