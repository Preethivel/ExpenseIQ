# transaction_module.py — LAYER 2: Singly linked list (transactions) + per-ID undo stacks
#
# UndoStack INHERITS from Container (base_structures.py), same as AlertQueue in
# alert_module.py -- POLYMORPHISM: identical method names (add/remove/is_empty),
# opposite behaviour (LIFO instead of FIFO).

from collections import defaultdict
from base_structures import Container


class TransactionNode:
    def __init__(self, trans_id, category, amount):
        self.trans_id, self.category, self.amount, self.next = trans_id, category, amount, None


class TransactionList:
    def __init__(self):
        self.__head = None              # ENCAPSULATION: private, exposed read-only below
        self.__counter = 1

    @property
    def head(self):
        return self.__head

    def add_transaction(self, category, amount):
        node = TransactionNode(self.__counter, category, amount)
        self.__counter += 1
        if self.__head is None:
            self.__head = node
        else:
            cur = self.__head
            while cur.next: cur = cur.next
            cur.next = node
        return node

    def delete_transaction(self, trans_id):
        prev, cur = None, self.__head
        while cur:
            if cur.trans_id == trans_id:
                if prev is None: self.__head = cur.next
                else: prev.next = cur.next
                return cur
            prev, cur = cur, cur.next
        return None

    def find_transaction(self, trans_id):
        cur = self.__head
        while cur:
            if cur.trans_id == trans_id: return cur
            cur = cur.next
        return None

    def show_all(self):
        if self.__head is None: print("No transactions yet."); return
        print("\nID   Category        Amount")
        print("-----------------------------")
        cur = self.__head
        while cur:
            print(cur.trans_id, " ", cur.category, "   Rs.", cur.amount)
            cur = cur.next

    def get_total_spent(self):
        total, cur = 0, self.__head
        while cur: total, cur = total + cur.amount, cur.next
        return total

    def get_category_totals(self):
        # collections.defaultdict: no need to check "if category in totals" ourselves
        totals, cur = defaultdict(int), self.__head
        while cur:
            totals[cur.category] += cur.amount
            cur = cur.next
        return dict(totals)


class UndoStack(Container):
    def __init__(self):
        self.__stack = []               # ENCAPSULATION: private attribute

    # ---- Container interface (POLYMORPHISM: LIFO version of the same interface AlertQueue uses) ----
    def add(self, action):
        self.__stack.append(action)                        # push

    def remove(self):
        return self.__stack.pop() if self.__stack else None   # pop -> LIFO: last in, first out

    def is_empty(self):
        return len(self.__stack) == 0

    def __len__(self):
        return len(self.__stack)

    # ---- familiar aliases so the rest of the codebase reads the same as before ----
    def push(self, action):
        self.add(action)

    def pop(self):
        return self.remove()


class TransactionManager:
    def __init__(self):
        self.transactions = TransactionList()
        self.__undo_stacks = {}     # ENCAPSULATION: one stack per trans_id, private to the manager

    def add_expense(self, category, amount):
        node = self.transactions.add_transaction(category, amount)
        stack = UndoStack()
        stack.push({"type": "ADD"})
        self.__undo_stacks[node.trans_id] = stack
        print("Expense added successfully! (ID:", node.trans_id, ")")

    def delete_expense(self, trans_id):
        node = self.transactions.delete_transaction(trans_id)
        if node is None: print("Transaction not found."); return
        self.__undo_stacks.pop(trans_id, None)
        print("Expense deleted successfully!")

    def undo_transaction(self, trans_id):
        if trans_id not in self.__undo_stacks: print("No undo history found for that ID."); return
        action = self.__undo_stacks[trans_id].pop()
        if action is None: print("Nothing left to undo for that ID."); return
        if action["type"] == "ADD":
            self.transactions.delete_transaction(trans_id)
            del self.__undo_stacks[trans_id]
            print("Undo successful: transaction", trans_id, "was removed.")

    def search_by_category(self, category):
        term, results, cur = category.strip().lower(), [], self.transactions.head
        while cur:
            if cur.category.strip().lower() == term: results.append(cur)
            cur = cur.next
        return results

    def get_total_spent(self):
        return self.transactions.get_total_spent()

    def get_category_totals(self):
        return self.transactions.get_category_totals()
