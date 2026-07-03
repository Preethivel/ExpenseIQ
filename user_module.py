# user_module.py — LAYER 1: User login, financial setup
#
# Person (ABC) -> FinanceUser   demonstrates ABSTRACTION + INHERITANCE.
# FinanceUser overrides get_role()/__str__()   demonstrates POLYMORPHISM (method overriding).
# Private attributes + @property               demonstrate ENCAPSULATION.
# Passwords are hashed with hashlib (never stored/compared in plain text) for real AUTHENTICATION.
import datetime
import hashlib
from abc import ABC, abstractmethod

users = {}


def _hash_password(plain_password):
    # one-way hash -- the original password is never stored or written to disk
    return hashlib.sha256(plain_password.encode()).hexdigest()


# ---------- ABSTRACT BASE CLASS ----------
class Person(ABC):
    """Cannot be instantiated on its own -- every concrete Person must define get_role()."""
    def __init__(self, username):
        self._username = username          # protected: subclasses may read/extend this

    @property
    def username(self):
        return self._username

    @abstractmethod
    def get_role(self):
        raise NotImplementedError

    def __str__(self):
        return f"{self.get_role()}: {self._username}"


# ---------- DOUBLY LINKED LIST (fixed expenses) ----------
class ExpenseNode:
    def __init__(self, name, amount):
        self.name, self.amount, self.next, self.prev = name, amount, None, None


class FixedExpenseList:
    def __init__(self):
        self.__head = self.__tail = None       # ENCAPSULATION: kept private, no outside code needs them

    def add_expense(self, name, amount):
        node = ExpenseNode(name, amount)
        if self.__head is None:
            self.__head = self.__tail = node
        else:
            node.prev, self.__tail.next, self.__tail = self.__tail, node, node

    def get_total(self):
        total, cur = 0, self.__head
        while cur: total, cur = total + cur.amount, cur.next
        return total

    def show_forward(self):
        print("\nFixed Expenses (forward order):")
        cur = self.__head
        while cur: print(cur.name, "-> Rs.", cur.amount); cur = cur.next

    def show_backward(self):
        print("\nFixed Expenses (backward order):")
        cur = self.__tail
        while cur: print(cur.name, "-> Rs.", cur.amount); cur = cur.prev

    def to_list(self):
        result, cur = [], self.__head
        while cur: result.append((cur.name, cur.amount)); cur = cur.next
        return result

    def show_all_expenses(self):
        if self.__head is None: print("No fixed expenses yet."); return
        print("\nFixed Expenses:")
        cur = self.__head
        while cur: print("-", cur.name, "Rs.", cur.amount); cur = cur.next

    def remove_expense(self, name):
        if self.__head is None: print("No expenses to remove."); return
        if self.__head.name.lower() == name.lower():
            self.__head = self.__head.next
            if self.__head is None: self.__tail = None
            else: self.__head.prev = None
            print("Expense removed."); return
        cur = self.__head
        while cur:
            if cur.name.lower() == name.lower():
                if cur.next: cur.next.prev = cur.prev
                else: self.__tail = cur.prev
                if cur.prev: cur.prev.next = cur.next
                print("Expense removed."); return
            cur = cur.next
        print("Expense not found.")


# ---------- CIRCULAR LINKED LIST (login history) ----------
class HistoryNode:
    def __init__(self, event_type, date_text, time_text):
        self.event_type, self.date_text, self.time_text, self.next = event_type, date_text, time_text, None


class LoginHistory:
    def __init__(self):
        self.__head = self.__last = None        # ENCAPSULATION: private
        self.__total_events = 0

    def add_event(self, event_type, date_text, time_text):
        node = HistoryNode(event_type, date_text, time_text)
        if self.__head is None:
            self.__head = self.__last = node
            node.next = self.__head
        else:
            node.next, self.__last.next, self.__last = self.__head, node, node
        self.__total_events += 1

    def show_history(self):
        if self.__head is None: print("No login history yet."); return
        print("\n----- LOGIN AND REGISTER HISTORY -----")
        cur, count = self.__head, 0
        while count < self.__total_events:
            print("-", cur.event_type, ":", cur.date_text, cur.time_text)
            cur, count = cur.next, count + 1

    def to_list(self):
        result = []
        if self.__head is None: return result
        cur, count = self.__head, 0
        while count < self.__total_events:
            result.append({"event_type": cur.event_type, "date_text": cur.date_text, "time_text": cur.time_text})
            cur, count = cur.next, count + 1
        return result

    def load_from_list(self, event_list):
        self.__head = self.__last = None
        self.__total_events = 0
        for e in event_list: self.add_event(e["event_type"], e["date_text"], e["time_text"])


