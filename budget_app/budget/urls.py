from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("change_month/<str:budget_month>/", views.change_month, name="change_month"),
    path("add_budget/", views.add_budget, name="add_budget"),
    path("add_expense/", views.add_expense, name="add_expense"),
    path("edit_expense/<int:id>/", views.edit_expense, name="edit_expense"),
    path("edit_budget/<int:id>/", views.edit_budget, name="edit_budget"),
    path("delete_expense/<int:id>/", views.delete_expense, name="delete_expense"),
    path("budget_api/<str:budget_month>/", views.budget_api, name="budget_api"),
    path("check_email/", views.check_email, name="check_email"),
    path("add_email_expenses/", views.add_email_expenses, name="add_email_expenses"),
    path("budget_visuals/", views.budget_visuals, name="budget_visuals"),
]