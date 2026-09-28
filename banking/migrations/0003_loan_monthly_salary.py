from decimal import Decimal

from django.db import migrations, models
from django.core.validators import MinValueValidator


class Migration(migrations.Migration):
    dependencies = [
        ("banking", "0002_loan_card_rules"),
    ]

    operations = [
        migrations.AddField(
            model_name="loan",
            name="monthly_salary",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                help_text="Monthly salary declared at the time of loan application.",
                max_digits=12,
                validators=[MinValueValidator(Decimal("0.00"))],
            ),
        ),
    ]