# ---------- SAVE / LOAD LOGIN HISTORY ----------
def save_login_history(username, login_history):
    with open("data/history_" + username + ".txt", "w") as f:
        for e in login_history.to_list():
            f.write(e["event_type"] + "|" + e["date_text"] + "|" + e["time_text"] + "\n")


def load_login_history(username):
    event_list = []
    try:
        with open("data/history_" + username + ".txt", "r") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) == 3:
                    event_list.append({"event_type": parts[0], "date_text": parts[1], "time_text": parts[2]})
    except FileNotFoundError:
        pass
    history = LoginHistory()
    history.load_from_list(event_list)
    return history


def record_event(username, login_history, event_type):
    now = datetime.datetime.now()
    login_history.add_event(event_type, now.strftime("%d/%m/%Y"), now.strftime("%I:%M %p"))
    save_login_history(username, login_history)


# ---------- SAVE / LOAD FINANCIAL PROFILE ----------
def save_profile(user):
    with open("data/profile_" + user.username + ".txt", "w") as f:
        f.write(str(user.income) + "\n" + str(user.savings) + "\n")
        for name, amount in user.fixed_expenses.to_list():
            f.write(name + "," + str(amount) + "\n")


def load_profile(user):
    try:
        with open("data/profile_" + user.username + ".txt", "r") as f:
            lines = f.readlines()
        if len(lines) >= 2:
            user.income, user.savings = float(lines[0].strip()), float(lines[1].strip())
            for line in lines[2:]:
                line = line.strip()
                if not line: continue
                parts = line.split(",")
                if len(parts) == 2: user.fixed_expenses.add_expense(parts[0], float(parts[1]))
    except (FileNotFoundError, ValueError, IndexError):
        pass


# ---------- FINANCE USER (INHERITANCE from Person) ----------
class FinanceUser(Person):
    def __init__(self, username, password_hash=""):
        super().__init__(username)                  # INHERITANCE: reuse Person's constructor
        self.__password_hash = password_hash        # ENCAPSULATION: never store plain text
        self.__income = 0
        self.__savings = 0
        self.fixed_expenses = FixedExpenseList()
        self.login_history = LoginHistory()

    # ---- AUTHENTICATION: hash on the way in, hash on the way in to compare, never store plain text ----
    def set_password(self, plain_password):
        self.__password_hash = _hash_password(plain_password)

    def check_password(self, plain_password):
        return self.__password_hash == _hash_password(plain_password)

    @property
    def password_hash(self):
        return self.__password_hash

    # ---- ENCAPSULATION: controlled access to income/savings via properties ----
    @property
    def income(self):
        return self.__income

    @income.setter
    def income(self, value):
        self.__income = value

    @property
    def savings(self):
        return self.__savings

    @savings.setter
    def savings(self, value):
        self.__savings = value

    def calculate_budget(self):
        return self.__income - self.fixed_expenses.get_total() - self.__savings

    # ---- POLYMORPHISM: overrides Person.get_role() ----
    def get_role(self):
        return "Registered User"


# ---------- STRONG PASSWORD CHECK ----------
def strong_password(password):
    if len(password) < 8: return False
    upper = lower = digit = special = False
    for ch in password:
        if ch.isupper(): upper = True
        elif ch.islower(): lower = True
        elif ch.isdigit(): digit = True
        else: special = True
    return upper and lower and digit and special


# ---------- SAVE / LOAD USERS ----------
def save_user_to_file(username, password_hash):
    with open("data/users.txt", "a") as f:
        f.write(username + "|" + password_hash + "\n")


def load_users_from_file():
    loaded = {}
    try:
        with open("data/users.txt", "r") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) == 2: loaded[parts[0]] = FinanceUser(parts[0], parts[1])
    except FileNotFoundError:
        pass
    return loaded


# ---------- REGISTER / LOGIN / FORGOT PASSWORD ----------
def register():
    print("\n----- REGISTER -----")
    username = input("Create username: ")
    if username in users:
        print("This username already exists. Please login instead.")
        return None
    password = input("Create password: ")
    if not strong_password(password):
        print("Password must contain:\n8 characters, Uppercase, Lowercase, Number, Special character")
        return None
    user = FinanceUser(username)
    user.set_password(password)                      # AUTHENTICATION: store a hash, not the password
    users[username] = user
    save_user_to_file(username, user.password_hash)
    record_event(username, user.login_history, "REGISTER")
    print("Registration Successful")
    return user


