from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import transaction as db_transaction
from django.db.models import Sum

from .models import BankAccount, Card, LoanEligibilityRule, Notification, Transaction

MINIMUM_WITHDRAWAL = Decimal("100.00")


def _active_account_for_user(user, account_id):
    return (
        BankAccount.objects.select_for_update()
        .filter(id=account_id, user=user, status="ACTIVE")
        .first()
    )


def current_month_card_spend(card):
    today = date.today()
    return (
        Transaction.objects.filter(
            card=card,
            status="SUCCESS",
            card_transaction_type__in=["DEBIT", "CREDIT"],
            created_at__year=today.year,
            created_at__month=today.month,
        ).aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )


def validate_loan_eligibility(user, loan_type, amount, monthly_salary):
    amount = Decimal(amount)
    monthly_salary = Decimal(monthly_salary)
    if monthly_salary <= 0:
        return False, "Please enter a valid monthly salary greater than ₹0.", None

    rule, _ = LoanEligibilityRule.objects.get_or_create(
        loan_type=loan_type,
        defaults={
            "minimum_monthly_salary": Decimal("15000.00"),
            "max_loan_salary_multiplier": Decimal("10.00"),
            "minimum_card_monthly_limit": Decimal("50000.00"),
            "max_card_utilization_percent": Decimal("80.00"),
        },
    )

    if monthly_salary < rule.minimum_monthly_salary:
        return False, (
            f"Minimum monthly salary for this loan is ₹{rule.minimum_monthly_salary:,.2f}. "
            f"Your declared salary is ₹{monthly_salary:,.2f}."
        ), rule

    max_amount = monthly_salary * rule.max_loan_salary_multiplier
    if amount > max_amount:
        return False, (
            f"Requested loan exceeds the salary-based limit of ₹{max_amount:,.2f} "
            f"({rule.max_loan_salary_multiplier:g}× monthly salary)."
        ), rule

    active_cards = list(Card.objects.filter(user=user, status="ACTIVE"))
    if not active_cards:
        return False, "At least one active debit or credit card is required for loan eligibility.", rule

    suitable_card_found = False
    for card in active_cards:
        if card.monthly_limit < rule.minimum_card_monthly_limit:
            continue
        spend = current_month_card_spend(card)
        utilization = (spend / card.monthly_limit * Decimal("100")) if card.monthly_limit else Decimal("100")
        if utilization <= rule.max_card_utilization_percent:
            suitable_card_found = True
            break

    if not suitable_card_found:
        return False, (
            f"At least one active card must have a monthly limit of ₹{rule.minimum_card_monthly_limit:,.2f} "
            f"or more and current-month usage at or below {rule.max_card_utilization_percent:g}%."
        ), rule

    return True, "Eligible based on the configured salary and card criteria.", rule


@db_transaction.atomic
def deposit_money(user, account_id, amount, description=""):
    amount = Decimal(amount)
    if amount <= 0:
        raise ValueError("Deposit amount must be greater than ₹0.")
    account = _active_account_for_user(user, account_id)
    if not account:
        raise ValueError("Active bank account not found.")
    account.balance += amount
    account.save(update_fields=["balance", "updated_at"])
    txn = Transaction.objects.create(user=user, account=account, transaction_type="DEPOSIT", amount=amount,
        description=description or "Cash deposit", balance_after=account.balance, status="SUCCESS")
    Notification.objects.create(user=user, title="Deposit Successful", message=f"₹{amount:.2f} has been deposited into your account.")
    return txn


@db_transaction.atomic
def withdraw_money(user, account_id, amount, description=""):
    amount = Decimal(amount)
    if amount < MINIMUM_WITHDRAWAL:
        raise ValueError("Minimum withdrawal amount is ₹100.")
    account = _active_account_for_user(user, account_id)
    if not account:
        raise ValueError("Active bank account not found.")
    remaining = account.balance - amount
    if remaining < account.minimum_balance:
        raise ValueError(f"Minimum balance of ₹{account.minimum_balance:.2f} must be maintained.")
    account.balance = remaining
    account.save(update_fields=["balance", "updated_at"])
    txn = Transaction.objects.create(user=user, account=account, transaction_type="WITHDRAW", amount=amount,
        description=description or "Cash withdrawal", balance_after=account.balance, status="SUCCESS")
    Notification.objects.create(user=user, title="Withdrawal Successful", message=f"₹{amount:.2f} has been withdrawn from your account.")
    return txn


