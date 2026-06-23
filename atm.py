class atm():
    def __init__(self, balance,pin=None):
        self.balance=balance
        self.pin=pin

    def create_pin(self,new_pin):
        if self.pin is None:
            self.pin = new_pin

    def check_balance(self):
        if self.pin is None:
            print("Please create a PIN first.")
            return
        print("Enter pin:")

        entered_pin=int(input())
        if entered_pin==self.pin :
            print("Your balance is : ", self.balance)
        else :
            print("Invalid PIN.")

    def withdraw(self):
        print("Enter amount to withdraw: ")

        amount=int(input())

        print("Enter Your pin:")

        entered_pin=int(input())

        if entered_pin==self.pin and amount <= self.balance:
            self.balance=self.balance-amount
            print("Withdraw complete")
        elif entered_pin==self.pin and amount > self.balance:
            print("Not enough balance")
            return
        else :
            print("Invalid PIN")
            return
            

    def deposit(self) : 
        print("Enter amount to deposit: ")

        amount=int(input())

        print("Enter Your pin:")

        entered_pin=int(input())

        if entered_pin==self.pin:
            self.balance=self.balance+amount
            print("Deposit complete")
        else :
            print("Invalid PIN")
            return

my_account=atm(1000)

#my_account.check_balance()

my_account.create_pin(1234)

# my_account.check_balance()
my_account.withdraw()
print(my_account.balance)

my_account.deposit()
