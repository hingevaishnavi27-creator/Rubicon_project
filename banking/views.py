from datetime import date
from decimal import Decimal
import secrets

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect

from .forms import (
    RegisterForm,
    AccountForm,
    AmountForm,
    TransferForm,
    CardForm,
    CardTransactionForm,
    LoanForm,
    TicketForm,
    ProfileForm,
)
from .models import (
    BankAccount,
    Transaction,
    Card,
    Loan,
    SupportTicket,
    Notification,
    CustomerProfile,
)
from .services import deposit_money, withdraw_money, transfer_money, card_payment, current_month_card_spend, validate_loan_eligibility


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "home.html")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            CustomerProfile.objects.create(
                user=user,
                phone=form.cleaned_data["phone"],
                address=form.cleaned_data["address"],
            )
            login(request, user)
            messages.success(
                request,
                "Welcome to Finova Bank. Your profile has been created.",
            )
            return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(
        request,
        "registration/register.html",
        {"form": form},
    )


@login_required
def dashboard(request):
    account = getattr(request.user, "account", None)
    total_balance = account.balance if account else Decimal("0.00")
    recent = request.user.transactions.select_related("account").all()[:6]
    unread = request.user.notifications.filter(is_read=False).count()

    return render(
        request,
        "dashboard.html",
        {
            "account": account,
            "total_balance": total_balance,
            "recent": recent,
            "unread": unread,
        },
    )


@login_required
def accounts(request):
    return render(
        request,
        "accounts.html",
        {"account": getattr(request.user, "account", None)},
    )


@login_required
def create_account(request):
    if hasattr(request.user, "account"):
        messages.warning(
            request,
            "You already have a bank account. Only one account is allowed per user.",
        )
        return redirect("accounts")

    if request.method == "POST":
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.minimum_balance = (
                Decimal("1000.00")
                if account.account_type == "SAVINGS"
                else Decimal("5000.00")
            )
            account.save()

            Notification.objects.create(
                user=request.user,
                title="Account Created",
                message=(
                    f"Account {account.account_number} "
                    "has been created successfully."
                ),
            )
            messages.success(
                request,
                "Bank account created successfully.",
            )
            return redirect("accounts")
    else:
        form = AccountForm()

    return render(
        request,
        "form_page.html",
        {
            "form": form,
            "title": "Open Bank Account",
            "button": "Open Account",
        },
    )


@login_required
def deposit(request):
    if not hasattr(request.user, "account"):
        messages.error(request, "Open a bank account first.")
        return redirect("create_account")

    form = AmountForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            deposit_money(
                request.user,
                request.user.account.id,
                form.cleaned_data["amount"],
                form.cleaned_data["description"],
            )
            messages.success(request, "Money deposited successfully.")
            return redirect("dashboard")
        except ValueError as exc:
            messages.error(request, str(exc))

    return render(
        request,
        "form_page.html",
        {"form": form, "title": "Deposit Money", "button": "Deposit"},
    )


@login_required
def withdraw(request):
    if not hasattr(request.user, "account"):
        messages.error(request, "Open a bank account first.")
        return redirect("create_account")

    form = AmountForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            withdraw_money(
                request.user,
                request.user.account.id,
                form.cleaned_data["amount"],
                form.cleaned_data["description"],
            )
            messages.success(request, "Money withdrawn successfully.")
            return redirect("dashboard")
        except ValueError as exc:
            messages.error(request, str(exc))

    return render(
        request,
        "form_page.html",
        {"form": form, "title": "Withdraw Money", "button": "Withdraw"},
    )


@login_required
def transfer(request):
    if not hasattr(request.user, "account"):
        messages.error(request, "Open a bank account first.")
        return redirect("create_account")

    form = TransferForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            transfer_money(
                request.user,
                request.user.account.id,
                form.cleaned_data["to_account_number"].strip(),
                form.cleaned_data["amount"],
                form.cleaned_data["description"],
            )
            messages.success(request, "Money transferred successfully.")
            return redirect("dashboard")
        except ValueError as exc:
            messages.error(request, str(exc))

    return render(
        request,
        "form_page.html",
        {
            "form": form,
            "title": "Transfer Money",
            "button": "Transfer Money",
        },
    )


@login_required
def transactions(request):
    data = request.user.transactions.select_related("account", "card").all()
    form = CardTransactionForm(request.POST or None, user=request.user)

    if request.method == "POST" and form.is_valid():
        try:
            card_payment(
                request.user,
                form.cleaned_data["card"].id,
                form.cleaned_data["amount"],
                form.cleaned_data["description"],
            )
            messages.success(request, "Card transaction completed successfully.")
            return redirect("transactions")
        except ValueError as exc:
            messages.error(request, str(exc))

    card_summary = [
        {"card": card, "used": current_month_card_spend(card),
         "remaining": max(card.monthly_limit - current_month_card_spend(card), Decimal("0.00"))}
        for card in request.user.cards.filter(status="ACTIVE")
    ]
    return render(request, "transactions.html", {
        "transactions": data, "card_form": form, "card_summary": card_summary,
    })


