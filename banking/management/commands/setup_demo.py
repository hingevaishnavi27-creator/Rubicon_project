from decimal import Decimal
from datetime import date

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from banking.models import BankAccount, CustomerProfile, Card, LoanEligibilityRule


class Command(BaseCommand):
    help = "Create the Finova demo administrator and demo customer."

    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@finovabank.local",
                "first_name": "Bank",
                "last_name": "Administrator",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        admin.email = "admin@finovabank.local"
        admin.is_staff = True
        admin.is_superuser = True
        admin.is_active = True
        admin.set_password("Admin@12345")
        admin.save()

        demo, _ = User.objects.get_or_create(
            username="customer",
            defaults={
                "email": "customer@finovabank.local",
                "first_name": "Demo",
                "last_name": "Customer",
                "is_active": True,
            },
        )
        demo.set_password("Customer@12345")
        demo.save()

        CustomerProfile.objects.get_or_create(
            user=demo,
            defaults={
                "phone": "9999999999",
                "address": "Demo Address, Pune",
                "monthly_salary": Decimal("50000.00"),
            },
        )

        profile = CustomerProfile.objects.get(user=demo)
        profile.monthly_salary = Decimal("50000.00")
        profile.save(update_fields=["monthly_salary"])

        account, account_created = BankAccount.objects.get_or_create(
            user=demo,
            defaults={
                "account_type": "SAVINGS",
                "balance": Decimal("25000.00"),
                "minimum_balance": Decimal("1000.00"),
                "status": "ACTIVE",
            },
        )


        Card.objects.get_or_create(
            user=demo,
            account=account,
            card_type="DEBIT",
            defaults={
                "monthly_limit": Decimal("50000.00"),
                "daily_limit": Decimal("50000.00"),
                "cvv": "123",
                "expiry_date": date.today().replace(year=date.today().year + 5, month=12, day=31),
            },
        )

        # Demo eligibility rules. These are educational defaults and can be edited from Django admin.
        default_rules = {
            "PERSONAL": (Decimal("15000.00"), Decimal("10.00"), Decimal("50000.00"), Decimal("80.00")),
            "EDUCATION": (Decimal("10000.00"), Decimal("20.00"), Decimal("30000.00"), Decimal("80.00")),
            "HOME": (Decimal("25000.00"), Decimal("30.00"), Decimal("100000.00"), Decimal("80.00")),
        }
        for loan_type, (salary, multiplier, card_limit, utilization) in default_rules.items():
            LoanEligibilityRule.objects.update_or_create(
                loan_type=loan_type,
                defaults={
                    "minimum_monthly_salary": salary,
                    "max_loan_salary_multiplier": multiplier,
                    "minimum_card_monthly_limit": card_limit,
                    "max_card_utilization_percent": utilization,
                },
            )

        self.stdout.write(self.style.SUCCESS(
            "Demo setup completed."
        ))
        self.stdout.write("Admin username: admin")
        self.stdout.write("Admin password: Admin@12345")
        self.stdout.write("Customer username: customer")
        self.stdout.write("Customer password: Customer@12345")
        self.stdout.write(
            f"Customer account: {account.account_number}"
        )
