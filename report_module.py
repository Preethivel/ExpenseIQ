# report_module.py — LAYER 4: Analytics & Report Generation (bubble sort)


class ReportGenerator:
    def __init__(self, user, transaction_manager):
        self.user, self.transaction_manager = user, transaction_manager

    def get_top_category(self):
        totals = self.transaction_manager.get_category_totals()
        if not totals: return None, 0
        top_category = max(totals, key=totals.get)
        return top_category, totals[top_category]

    def calculate_health_score(self):
        budget = self.user.calculate_budget()
        total_spent = self.transaction_manager.get_total_spent()
        remaining = budget - total_spent
        score = 0

        # part 1: budget remaining (40 pts)
        if budget > 0:
            pct = remaining / budget
            if pct <= 0: score += 0
            elif pct <= 0.20: score += 5
            elif pct <= 0.40: score += 15
            elif pct <= 0.60: score += 25
            else: score += 40

        # part 2: budget discipline (30 pts)
        if budget > 0:
            if total_spent <= budget:
                score += 30
            else:
                over_percent = min(1, (total_spent - budget) / budget)
                score += 30 - (over_percent * 30)

        # part 3: fixed expense ratio (30 pts)
        if self.user.income > 0:
            fixed_ratio = min(1, self.user.fixed_expenses.get_total() / self.user.income)
            score += 30 - (fixed_ratio * 30)

        score = round(score, 1)
        if score >= 85: status = "Excellent"
        elif score >= 70: status = "Good"
        elif score >= 50: status = "Fair"
        else: status = "Needs Improvement"
        return score, status

    def show_analytics(self):
        total_spent = self.transaction_manager.get_total_spent()
        budget = self.user.calculate_budget()
        top_category, top_amount = self.get_top_category()

        print("\n----- ANALYTICS -----")
        print("Total Spent      : Rs.", total_spent)
        print("Remaining Budget : Rs.", budget - total_spent)
        if top_category is not None:
            print("Top Category     :", top_category, "(Rs.", top_amount, ")")

        print("\nCategory Breakdown:")
        for category, amount in self.transaction_manager.get_category_totals().items():
            print(" -", category, ": Rs.", amount)

    def generate_report(self):
        all_transactions, cur = [], self.transaction_manager.transactions.head
        while cur: all_transactions.append(cur); cur = cur.next

        # bubble sort by amount, smallest to largest
        n = len(all_transactions)
        for i in range(n):
            for j in range(n - i - 1):
                if all_transactions[j].amount > all_transactions[j + 1].amount:
                    all_transactions[j], all_transactions[j + 1] = all_transactions[j + 1], all_transactions[j]

        score, status = self.calculate_health_score()
        top_category, top_amount = self.get_top_category()

        with open("data/report_" + self.user.username + ".txt", "w") as f:
            f.write("========================================\n")
            f.write("        EXPENSELQ FINAL REPORT\n")
            f.write("========================================\n\n")
            f.write("Username        : " + self.user.username + "\n")
            f.write("Income          : Rs. " + str(self.user.income) + "\n")
            f.write("Fixed Expenses  : Rs. " + str(self.user.fixed_expenses.get_total()) + "\n")
            f.write("Savings Target  : Rs. " + str(self.user.savings) + "\n")
            f.write("Available Budget: Rs. " + str(self.user.calculate_budget()) + "\n\n")

            f.write("---- Transactions (sorted by amount) ----\n")
            for t in all_transactions:
                f.write(t.category + " - Rs." + str(t.amount) + "\n")

            f.write("\n---- Top Category ----\n")
            if top_category is not None:
                f.write(str(top_category) + " - Rs." + str(top_amount) + "\n")

            f.write("\n---- Health Score ----\n")
            f.write(str(score) + " / 100 (" + status + ")\n")

        print("\nReport generated successfully!")
        print("Saved as: data/report_" + self.user.username + ".txt")
