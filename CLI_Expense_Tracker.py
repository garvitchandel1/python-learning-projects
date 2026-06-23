from dataclasses import  dataclass
from datetime import date as Date
from typing import Dict, List,Generator

from dataclasses import dataclass, field
from collections import defaultdict
import calendar 


@dataclass
class Expense:
    id:int = field(init=False)
    _counter:int=field(default=0, init=False, repr=False)
    name:str
    amount:float
    category:str
    date: Date =field(default_factory=Date.today)

    def __post_init__(self)->None:
        type(self)._counter += 1
        self.id = self._counter
        if self.amount <=0:
            raise ValueError("Amount must be a positive number.")
        if not self.name:
            raise ValueError("Name cannot be empty.")
        if not self.category:
            raise ValueError("Category cannot be empty.")


    def __str__(self)->str:
        return f"ID: {self.id}, Name: {self.name}, Amount: {self.amount}, Category: {self.category}, Date: {self.date}"

class ExpenseTracker:

    def __init__(self)->None:
        self.expenses :List[Expense] = []
        self.monthly_summary : Dict[str,int]=defaultdict(float)
        self.total_spend: float= 0
    
    def add_expense(self, name: str, amount: float, category: str) -> None:
        expense = Expense(name=name, amount=amount, category=category)
        self.expenses.append(expense)
    
    
    def delete_expense(self, expense_id: int) -> bool:
        expense_to_delete=self.fetch_expense(expense_id)
        if expense_to_delete is None:
            return False
        self.expenses.remove(expense_to_delete)
        return True
    
    # def filter_expenses_by_category(self,category:str)->list[Expense]:
    #     return [expense for expense in self.expenses if expense.category.lower() == category.lower()]

    def filter_expenses_by_category(self,category:str)->Generator[Expense, None, None]:
        for expense in self.expenses:
            if expense.category.lower()==category.lower():
                yield expense


    def fetch_expense(self,expense_id:int)->Expense | None:
        for expense in self.expenses:
            if expense.id == expense_id:
                return expense
        return None
    
    def create_summary(self,month:int,year:int) -> None:
        self.total_spend = 0
        self.monthly_summary.clear()
        for expense in self.expenses:
            if expense.date.month == month and expense.date.year == year:
                self.total_spend +=expense.amount

                self.monthly_summary[expense.category] += expense.amount







class ExpenseTrackerCLI:

    def __init__(self):
        self.expense_tracker = ExpenseTracker()
        

    def menu(self)->None:

        while True:
            user_input=input(
                """
                Welcome to the Your Expense Tracker, What would you like to do? 
                
                1. Add Expense
                2. View Your Expenses
                3. Delete any Expense
                4. Filter expenses by category
                5. View Monthly Summary
                6. Exit

                """
            )
            if user_input=="1":
                print("Please provide the details of the expense you want to add:")
                name=input("Name: ")

                try:
             
                   amount=float(input("Amount: ")) 
                except ValueError:
                    print("Amount can only be a number.")
                    continue
        
                category=input("Category: ")

                try :
                    self.expense_tracker.add_expense(name,amount,category)
                except ValueError as e:
                    print(f"Error adding expense: {e}")

            elif user_input=="2":
                self.view_expenses()
            
            elif user_input=="3":
                self.delete_expense()
            
            elif user_input=="4":
                category=input("Enter the category to filter by: ")
                filtered_list=self.expense_tracker.filter_expenses_by_category(category)
                flag=True
                for expense in filtered_list:
                    flag=False
                    print(expense)
                
                if flag:
                    print("No expenses found for the specified category.")
                    
                
            elif user_input=='5':
                try:
                    year=int(input("Enter the year for the monthly summary: "))
                    
                except ValueError:
                    print("Year can only be a number.")
                    continue
                try:
                    month=int(input("Enter the month for the monthly summary [1-12]: "))

                    if month > 12 or month < 1 :
                        print("Invalid month. Please enter a month between 1 and 12.")
                        continue
                except ValueError:
                    print("Month can only be a number.")
                    continue
                self.expense_tracker.create_summary(month, year)
                print(f"The total spend for {calendar.month_name[month]}  {year} is: ", self.expense_tracker.total_spend)
                print("Monthly summary by category:")
                for category, amount in self.expense_tracker.monthly_summary.items():
                    print(f"  {category}: {amount}")

            elif user_input=="6":
                print("Thank you for using the Expense Tracker!")
                break

            else:
                print("Invalid input. Please try again.")
    def view_expenses(self)->None:
        if len(self.expense_tracker.expenses) == 0:
            print("No expenses to display.")
        else:
            for expense in self.expense_tracker.expenses:
                print(f"{expense.id}. Spent {expense.amount} on {expense.name} on {expense.date}")
            
            try:
                expense_id = int(input(("Enter the ID of the expense you want to expand:"))) 
            except ValueError:
                print("Please enter a valid expense ID.")
                return
            expense_to_view=self.expense_tracker.fetch_expense(expense_id)

            if expense_to_view is None:
                print("Expense not found.")
            else:
                print(expense_to_view) 

    
    def delete_expense(self)->None:
        if len(self.expense_tracker.expenses)==0:
            print("No expenses to delete.")
            return
        else:
            for expense in self.expense_tracker.expenses:
                print(f"{expense.id}. Spent {expense.amount} on {expense.name} on {expense.date}")
            try:
                expense_id = int(input(("Enter the ID of the expense you want to delete: "))) 
            except ValueError:
                print("Please enter a valid expense ID.")
                return
            
            flag= self.expense_tracker.delete_expense(expense_id)
            
            if flag: 
            
                    print("Expense deleted successfully.")
            else:
                    print("Expense not found.")

tracker=ExpenseTrackerCLI()
tracker.menu()


# my_expense_tracker=ExpenseTracker()

# my_expense_tracker.menu()


# my_first_expense=Expense("Groceries", 50.0, "Food")
# my_second_expense=Expense("Utilities", 100.0, "Bills")
# print(my_first_expense)
# print(my_second_expense)