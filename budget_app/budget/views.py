from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from datetime import datetime
from .forms import ExpenseForm, MonthForm, BudgetForm, EmailForm
from .models import Budget, Expense
import json
import os
import imapclient
import matplotlib
from matplotlib import pyplot as plt
import numpy
from pathlib import Path

from .email_checker.check_email import EmailChecker

#App wide functions and variables
def create_context(request):
    if 'current_budget' not in request.session:
        request.session['current_budget'] = datetime.now().strftime("%-m-%Y")
    budget = Budget.objects.get(budget_month=request.session['current_budget'])
    return {
         'current_budget': request.session['current_budget'],
         'expenses': Expense.objects.filter(budget_id=budget.id).values(),
         'expense_columns': Expense().table_columns(),
         'budget_totals': budget.totals(),
         'budget_columns': Budget().table_columns(),
         'spent': budget.spent(),
         'remaining': budget.remaining(),
         'budget_id': budget.id,
         'months': tuple([(budget['id'], budget['budget_month']) for budget in Budget.objects.values('id', 'budget_month')]),
        }

def get_month_by_id(budget_id):
    return Budget.objects.filter(id=budget_id).values('budget_month')[0]['budget_month']

def calc_percentages(pct, values):
    value = round(pct/100*sum(values), 2)
    return f"{round(pct, 2)}%\n${value}"

def create_pie_chart(column, context):
    matplotlib.use('agg')
    sizes = [float(context['spent'][column]), float(context['remaining'][column])]
    fig, ax = plt.subplots(figsize=(2,2))
    ax.pie(sizes, explode=(0.1, 0), shadow=True, startangle=90,
            autopct=lambda pct: calc_percentages(pct, sizes),
            colors=('#f5c6cb', '#ffeeba'))
    ax.axis('equal')
    ax.set_title(column.replace('_', ' ').title())
    filename = Path.joinpath(Path.cwd(), f'budget/static/{column}.png')
    plt.savefig(fname=filename, dpi=100)


###############################################################################
# Views
def index(request):
    if request.method == "GET":
        try:
            context = create_context(request)
            return render(request, 'index.html', context=context)
        except:
            return render(request, 'first_budget.html', context={'budget_form': BudgetForm()})
    elif request.method == "POST":
        budget_form = BudgetForm(request.POST)
        if budget_form.is_valid():
            budget_form.save()
            request.session['current_budget'] = budget_form.cleaned_data['budget_month']
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'first_budget.html', context={'budget_form': budget_form})

def change_month(request, budget_month):
    request.session['current_budget'] = budget_month
    return HttpResponseRedirect(reverse('index'))

def add_budget(request):
    context = create_context(request)
    if request.method == "GET":
        context['budget_form'] = BudgetForm()
        return render(request, 'add_budget.html', context=context)
    elif request.method == "POST":
        form = BudgetForm(request.POST)
        if form.is_valid():
            print('valid')
            form.save()
            request.session['current_budget'] = form.cleaned_data['budget_month']
            return HttpResponseRedirect(reverse('index'))
        else:
            context['budget_form'] = form
            return render(request, 'add_budget.html', context=context)

def edit_expense(request, id):
    context = create_context(request)
    expense = Expense.objects.get(id=id)
    context['expense_form'] = ExpenseForm(instance=expense)
    if request.method == 'GET':
        return render(request, 'edit_expense.html', context=context)
    elif request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.id = id
            print(form.cleaned_data)
            form.save()
            request.session['current_budget'] = get_month_by_id(form.cleaned_data['budget_id'])
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'add_expense.html', context=context)

def delete_expense(request, id):
    Expense.objects.get(id=id).delete()
    return HttpResponseRedirect(reverse('index'))

def add_expense(request):
    context = create_context(request)
    if request.method == "GET":
        context['expense_form'] = ExpenseForm()
        return render(request, 'add_expense.html', context=context)
    elif request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            request.session['current_budget'] = get_month_by_id(form.cleaned_data['budget_id'])
            return HttpResponseRedirect(reverse('index'))
        else:
            context['expense_form'] = form
            return render(request, 'add_expense.html', context=context)
        
def edit_budget(request, id):
    context = create_context(request)
    budget = Budget.objects.get(id=id)
    context['budget_form'] = BudgetForm(instance=budget)
    context['budget_form'].fields['budget_month'].disabled = True
    if request.method == 'GET':
        return render(request, 'edit_budget.html', context=context)
    elif request.method == "POST":
        form = BudgetForm(request.POST)
        form.budget_month = budget.budget_month
        print(form.__dict__)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.id = id
            form.save()
            request.session['current_budget'] = budget.budget_month
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'edit_budget.html', context=context)
        
def budget_api(request, budget_month):
    try:
        budget = Budget.objects.get(budget_month=budget_month)
    except:
        return JsonResponse({'error': f'No budget for {budget_month}',
                             'solutions': 'Use format %m-%Y or create a new budget'})
    else:
        results = {"budget_month": budget_month, "budget_id": budget.id, "expenses": "No Expenses"}
        expenses = list(Expense.objects.filter(budget_id=budget.id).values())
        if expenses:
            results['expenses'] = expenses
        return JsonResponse(results)
    
def check_email(request):
    context = create_context(request)
    context['invalid_login'] = ""
    if request.method == "GET":
        context['email_form'] = EmailForm()
        return render(request, 'check_email.html', context=context)
    elif request.method == "POST":
        email_form = EmailForm(request.POST)
        if email_form.is_valid():
            try:
                email_expenses = EmailChecker().get_emails(email_form.cleaned_data['username'],
                                                        email_form.cleaned_data['password'])
                context['email_expenses'] = []
                context['prefixes'] = []
                i = 1
                for expense in email_expenses:
                    date = datetime.strptime(expense[1], "%m/%d/%Y")
                    context['email_expenses'].append(ExpenseForm(prefix=f"form{i}", initial={
                        'amount': expense[0],
                        'date': date.strftime("%Y-%m-%d"),
                        'merchant': expense[2][:20],
                    }))
                    context['prefixes'].append(i)
                    i += 1
                return render(request, 'email_results.html', context)
            except imapclient.exceptions.LoginError:
                context['email_form'] = email_form
                context['invalid_login'] = "Invalid username or password"
            return render(request, 'check_email.html', context=context)
        else:
            context['email_form'] = email_form
            return render(request, 'check_email.html', context=context)
        
def add_email_expenses(request):
    context = create_context(request)
    if request.method == "POST":
        prefixes = request.POST['prefixes']
        prefixes = [int(i) for i in prefixes[1:-1].split(',')]
        context['prefixes'] = []
        print(prefixes)
        print(type(prefixes))
        valid_forms = []
        invalid_forms = []
        for i in prefixes:
            form = ExpenseForm(request.POST, prefix=f"form{i}")
            if form.is_valid():
                valid_forms.append(form)
            else:
                invalid_forms.append(form)
                context['prefixes'].append(i)
        if valid_forms:
            for form in valid_forms:
                form.save()
        if invalid_forms:
            context['email_expenses'] = []
            for form in invalid_forms:
                context['email_expenses'].append(form)
            return render(request, 'email_results.html', context=context)
        else:
            return HttpResponseRedirect(reverse('index'))
        
def budget_visuals(request):
    context = create_context(request)
    if request.method == "GET":
        for column in context['budget_columns']:
            create_pie_chart(column, context)
    return render(request, 'matplotlib.html', context=context)


### login/authentication
### put in docker
### use sqlite and publish on pages
#### manually create models and forms using sql