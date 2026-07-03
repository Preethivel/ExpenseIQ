# base_structures.py
# Shared ABSTRACT BASE CLASS for our custom containers.
#
# ABSTRACTION  : Container defines *what* every container must do (add / remove / is_empty)
#                without saying *how*. It can never be created on its own.
# INHERITANCE  : AlertQueue (alert_module.py) and UndoStack (transaction_module.py) both
#                inherit from Container.
# POLYMORPHISM : Both subclasses expose the exact same method names, but each one behaves
#                completely differently underneath -- Queue = FIFO, Stack = LIFO. Code that
#                only knows about "a Container" can call .add()/.remove() on either one and
#                get the correct behaviour automatically.

from abc import ABC, abstractmethod


class Container(ABC):
    """Abstract base class -- cannot be instantiated directly."""

    @abstractmethod
    def add(self, item):
        """Add one item to the container."""
        raise NotImplementedError

    @abstractmethod
    def remove(self):
        """Remove and return one item from the container (None if empty)."""
        raise NotImplementedError

    @abstractmethod
    def is_empty(self):
        """True if the container currently holds nothing."""
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError
