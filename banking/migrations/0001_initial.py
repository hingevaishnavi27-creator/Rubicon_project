# Generated for the Finova Bank educational project.
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
import banking.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BankAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("account_number", models.CharField(default=banking.models.generate_account_number, max_length=20, unique=True)),
                ("account_type", models.CharField(choices=[("SAVINGS", "Savings Account"), ("CURRENT", "Current Account")], default="SAVINGS", max_length=20)),
                ("balance", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=15)),
                ("minimum_balance", models.DecimalField(decimal_places=2, default=Decimal("1000.00"), max_digits=15)),
                ("status", models.CharField(choices=[("ACTIVE", "Active"), ("BLOCKED", "Blocked"), ("CLOSED", "Closed")], default="ACTIVE", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="account", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="CustomerProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("phone", models.CharField(blank=True, max_length=15)),
                ("address", models.TextField(blank=True)),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                ("customer_id", models.CharField(blank=True, max_length=30, unique=True)),
                ("kyc_verified", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Card",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("card_type", models.CharField(choices=[("DEBIT", "Debit Card"), ("CREDIT", "Credit Card")], max_length=10)),
                ("card_number", models.CharField(default=banking.models.generate_card_number, max_length=16, unique=True)),
                ("cvv", models.CharField(max_length=3)),
                ("expiry_date", models.DateField()),
                ("status", models.CharField(choices=[("ACTIVE", "Active"), ("BLOCKED", "Blocked"), ("EXPIRED", "Expired")], default="ACTIVE", max_length=20)),
                ("daily_limit", models.DecimalField(decimal_places=2, default=Decimal("50000.00"), max_digits=12)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="cards", to="banking.bankaccount")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="cards", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
                "constraints": [
                    models.UniqueConstraint(fields=("account", "card_type"), name="one_card_type_per_account")
                ],
            },
        ),
        migrations.CreateModel(
            name="Loan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("loan_type", models.CharField(choices=[("PERSONAL", "Personal Loan"), ("EDUCATION", "Education Loan"), ("HOME", "Home Loan")], max_length=20)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=15)),
                ("interest_rate", models.DecimalField(decimal_places=2, default=Decimal("10.50"), max_digits=5)),
                ("tenure_months", models.PositiveIntegerField(default=12)),
                ("outstanding_amount", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=15)),
                ("status", models.CharField(choices=[("PENDING", "Pending"), ("APPROVED", "Approved"), ("REJECTED", "Rejected"), ("CLOSED", "Closed")], default="PENDING", max_length=20)),
                ("applied_at", models.DateTimeField(auto_now_add=True)),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="loans", to="banking.bankaccount")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="loans", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=150)),
                ("message", models.TextField()),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="SupportTicket",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("ticket_number", models.CharField(default=banking.models.generate_ticket_number, max_length=30, unique=True)),
                ("category", models.CharField(choices=[("ACCOUNT", "Account"), ("CARD", "Debit/Credit Card"), ("TRANSACTION", "Transaction"), ("LOAN", "Loan"), ("OTHER", "Other")], max_length=20)),
                ("subject", models.CharField(max_length=150)),
                ("message", models.TextField()),
                ("status", models.CharField(choices=[("OPEN", "Open"), ("IN_PROGRESS", "In Progress"), ("RESOLVED", "Resolved")], default="OPEN", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="support_tickets", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("transaction_type", models.CharField(choices=[("DEPOSIT", "Deposit"), ("WITHDRAW", "Withdrawal"), ("TRANSFER", "Transfer"), ("RECEIVE", "Money Received"), ("CARD", "Card Payment"), ("LOAN", "Loan")], max_length=20)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(Decimal("0.01"))])),
                ("reference", models.CharField(default=banking.models.generate_reference, max_length=30, unique=True)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("balance_after", models.DecimalField(decimal_places=2, max_digits=15)),
                ("status", models.CharField(choices=[("SUCCESS", "Success"), ("FAILED", "Failed"), ("PENDING", "Pending")], default="SUCCESS", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="transactions", to="banking.bankaccount")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="transactions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="transaction",
            index=models.Index(fields=["account", "-created_at"], name="banking_tra_account_5df5e0_idx"),
        ),
        migrations.AddIndex(
            model_name="transaction",
            index=models.Index(fields=["user", "-created_at"], name="banking_tra_user_id_5e5b35_idx"),
        ),
    ]
