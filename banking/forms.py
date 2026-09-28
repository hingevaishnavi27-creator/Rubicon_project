from decimal import Decimal

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import (
    BankAccount,
    Card,
    Loan,
    SupportTicket,
    CustomerProfile,
    Transaction,
)


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}))

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "password1",
            "password2",
        ]


class AccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ["account_type"]


class AmountForm(forms.Form):
    amount = forms.DecimalField(
        min_value=Decimal("0.01"),
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"min": "0.01", "step": "0.01", "placeholder": "0.00"}
        ),
    )
    description = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(
            attrs={"placeholder": "Optional description"}
        ),
    )


class TransferForm(forms.Form):
    to_account_number = forms.CharField(
        max_length=20,
        label="Receiver Account Number",
        widget=forms.TextInput(
            attrs={"placeholder": "Example: SB123456789012"}
        ),
    )
    amount = forms.DecimalField(
        min_value=Decimal("0.01"),
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"min": "0.01", "step": "0.01"}
        ),
    )
    description = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(
            attrs={"placeholder": "Optional description"}
        ),
    )


class CardForm(forms.Form):
    card_type = forms.ChoiceField(choices=Card.CARD_TYPES)


class CardTransactionForm(forms.Form):
    card = forms.ModelChoiceField(
        queryset=Card.objects.none(),
        label="Card",
    )
    amount = forms.DecimalField(
        min_value=Decimal("0.01"), max_digits=15, decimal_places=2,
        widget=forms.NumberInput(attrs={"min": "0.01", "step": "0.01"}),
    )
    description = forms.CharField(
        required=False, max_length=255,
        widget=forms.TextInput(attrs={"placeholder": "Merchant / transaction description"}),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["card"].queryset = Card.objects.filter(
                user=user, status="ACTIVE"
            ).select_related("account")
            self.fields["card"].label_from_instance = (
                lambda card: f"{card.get_card_type_display()} • {card.masked_number()} • ₹{card.monthly_limit:,.0f}/month"
            )


class LoanForm(forms.ModelForm):
    monthly_salary = forms.DecimalField(
        label="Monthly Salary (₹)",
        min_value=Decimal("0.01"),
        max_digits=12,
        decimal_places=2,
        help_text="Enter your gross monthly salary. This salary is used only for this loan application's eligibility check and is saved with the application.",
        widget=forms.NumberInput(
            attrs={
                "min": "0.01",
                "step": "100",
                "placeholder": "Example: 50000",
            }
        ),
    )

    class Meta:
        model = Loan
        fields = [
            "loan_type",
            "monthly_salary",
            "amount",
            "interest_rate",
            "tenure_months",
        ]
        widgets = {
            "amount": forms.NumberInput(attrs={"min": "1000", "step": "100"}),
            "interest_rate": forms.NumberInput(attrs={"step": "0.01"}),
            "tenure_months": forms.NumberInput(attrs={"min": "1", "max": "360"}),
        }


class TicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ["category", "subject", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ["phone", "address", "monthly_salary", "date_of_birth"]
        widgets = {
            "monthly_salary": forms.NumberInput(attrs={"min": "0", "step": "100"}),
        }
