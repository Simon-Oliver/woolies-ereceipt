import db_util

total_expenses = db_util.get_total_expenses_by_month()
for expenses in total_expenses:
    index, date, total = expenses
    print(f'{date} - ${total:.2f}')

