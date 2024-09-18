from django import forms
from .models import Budget, Expense
from datetime import datetime
import os


class BudgetForm(forms.ModelForm):
    class Meta:
        months = [f"{i}-{datetime.now().year-1}" for i in range(6, 13)]
        months += [f"{i}-{datetime.now().year}" for i in range(1, 13)]
        months += [f"{i}-{datetime.now().year+1}" for i in range(1, 7)]
        months = tuple([(month, month) for month in months])
        
        model = Budget
        fields = "__all__"
        widgets = {'budget_month': forms.Select(choices=months)}

class MonthForm(forms.Form):
    months = tuple([(budget.id, budget.budget_month) for budget in Budget.objects.all()])
    month = forms.ChoiceField(choices=months)

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = "__all__"
        widgets = {
            'date': forms.DateInput(format="%Y-%m-%d", attrs={'type': 'date'}),
            }
    
    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        self.fields['amount'].widget.attrs['placeholder'] = 'Amount...'
        self.fields['description'].widget.attrs['placeholder'] = 'Description...'
        self.fields['merchant'].widget.attrs['placeholder'] = 'Merchant...'

class EmailForm(forms.Form):
    username = forms.EmailField(initial='example@example.com', disabled=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': "****"}), disabled=True, initial='*****')

