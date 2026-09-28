from decimal import Decimal
import secrets

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


def generate_account_number():
    return "SB" + "".join(str(secrets.randbelow(10)) for _ in range(12))


def generate_card_number():
    return "4532" + "".join(str(secrets.randbelow(10)) for _ in range(12))


def generate_reference():
    return "TXN-" + secrets.token_hex(6).upper()


def generate_ticket_number():
    return "TKT-" + secrets.token_hex(4).upper()


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    monthly_salary = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Gross monthly salary in INR.",
    )
    date_of_birth = models.DateField(null=True, blank=True)
    customer_id = models.CharField(max_length=30, unique=True, blank=True)
    kyc_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.customer_id:
            self.customer_id = "CUS-" + secrets.token_hex(4).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class BankAccount(models.Model):
    ACCOUNT_TYPES = [
        ("SAVINGS", "Savings Account"),
        ("CURRENT", "Current Account"),
    ]
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("BLOCKED", "Blocked"),
        ("CLOSED", "Closed"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="account"
    )
    account_number = models.CharField(
        max_length=20, unique=True, default=generate_account_number
    )
    account_type = models.CharField(
        max_length=20, choices=ACCOUNT_TYPES, default="SAVINGS"
    )
    balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00")
    )
    minimum_balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("1000.00")
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="ACTIVE"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.account_number} - {self.user.username}"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("DEPOSIT", "Deposit"),
        ("WITHDRAW", "Withdrawal"),
        ("TRANSFER", "Transfer"),
        ("RECEIVE", "Money Received"),
        ("CARD", "Card Payment"),
        ("LOAN", "Loan"),
    ]
    STATUS_CHOICES = [
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("PENDING", "Pending"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transactions"
    )
    account = models.ForeignKey(
        BankAccount, on_delete=models.CASCADE, related_name="transactions"
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    reference = models.CharField(
        max_length=30, unique=True, default=generate_reference
    )
    description = models.CharField(max_length=255, blank=True)
    card = models.ForeignKey(
        "Card", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="transactions",
    )
    card_transaction_type = models.CharField(
        max_length=10,
        choices=[("DEBIT", "Debit Card Payment"), ("CREDIT", "Credit Card Payment")],
        blank=True,
    )
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="SUCCESS"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["account", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return self.reference


class Card(models.Model):
    CARD_TYPES = [
        ("DEBIT", "Debit Card"),
        ("CREDIT", "Credit Card"),
    ]
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("BLOCKED", "Blocked"),
        ("EXPIRED", "Expired"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cards"
    )
    account = models.ForeignKey(
        BankAccount, on_delete=models.CASCADE, related_name="cards"
    )
    card_type = models.CharField(max_length=10, choices=CARD_TYPES)
    card_number = models.CharField(
        max_length=16, unique=True, default=generate_card_number
    )
    cvv = models.CharField(max_length=3)
    expiry_date = models.DateField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="ACTIVE"
    )
    daily_limit = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("50000.00")
    )
    monthly_limit = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("50000.00"),
        validators=[MinValueValidator(Decimal("1.00"))],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["account", "card_type"],
                name="one_card_type_per_account",
            )
        ]

    def masked_number(self):
        return "**** **** **** " + self.card_number[-4:]

    def __str__(self):
        return self.masked_number()


class Loan(models.Model):
    LOAN_TYPES = [
        ("PERSONAL", "Personal Loan"),
        ("EDUCATION", "Education Loan"),
        ("HOME", "Home Loan"),
    ]
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("CLOSED", "Closed"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="loans"
    )
    account = models.ForeignKey(
        BankAccount, on_delete=models.CASCADE, related_name="loans"
    )
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    monthly_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Monthly salary declared at the time of loan application.",
    )
    interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("10.50")
    )
    tenure_months = models.PositiveIntegerField(default=12)
    outstanding_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00")
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="PENDING"
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.loan_type} - {self.amount}"


class LoanEligibilityRule(models.Model):
    LOAN_TYPES = Loan.LOAN_TYPES

    loan_type = models.CharField(max_length=20, choices=LOAN_TYPES, unique=True)
    minimum_monthly_salary = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("15000.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    max_loan_salary_multiplier = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("10.00"),
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Maximum loan amount = monthly salary × this multiplier.",
    )
    minimum_card_monthly_limit = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("50000.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    max_card_utilization_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("80.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["loan_type"]

    def __str__(self):
        return f"{self.get_loan_type_display()} eligibility rule"


class SupportTicket(models.Model):
    CATEGORIES = [
        ("ACCOUNT", "Account"),
        ("CARD", "Debit/Credit Card"),
        ("TRANSACTION", "Transaction"),
        ("LOAN", "Loan"),
        ("OTHER", "Other"),
    ]
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("IN_PROGRESS", "In Progress"),
        ("RESOLVED", "Resolved"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="support_tickets"
    )
    ticket_number = models.CharField(
        max_length=30, unique=True, default=generate_ticket_number
    )
    category = models.CharField(max_length=20, choices=CATEGORIES)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="OPEN"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ticket_number


class Notification(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=150)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
