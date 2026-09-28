from django.db import migrations, models
import django.core.validators
import decimal
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("banking", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="customerprofile",
            name="monthly_salary",
            field=models.DecimalField(
                decimal_places=2,
                default=decimal.Decimal("0.00"),
                help_text="Gross monthly salary in INR.",
                max_digits=12,
                validators=[django.core.validators.MinValueValidator(decimal.Decimal("0.00"))],
            ),
        ),
        migrations.AddField(
            model_name="card",
            name="monthly_limit",
            field=models.DecimalField(
                decimal_places=2,
                default=decimal.Decimal("50000.00"),
                max_digits=12,
                validators=[django.core.validators.MinValueValidator(decimal.Decimal("1.00"))],
            ),
        ),
        migrations.AddField(
            model_name="transaction",
            name="card_transaction_type",
            field=models.CharField(
                blank=True,
                choices=[("DEBIT", "Debit Card Payment"), ("CREDIT", "Credit Card Payment")],
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="transaction",
            name="card",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="transactions",
                to="banking.card",
            ),
        ),
        migrations.CreateModel(
            name="LoanEligibilityRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("loan_type", models.CharField(choices=[("PERSONAL", "Personal Loan"), ("EDUCATION", "Education Loan"), ("HOME", "Home Loan")], max_length=20, unique=True)),
                ("minimum_monthly_salary", models.DecimalField(decimal_places=2, default=decimal.Decimal("15000.00"), max_digits=12, validators=[django.core.validators.MinValueValidator(decimal.Decimal("0.00"))])),
                ("max_loan_salary_multiplier", models.DecimalField(decimal_places=2, default=decimal.Decimal("10.00"), help_text="Maximum loan amount = monthly salary × this multiplier.", max_digits=6, validators=[django.core.validators.MinValueValidator(decimal.Decimal("0.01"))])),
                ("minimum_card_monthly_limit", models.DecimalField(decimal_places=2, default=decimal.Decimal("50000.00"), max_digits=12, validators=[django.core.validators.MinValueValidator(decimal.Decimal("0.00"))])),
                ("max_card_utilization_percent", models.DecimalField(decimal_places=2, default=decimal.Decimal("80.00"), max_digits=5, validators=[django.core.validators.MinValueValidator(decimal.Decimal("0.00"))])),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["loan_type"]},
        ),
    ]