def login():
    print("\n----- LOGIN -----")
    username = input("Username: ")
    if username not in users:
        print("User not found")
        return None
    attempts = 3
    while attempts > 0:
        password = input("Password: ")
        if users[username].check_password(password):    # AUTHENTICATION: compare hashes
            print("Login Successful")
            users[username].login_history = load_login_history(username)
            load_profile(users[username])
            record_event(username, users[username].login_history, "LOGIN")
            return users[username]
        attempts -= 1
        print("Wrong Password")
        print("Attempts left:", attempts)
    print("Too many wrong attempts. Try later")
    return None


def forgot_password():
    print("\n----- FORGOT PASSWORD -----")
    username = input("Enter username: ")
    if username not in users:
        print("User not found")
        return
    new_password = input("Enter new password: ")
    if strong_password(new_password):
        users[username].set_password(new_password)       # AUTHENTICATION: re-hash the new password
        print("Password Changed Successfully")
    else:
        print("Weak Password\nPassword must contain:\n8 characters, Uppercase, Lowercase, Number, Special character")


# ---------- SAFE INPUT HELPERS ----------
def read_amount(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value < 0: print("Please enter a number that is zero or greater."); continue
            return value
        except ValueError:
            print("That is not a valid number. Please try again.")


def read_whole_number(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("That is not a valid number. Please try again.")


def read_expense_name(prompt):
    while True:
        text = input(prompt)
        if text.strip() == "": print("Expense name cannot be empty. Please try again."); continue
        if text.isdigit(): print("Expense name must be text, not just numbers. Please try again."); continue
        return text


# ---------- PROFILE SETUP / EDIT / DASHBOARD ----------
def setup_profile(user):
    print("\n----- FINANCIAL PROFILE SETUP -----")
    user.income = read_amount("Enter your monthly income: Rs.")
    print("Now add your fixed expenses one by one.\nType 'done' as the name when you are finished.")
    while True:
        name = read_expense_name("Fixed expense name (or 'done'): ")
        if name.lower() == "done": break
        user.fixed_expenses.add_expense(name, read_amount("Amount for " + name + ": Rs."))
    user.savings = read_amount("Enter your monthly savings target: Rs.")
    print("\nYour available spending budget is: Rs.", user.calculate_budget())
    save_profile(user)


def edit_profile(user):
    print("\n----- EDIT FINANCIAL PROFILE -----")
    print("1. Change monthly income\n2. Add fixed expense\n3. Remove fixed expense\n4. Change savings target\n0. Cancel")
    choice = input("\nEnter choice: ")
    if choice == "1":
        user.income = read_amount("Enter new monthly income: Rs.")
        save_profile(user); print("Income updated successfully!")
    elif choice == "2":
        name = read_expense_name("Enter expense name: ")
        user.fixed_expenses.add_expense(name, read_amount("Enter amount: Rs."))
        save_profile(user); print("Fixed expense added successfully!")
    elif choice == "3":
        print("\nCurrent fixed expenses:")
        user.fixed_expenses.show_all_expenses()
        user.fixed_expenses.remove_expense(read_expense_name("Enter expense name to remove: "))
        save_profile(user); print("Fixed expense removed successfully!")
    elif choice == "4":
        user.savings = read_amount("Enter new monthly savings target: Rs.")
        save_profile(user); print("Savings target updated successfully!")
    elif choice == "0":
        print("Edit cancelled.")
    else:
        print("Invalid choice.")


def show_dashboard(user, total_spent):
    budget = user.calculate_budget()
    remaining = budget - total_spent
    print("\n========== DASHBOARD ==========")
    print("Income           : Rs.", user.income)
    print("Fixed Expenses   : Rs.", user.fixed_expenses.get_total())
    print("Savings Target   : Rs.", user.savings)
    print("Available Budget : Rs.", budget)
    print("Spent So Far     : Rs.", total_spent)
    print("Remaining Budget : Rs.", remaining)
    if remaining < 0: status = "OVER BUDGET - touching savings"
    elif remaining <= budget * 0.20: status = "CAUTION - budget running low"
    elif remaining < budget * 0.50: status = "WARNING - moderate spending"
    else: status = "SAFE - good spending"
    print("Status           :", status)
    print("================================")
