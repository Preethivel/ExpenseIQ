# main.py — entry point, connects all four modules via a menu
import user_module, transaction_module, alert_module, report_module


def read_category(prompt):
    while True:
        text = input(prompt)
        if text.strip() == "": print("Category cannot be empty. Please try again."); continue
        if text.isdigit(): print("Category must be text, not just numbers. Please try again."); continue
        return text


def show_main_menu():
    print("\n========== MAIN MENU ==========")
    for line in ["1. View Dashboard", "2. Add Expense", "3. Delete Expense", "4. View All Expenses",
                 "5. Search by Category", "6. Undo a Transaction (by ID)", "7. View Alerts",
                 "8. View Login History", "9. Edit Financial Profile", "10. View Analytics",
                 "11. Financial Health Score", "12. Generate Report", "0. Logout"]:
        print(line)


def run_app(user):
    tm = transaction_module.TransactionManager()
    monitoring = alert_module.MonitoringSystem()
    report = report_module.ReportGenerator(user, tm)

    while True:
        show_main_menu()
        choice = input("\nEnter your choice: ")

        if choice == "1":
            user_module.show_dashboard(user, tm.get_total_spent())

        elif choice == "2":
            category = read_category("Enter category: ")
            amount = user_module.read_amount("Enter amount: Rs.")
            budget, total_spent = user.calculate_budget(), tm.get_total_spent()

            if alert_module.check_before_adding(amount, total_spent, budget, user.savings):
                tm.add_expense(category, amount)
                new_total = tm.get_total_spent()
                monitoring.check_budget(new_total, budget, user.savings)
                monitoring.show_alerts()
                print("\n--- Remaining Budget Available: Rs.", budget - new_total, "---")
                score, status = report.calculate_health_score()
                print("Your Financial Health Score is now:", score, "/ 100 (", status, ")")
            else:
                print("Expense was not added.")

        elif choice == "3":
            tm.transactions.show_all()
            tm.delete_expense(user_module.read_whole_number("Enter ID to delete: "))

        elif choice == "4":
            tm.transactions.show_all()

        elif choice == "5":
            results = tm.search_by_category(input("Enter category to search: "))
            if not results:
                print("No transactions found in this category.")
            else:
                for t in results: print(t.trans_id, t.category, "Rs.", t.amount)

        elif choice == "6":
            tm.transactions.show_all()
            tm.undo_transaction(user_module.read_whole_number("Enter the ID of the transaction to undo: "))

        elif choice == "7":
            monitoring.show_alerts()

        elif choice == "8":
            user.login_history.show_history()

        elif choice == "9":
            user_module.edit_profile(user)

        elif choice == "10":
            report.show_analytics()

        elif choice == "11":
            score, status = report.calculate_health_score()
            print("\nFinancial Health Score:", score, "/ 100 (", status, ")")

        elif choice == "12":
            report.generate_report()

        elif choice == "0":
            print("Logging out... Goodbye,", user.username)
            break

        else:
            print("Invalid choice. Please try again.")


def start():
    print("====================================\n              EXPENSEIQ")
    print("  Personal Finance Management System\n====================================")
    user_module.users.update(user_module.load_users_from_file())

    while True:
        print("\n1. Register\n2. Login\n3. Forgot Password\n4. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            user = user_module.register()
            if user is not None:
                user_module.setup_profile(user)   # only right after registration
                run_app(user)
        elif choice == "2":
            user = user_module.login()
            if user is not None: run_app(user)
        elif choice == "3":
            user_module.forgot_password()
        elif choice == "4":
            print("Goodbye!"); break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    try:
        start()
    except KeyboardInterrupt:
        print("\n\nProgram closed. Goodbye!")