@login_required
def cards(request):
    data = request.user.cards.select_related("account").all()
    return render(
        request,
        "cards.html",
        {"cards": data},
    )


@login_required
def apply_card(request):
    account = getattr(request.user, "account", None)

    if not account:
        messages.error(request, "Open a bank account before applying for a card.")
        return redirect("create_account")

    form = CardForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        card_type = form.cleaned_data["card_type"]

        if Card.objects.filter(
            account=account,
            card_type=card_type,
        ).exists():
            messages.error(
                request,
                f"You already have a {card_type.lower()} card for this account.",
            )
            return redirect("cards")

        card = Card.objects.create(
            user=request.user,
            account=account,
            card_type=card_type,
            monthly_limit=Decimal("50000.00") if card_type == "DEBIT" else Decimal("100000.00"),
            cvv=str(secrets.randbelow(900) + 100),
            expiry_date=date(date.today().year + 5, 12, 31),
        )

        Notification.objects.create(
            user=request.user,
            title="Card Issued",
            message=f"Your {card_type.lower()} card has been issued.",
        )
        messages.success(
            request,
            f"{card_type.title()} card created successfully.",
        )
        return redirect("cards")

    return render(
        request,
        "form_page.html",
        {"form": form, "title": "Apply for Card", "button": "Apply for Card"},
    )


@login_required
def loans(request):
    data = request.user.loans.select_related("account").all()
    return render(request, "loans.html", {"loans": data})


@login_required
def apply_loan(request):
    account = getattr(request.user, "account", None)

    if not account:
        messages.error(request, "Open a bank account before applying for a loan.")
        return redirect("create_account")

    form = LoanForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        eligible, reason, rule = validate_loan_eligibility(
            request.user,
            form.cleaned_data["loan_type"],
            form.cleaned_data["amount"],
            form.cleaned_data["monthly_salary"],
        )
        if not eligible:
            form.add_error(None, reason)
        else:
            loan = form.save(commit=False)
            loan.user = request.user
            loan.account = account
            loan.monthly_salary = form.cleaned_data["monthly_salary"]
            loan.outstanding_amount = loan.amount
            loan.save()

            Notification.objects.create(
                user=request.user,
                title="Loan Application Submitted",
                message="Your loan application passed the configured eligibility checks and is pending review.",
            )
            messages.success(request, "Loan application submitted successfully.")
            return redirect("loans")

    return render(
        request,
        "form_page.html",
        {"form": form, "title": "Apply for Loan", "button": "Submit Application"},
    )


@login_required
def support(request):
    tickets = request.user.support_tickets.all()
    return render(request, "support.html", {"tickets": tickets})


@login_required
def create_ticket(request):
    form = TicketForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        ticket = form.save(commit=False)
        ticket.user = request.user
        ticket.save()

        Notification.objects.create(
            user=request.user,
            title="Support Ticket Created",
            message=f"Ticket {ticket.ticket_number} has been created.",
        )
        messages.success(
            request,
            f"Support ticket {ticket.ticket_number} created.",
        )
        return redirect("support")

    return render(
        request,
        "form_page.html",
        {"form": form, "title": "Customer Service", "button": "Create Ticket"},
    )


@login_required
def profile(request):
    profile_obj, _ = CustomerProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile_obj)

    return render(
        request,
        "profile.html",
        {"form": form, "profile": profile_obj},
    )


@login_required
def notifications(request):
    data = request.user.notifications.all()
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, "notifications.html", {"notifications": data})


@login_required
def live_data(request):
    account = getattr(request.user, "account", None)
    unread = request.user.notifications.filter(is_read=False).count()

    return JsonResponse(
        {
            "account_number": account.account_number if account else None,
            "balance": str(account.balance) if account else "0.00",
            "unread_notifications": unread,
        }
    )


@staff_member_required
def bank_admin_dashboard(request):
    users_count = User.objects.count()
    accounts_count = BankAccount.objects.count()
    cards_count = Card.objects.count()
    transactions_count = Transaction.objects.count()
    loans_count = Loan.objects.count()
    tickets_count = SupportTicket.objects.count()
    total_balance = (
        BankAccount.objects.filter(status="ACTIVE")
        .aggregate(total=Sum("balance"))["total"]
        or Decimal("0.00")
    )
    recent_transactions = Transaction.objects.select_related(
        "user", "account"
    )[:10]

    return render(
        request,
        "bank_admin/dashboard.html",
        {
            "users_count": users_count,
            "accounts_count": accounts_count,
            "cards_count": cards_count,
            "transactions_count": transactions_count,
            "loans_count": loans_count,
            "tickets_count": tickets_count,
            "total_balance": total_balance,
            "recent_transactions": recent_transactions,
        },
    )
