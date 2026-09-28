from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("accounts/", views.accounts, name="accounts"),
    path("accounts/open/", views.create_account, name="create_account"),
    path("deposit/", views.deposit, name="deposit"),
    path("withdraw/", views.withdraw, name="withdraw"),
    path("transfer/", views.transfer, name="transfer"),
    path("transactions/", views.transactions, name="transactions"),
    path("cards/", views.cards, name="cards"),
    path("cards/apply/", views.apply_card, name="apply_card"),
    path("loans/", views.loans, name="loans"),
    path("loans/apply/", views.apply_loan, name="apply_loan"),
    path("support/", views.support, name="support"),
    path("support/create/", views.create_ticket, name="create_ticket"),
    path("profile/", views.profile, name="profile"),
    path("notifications/", views.notifications, name="notifications"),
    path("api/live-data/", views.live_data, name="live_data"),
    path("bank-admin/", views.bank_admin_dashboard, name="bank_admin_dashboard"),
]
