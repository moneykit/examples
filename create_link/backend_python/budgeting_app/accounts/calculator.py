from dataclasses import dataclass
from decimal import Decimal

from .models import Transaction


@dataclass
class Category:
    id: str
    name: str
    total: Decimal


class BudgetCalculator:
    def __init__(self, transactions: list[Transaction]) -> None:
        self._transactions = transactions

    def spending_by_category(self, include_subcategories: bool) -> dict[str, Category]:
        result: dict[str, Category] = {}
        for txn in self._transactions:
            category = txn.category
            if not include_subcategories:
                category = category.partition(".")[0]
            if category in result:
                # TODO: Credit vs debit
                result[category].total += txn.ammount
            else:
                name = " ".join((value.title() for value in category.split(".")))
                result[category] = Category(id=category, name=name, total=txn.ammount)

        return result

    def top_categories(self, include_subcategories: bool) -> list[Category]:
        # Naive implementation
        breakdown = self.spending_by_category(include_subcategories)
        categories = breakdown.values()
        return sorted(categories, key=lambda category: category.total, reverse=True)[0:5]