@db_transaction.atomic
def transfer_money(sender, sender_account_id, receiver_account_number, amount, description=""):
    amount = Decimal(amount)
    if amount <= 0:
        raise ValueError("Transfer amount must be greater than ₹0.")
    sender_account = _active_account_for_user(sender, sender_account_id)
    if not sender_account:
        raise ValueError("Sender account not found.")
    receiver_account = (BankAccount.objects.select_for_update().select_related("user")
        .filter(account_number=receiver_account_number, status="ACTIVE").first())
    if not receiver_account:
        raise ValueError("Receiver account not found.")
    if sender_account.id == receiver_account.id:
        raise ValueError("You cannot transfer money to your own account.")
    remaining = sender_account.balance - amount
    if remaining < sender_account.minimum_balance:
        raise ValueError(f"Transfer failed. You must maintain a minimum balance of ₹{sender_account.minimum_balance:.2f}.")
    sender_account.balance = remaining
    sender_account.save(update_fields=["balance", "updated_at"])
    receiver_account.balance += amount
    receiver_account.save(update_fields=["balance", "updated_at"])
    sender_txn = Transaction.objects.create(user=sender, account=sender_account, transaction_type="TRANSFER", amount=amount,
        description=description or f"Transfer to {receiver_account.account_number}", balance_after=sender_account.balance, status="SUCCESS")
    Transaction.objects.create(user=receiver_account.user, account=receiver_account, transaction_type="RECEIVE", amount=amount,
        description=description or f"Received from {sender_account.account_number}", balance_after=receiver_account.balance, status="SUCCESS")
    Notification.objects.create(user=sender, title="Transfer Successful", message=f"₹{amount:.2f} transferred to {receiver_account.account_number}.")
    Notification.objects.create(user=receiver_account.user, title="Money Received", message=f"₹{amount:.2f} received from {sender_account.account_number}.")
    return sender_txn


@db_transaction.atomic
def card_payment(user, card_id, amount, description=""):
    amount = Decimal(amount)
    if amount <= 0:
        raise ValueError("Card transaction amount must be greater than ₹0.")
    card = Card.objects.select_for_update().select_related("account").filter(
        id=card_id, user=user, status="ACTIVE", account__status="ACTIVE"
    ).first()
    if not card:
        raise ValueError("Active card not found.")
    if card.expiry_date < date.today():
        raise ValueError("This card has expired.")

    monthly_spend = current_month_card_spend(card)
    if monthly_spend + amount > card.monthly_limit:
        remaining = max(card.monthly_limit - monthly_spend, Decimal("0.00"))
        raise ValueError(f"Monthly card limit exceeded. Remaining limit this month: ₹{remaining:,.2f}.")

    if card.card_type == "DEBIT":
        account = BankAccount.objects.select_for_update().get(pk=card.account_id)
        remaining = account.balance - amount
        if remaining < account.minimum_balance:
            raise ValueError(f"Insufficient funds. You must maintain ₹{account.minimum_balance:,.2f} minimum balance.")
        account.balance = remaining
        account.save(update_fields=["balance", "updated_at"])
        balance_after = account.balance
    else:
        balance_after = card.account.balance

    txn = Transaction.objects.create(
        user=user, account=card.account, transaction_type="CARD", amount=amount,
        card=card, card_transaction_type=card.card_type,
        description=description or f"{card.get_card_type_display()} payment",
        balance_after=balance_after, status="SUCCESS",
    )
    Notification.objects.create(
        user=user, title=f"{card.get_card_type_display()} Transaction",
        message=f"₹{amount:,.2f} charged to {card.masked_number()}.",
    )
    return txn
