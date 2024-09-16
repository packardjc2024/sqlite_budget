from django.db import models
from datetime import datetime

class Budget(models.Model):
    budget_month = models.CharField(blank=False, max_length=7, unique=True, null=False)
    gas = models.DecimalField(blank=False, decimal_places=2, max_digits=6, null=False)
    food = models.DecimalField(blank=False, decimal_places=2, max_digits=6, null=False)
    internet = models.DecimalField(blank=False, decimal_places=2, max_digits=6, null=False)
    phone = models.DecimalField(blank=False, decimal_places=2, max_digits=6, null=False)
    electric = models.DecimalField(blank=False, decimal_places=2, max_digits=6, null=False)
    trash = models.DecimalField(blank=False, decimal_places=2, max_digits=6, null=False)
    mortgage = models.DecimalField(blank=False, decimal_places=2, max_digits=6, null=False)
    child_care = models.DecimalField(blank=False, decimal_places=2, max_digits=6, null=False)
    insurance = models.DecimalField(blank=False, decimal_places=2, max_digits=6, null=False)
    
    def __get_columns(self):
        return [key for key in self.__dict__.keys() if key not in ('_state', 'id', 'budget_month')]
        
    def table_columns(self):
        return self.__get_columns() + ['Total']
    
    def totals(self):
        columns = {key: self.__dict__[key] for key in self.__get_columns()}
        columns['Total'] = sum(columns.values())
        return columns
    
    def spent(self):
        totals = self.totals()
        expenses = Expense.objects.filter(budget_id=self.id)
        spent = {key: 0 for key in totals.keys()}
        for expense in expenses:
            if expense.line_item in spent.keys():
                spent[expense.line_item] += expense.amount
                spent['Total'] += expense.amount
        return spent
    
    def remaining(self):
        totals = self.totals()
        spent = self.spent()
        return {key: totals[key] - spent[key] for key in totals.keys()}
   

class Expense(models.Model):
    current_month = datetime.now().strftime("%-m-%Y")
    try:
        current_budget = Budget.objects.filter(budget_month=current_month).values('id')[0]['id']
        default_budget = current_budget
    except IndexError:
        default_budget = None

    class PaymentMethod(models.TextChoices):
        credit = 'credit_card', 'Credit Card'
        debit  = 'debit_card', 'Debit Card'
        cash = 'cash', 'Cash'
        check = 'check', 'Check'

    class LineItem(models.TextChoices):
        gas = 'gas', 'Gas'
        food = 'food', 'Food'
        internet = 'internet', 'Internet'
        phone = 'phone', 'Phone'
        electric = 'electric', 'Electric'
        trash = 'trash', 'Trash'
        mortgage = 'mortgage', 'Mortgage'
        child_care = 'child_care', 'Child Care'
        insurance = 'insurance', 'Insurance'

    description = models.CharField(max_length=20, blank=False, null=False)
    amount = models.DecimalField(decimal_places=2, blank=False, max_digits=6, null=False)
    date = models.DateField(blank=False, default=datetime.now().strftime("%Y-%m-%d"))
    merchant = models.CharField(max_length=20, blank=False)
    line_item = models.CharField(blank=False, choices=LineItem.choices, max_length=20,
                                 default=LineItem.food, null=False)
    payment_method = models.CharField(max_length=11, blank=False, default=PaymentMethod.credit,
                                      choices=PaymentMethod.choices, null=False)
    budget_id = models.IntegerField(blank=False, null=False, default=default_budget,
                                    choices=tuple([(budget['id'], budget['budget_month']) for budget in Budget.objects.values('id', 'budget_month')]))

    def table_columns(self):
        return [key for key in self.__dict__.keys() if key not in ('_state')]