from decimal import Decimal
from typing import Annotated

import pydantic
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from budgeting_app import accounts
from budgeting_app.database.connection import get_db_session
from budgeting_app.users import User, UserSessionManager

router = APIRouter(prefix="/budget")


class Category(pydantic.BaseModel):
    id: str
    name: str
    total: Decimal


class SpendingByCategoryResponse(pydantic.BaseModel):
    spending_by_category: dict[str, Category]


class TopCategoriesResponse(pydantic.BaseModel):
    top_categories: list[Category]


@router.get("/accounts/all/category-breakdown", response_model=SpendingByCategoryResponse)
async def get_spending_by_category(
    current_user: Annotated[User, Depends(UserSessionManager.current_user)],
    db_session: Annotated[Session, Depends(get_db_session)],
    include_subcategories: Annotated[bool, Query()] = False,
) -> SpendingByCategoryResponse:
    repo = accounts.AccountsRepository(db_session)
    transactions = []
    # Naive implementation
    # TODO: Replace wih less loops
    for link_id, link_accounts in repo.get_all_accounts(current_user.id).items():
        for account in link_accounts:
            transactions += repo.get_transactions_for_account(current_user.id, account_id=account.id)

    calculator = accounts.BudgetCalculator(transactions)
    spending_breakdown = calculator.spending_by_category(include_subcategories)

    return SpendingByCategoryResponse(
        spending_by_category={
            category_id: Category(id=category_id, name=category.name, total=category.total)
            for category_id, category in spending_breakdown.items()
        }
    )


@router.get("/accounts/{account_id}/category-breakdown", response_model=SpendingByCategoryResponse)
async def get_spending_by_category_for_account(
    account_id: int,
    current_user: Annotated[User, Depends(UserSessionManager.current_user)],
    db_session: Annotated[Session, Depends(get_db_session)],
    include_subcategories: Annotated[bool, Query()] = False,
) -> SpendingByCategoryResponse:
    accounts_repo = accounts.AccountsRepository(db_session)
    account = accounts_repo.get_account(current_user.id, account_id=account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error_message": "Account not found"})

    transactions = accounts_repo.get_transactions_for_account(current_user.id, account.id)

    calculator = accounts.BudgetCalculator(transactions)
    spending_breakdown = calculator.spending_by_category(include_subcategories)

    return SpendingByCategoryResponse(
        spending_by_category={
            category_id: Category(id=category_id, name=category.name, total=category.total)
            for category_id, category in spending_breakdown.items()
        }
    )


@router.get("/accounts/all/top-categories", response_model=TopCategoriesResponse)
async def get_top_categories(
    current_user: Annotated[User, Depends(UserSessionManager.current_user)],
    db_session: Annotated[Session, Depends(get_db_session)],
    include_subcategories: Annotated[bool, Query()] = False,
) -> TopCategoriesResponse:
    repo = accounts.AccountsRepository(db_session)
    transactions = []
    # Naive implementation
    # TODO: Replace wih less loops
    for link_id, link_accounts in repo.get_all_accounts(current_user.id).items():
        for account in link_accounts:
            transactions += repo.get_transactions_for_account(current_user.id, account.id)

    calculator = accounts.BudgetCalculator(transactions)
    top_categories = calculator.top_categories(include_subcategories)

    return TopCategoriesResponse(
        top_categories=[
            Category(id=category.id, name=category.name, total=category.total) for category in top_categories
        ]
    )


@router.get("/accounts/{account_id}/top-categories", response_model=TopCategoriesResponse)
async def get_top_categories_for_account(
    account_id: int,
    current_user: Annotated[User, Depends(UserSessionManager.current_user)],
    db_session: Annotated[Session, Depends(get_db_session)],
    include_subcategories: Annotated[bool, Query()] = False,
) -> TopCategoriesResponse:
    accounts_repo = accounts.AccountsRepository(db_session)
    account = accounts_repo.get_account(current_user.id, account_id=account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error_message": "Account not found"})

    transactions = accounts_repo.get_transactions_for_account(current_user.id, account.id)

    calculator = accounts.BudgetCalculator(transactions)
    top_categories = calculator.top_categories(include_subcategories)

    return TopCategoriesResponse(
        top_categories=[
            Category(id=category.id, name=category.name, total=category.total) for category in top_categories
        ]
    )
