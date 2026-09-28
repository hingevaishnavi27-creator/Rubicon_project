from django.contrib import admin

from .models import (
    CustomerProfile,
    BankAccount,
    Transaction,
    Card,
    Loan,
    SupportTicket,
    Notification,
    LoanEligibilityRule,
)


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "customer_id",
        "user",
        "phone",
        "monthly_salary",
        "kyc_verified",
        "created_at",
    )
    search_fields = (
        "customer_id",
        "user__username",
        "user__email",
        "phone",
    )
    list_filter = ("kyc_verified",)


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = (
        "account_number",
        "user",
        "account_type",
        "balance",
        "minimum_balance",
        "status",
        "created_at",
    )
    search_fields = (
        "account_number",
        "user__username",
        "user__email",
    )
    list_filter = ("account_type", "status")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "user",
        "account",
        "transaction_type",
        "card_transaction_type",
        "card",
        "amount",
        "balance_after",
        "status",
        "created_at",
    )
    search_fields = (
        "reference",
        "user__username",
        "account__account_number",
        "description",
    )
    list_filter = ("transaction_type", "status", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = (
        "masked_card",
        "user",
        "account",
        "card_type",
        "status",
        "expiry_date",
        "monthly_limit",
        "created_at",
    )
    search_fields = (
        "card_number",
        "user__username",
        "account__account_number",
    )
    list_filter = ("card_type", "status")
    list_editable = ("monthly_limit",)

    @admin.display(description="Card Number")
    def masked_card(self, obj):
        return obj.masked_number()


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "account",
        "loan_type",
        "monthly_salary",
        "amount",
        "outstanding_amount",
        "status",
        "applied_at",
    )
    search_fields = (
        "user__username",
        "account__account_number",
    )
    list_filter = ("loan_type", "status")


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = (
        "ticket_number",
        "user",
        "category",
        "subject",
        "status",
        "created_at",
    )
    search_fields = (
        "ticket_number",
        "user__username",
        "subject",
    )
    list_filter = ("category", "status")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "title",
        "is_read",
        "created_at",
    )
    search_fields = (
        "user__username",
        "title",
        "message",
    )
    list_filter = ("is_read", "created_at")


admin.site.site_header = "Finova Bank Administration"
admin.site.site_title = "Finova Bank Admin"
admin.site.index_title = "Bank Management"


@admin.register(LoanEligibilityRule)
class LoanEligibilityRuleAdmin(admin.ModelAdmin):
    list_display = ("loan_type", "minimum_monthly_salary", "max_loan_salary_multiplier", "minimum_card_monthly_limit", "max_card_utilization_percent", "updated_at")
    list_editable = ("minimum_monthly_salary", "max_loan_salary_multiplier", "minimum_card_monthly_limit", "max_card_utilization_percent")
