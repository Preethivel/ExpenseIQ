# alert_module.py — LAYER 3: Budget Monitoring & Alerts (QUEUE)
#
# AlertQueue INHERITS from Container (base_structures.py) and implements it as a FIFO
# queue using collections.deque -- an OPTIMISATION over a plain list, since
# deque.popleft() is O(1) while list.pop(0) is O(n) (it has to shift every remaining item).

from collections import deque
from base_structures import Container


class AlertQueue(Container):
    def __init__(self):
        self.__queue = deque()          # ENCAPSULATION: private, name-mangled attribute

    # ---- Container interface (POLYMORPHISM: same names as UndoStack, different behaviour) ----
    def add(self, message):
        self.__queue.append(message)                       # add to the back

    def remove(self):
        return self.__queue.popleft() if self.__queue else None   # remove from the front -> FIFO

    def is_empty(self):
        return len(self.__queue) == 0

    def __len__(self):
        return len(self.__queue)

    # ---- familiar aliases so the rest of the codebase reads the same as before ----
    def enqueue(self, message):
        self.add(message)

    def dequeue(self):
        return self.remove()

    def total_pending(self):
        return len(self)


class MonitoringSystem:
    def __init__(self):
        self.__alert_queue = AlertQueue()                   # ENCAPSULATION: private state
        self.__alerted_70 = self.__alerted_85 = self.__alerted_100 = False

    def check_budget(self, total_spent, budget, savings_target):
        if budget <= 0:
            print("Warning: your fixed expenses and savings already use up your full income.")
            return
        percent_used = (total_spent / budget) * 100

        if percent_used >= 70 and not self.__alerted_70:
            self.__alert_queue.enqueue("Reminder: you have used 70% of your budget.")
            self.__alerted_70 = True
        if percent_used >= 85 and not self.__alerted_85:
            self.__alert_queue.enqueue("Warning: you have used 85% of your budget. Your savings may be at risk.")
            self.__alerted_85 = True
        if percent_used >= 100 and not self.__alerted_100:
            expected_savings = max(0, savings_target - (total_spent - budget))
            self.__alert_queue.enqueue("Critical: you have crossed your budget! Expected savings now: Rs." + str(expected_savings))
            self.__alerted_100 = True

    def show_alerts(self):
        if self.__alert_queue.is_empty(): print("\nNo new alerts."); return
        print("\n----- NEW ALERTS -----")
        while not self.__alert_queue.is_empty():
            print(">>", self.__alert_queue.dequeue())


def check_before_adding(amount_to_spend, total_spent, budget, savings_target):
    # Returns True if the expense should go ahead, False if the user cancels after a warning.
    new_remaining = budget - (total_spent + amount_to_spend)

    if new_remaining < 0:
        shortfall = abs(new_remaining)
        expected_savings = max(0, savings_target - shortfall)
        print("\n----- WARNING -----")
        print("This expense will go OVER your budget by Rs.", shortfall)
        print("Your savings target of Rs.", savings_target, "will be affected.")
        print("Expected savings would drop to: Rs.", expected_savings)
        return input("Do you still want to add this expense? (yes/no): ").lower() == "yes"

    elif budget > 0 and new_remaining < (budget * 0.20):
        print("\n----- NEARING SAVINGS LIMIT -----")
        print("After this expense, only Rs.", new_remaining, "of your budget will remain.")
        print("You are getting close to your savings limit.")
        print("If you reduce this expense or skip it, your savings stays safer.")
        return input("Do you still want to add this expense? (yes/no): ").lower() == "yes"

    print("\nThis expense is within your safe spending budget.")
    return True
