class book:
    ID=1
    def __init__(self,title,author,year):
        self.title = title
        self.author = author
        self.year = year
        self.id=book.ID
        book.ID += 1

class user:
    
    ID=1

    def __init__(self,name):
        self.name = name
        self.ID = user.ID
        user.ID += 1

class loan:

    def __init__(self,user,book):
        self.user = user
        self.book = book

class library():

    def __init__(self):
        self.users = []
        self.books = []
        self.active_loans=[]

    def menu(self):

        while True:
            user_input=input(
                """
                Welcome to the Library !
                1. Enter 1 to register as User
                2. Enter 2 to register/add a book
                3. Enter 3 to list all the books
                4. Enter 4 to loan a book
                5. Enter 5 to return a book
                6. Enter 6 to exit
                """
            )
            if user_input=="1":
                print("Please provide your name to register")
                name=input("Name: ")
                user1=user(name)
                self.users.append(user1)
                print(f"Congrats, you are now registered!, Your ID is {user1.ID}")
                

            elif user_input=="2":
                self.add_book()
                print("Book added successfully!")
                
            
            
            elif user_input=="3":
                self.list_books()
                
            elif user_input=="4":
                print("Please provide your name and your Id:")
                name=input("Your name: ")
                user_id=int(input("Your ID: "))

                check=self.check_valid_user(name,user_id)

                if check==True:
                    print("Match Found !")
                    self.list_books()
                    print("Enter the Id of the book you want to loan:")
                    book_id=int(input("Book ID: "))
                    self.loan_book(name,user_id,book_id)
                    
                else:
                    print("User not found, Please register first.")
                    

            elif user_input=="5":
                print("Please provide your name and your Id:")
                name=input("Your name: ")
                user_id=int(input("Your ID: "))

                check=self.check_valid_user(name,user_id)

                if check==True:
                    print("Match Found !")
                    book=self.list_user_books_get_book(name,user_id)
                    self.return_book(name,user_id,book)
                    
                else:
                    print("User not found, Please register first.")
                    

            elif user_input=="6":
                print("Thank you for using the Library Management System!")
                break
            
            else:
                print("Invalid input. Please try again.")

              
    def check_valid_user(self,name,user_id):

        for user in self.users:
            if user.name==name and user.ID==user_id:
                return True
        return False
    
    def fetch_book(self,user_book_id):
        for book in self.books:
            if book.id == user_book_id:
                return book
        return None
    
    def fetch_user(self,user_name,user_id):
        for user in self.users:
            if user.name==user_name and user.ID==user_id:
                return user
        return None

    def loan_book(self,user_name,user_id,book_id):
        book=self.fetch_book(book_id)
        user=self.fetch_user(user_name,user_id)

        if book is None :
            print("Please enter a valid book ID")
              
        loan1=loan(user,book)
        self.active_loans.append(loan1)
        self.books.remove(book)
        print(f"Book '{book.title}' has been loaned to {user.name}.")
    
    def return_book(self,user_name,user_id,book):
        user=self.fetch_user(user_name,user_id)
        for loan in self.active_loans:
            if user==loan.user and book==loan.book:
                self.active_loans.remove(loan)
                self.books.append(book)
                print(f"Book '{book.title}' has been returned by {user.name}.")
                return
        print("Book not found in your borrowed books.")

    def add_book(self):
            print("Please provide the book details:")
            title=input("Title: ")
            author=input("Author: ")
            year=int(input("Year: "))
            book1=book(title,author,year)
            self.books.append(book1)
    
    def list_books(self):
        print("In this library, we have the following books:")
        for i in range(len(self.books)):
            print(f"-{self.books[i].title} by {self.books[i].author} published in year {self.books[i].year} and the ID of the book is {self.books[i].id}" )
    
    def list_user_books_get_book(self,user_name,user_id):
        user=self.fetch_user(user_name,user_id)
        print("You have loaned the following books:")
        for loan in self.active_loans:
            if loan.user==user:
                print(f"-{loan.book.title} by {loan.book.author} published in year {loan.book.year} and the ID of the book is {loan.book.id}" )
        
        print("Enter the ID of the book you want to return:")
        book_id=int(input("Book ID: "))
        
        for loan in self.active_loans:
            if loan.user==user and loan.book.id==book_id:
                return loan.book
        
        print("Book not found in your borrowed books.")

lib=library()
lib.menu()
    
            
    
