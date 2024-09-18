from ..models import Budget, Expense
import random


class Samples:
    def __init__(self):
        self.expense_id = Expense.objects.order_by('id').last().id
        if not self.expense_id:
            self.expense_id = 1
        self.budgets = []
        for i in range(1, 13):
            self.budgets.append({"id": i, "budget_month": f"{i}-2024"})
        self.line_items = {column: 200 for column in Budget().table_columns() if column not in ('id', 'budget_month', 'Total')}

    def create_budget_samples(self):
        for budget in self.budgets:
            to_add = budget
            to_add.update(self.line_items)
            Budget(**to_add).save()

    def create_expense_samples(self):
        for budget in self.budgets:
            for i in range(1, 21):
                expense = {
                    'id': self.expense_id,
                    'description': f'expense sample {i}',
                    'amount': round(random.uniform(10, 30), 2),
                    'date': f'2024-{str(budget['id'])}-{str(random.randint(1, 28))}',
                    'merchant': f"merchant sample {1}",
                    'line_item': random.choice(list(self.line_items.keys())),
                    'payment_method': random.choice(['Credit Card', 'Debit Card', 'Cash', 'Check']),
                    'budget_id': budget['id'],
                }
                self.expense_id += 1
                Expense(**expense).save()

if __name__ == "__main__":  
    samples = Samples()
    samples.create_budget_samples()
    samples.create_expense_samples()