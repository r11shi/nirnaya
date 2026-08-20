"""Tests for Nirnaya finance engine."""

import pytest
from app.services.finance_engine import categorize_transaction, _months_to_goal


class TestCategorization:
    """Test transaction categorization."""

    def test_food_swiggy(self):
        assert categorize_transaction("Swiggy order #12345") == "food"

    def test_food_restaurant(self):
        assert categorize_transaction("Restaurant bill", "Pizza Hut") == "food"

    def test_transport_uber(self):
        assert categorize_transaction("Uber trip") == "transport"

    def test_shopping_amazon(self):
        assert categorize_transaction("Amazon purchase") == "shopping"

    def test_utilities_electricity(self):
        assert categorize_transaction("Electricity bill payment") == "utilities"

    def test_rent(self):
        assert categorize_transaction("Monthly rent payment") == "rent"

    def test_salary(self):
        assert categorize_transaction("Salary credit") == "salary"

    def test_emi(self):
        assert categorize_transaction("EMI payment") == "emi"

    def test_unknown_category(self):
        assert categorize_transaction("Random unknown thing xyz") == "other"

    def test_payee_context(self):
        assert categorize_transaction("Monthly payment", "Netflix") == "entertainment"


class TestGoalCalculations:
    """Test deterministic financial calculations."""

    def test_months_to_goal_basic(self):
        # Need 10000 more, saving 5000/month = 2 months
        assert _months_to_goal(10000, 5000) == 2

    def test_months_to_goal_fractional(self):
        # Need 10000, saving 3000/month = ceil(3.33) = 4 months
        assert _months_to_goal(10000, 3000) == 4

    def test_months_to_goal_zero_savings(self):
        assert _months_to_goal(10000, 0) is None

    def test_months_to_goal_negative_savings(self):
        assert _months_to_goal(10000, -500) is None

    def test_months_to_goal_exact(self):
        assert _months_to_goal(10000, 10000) == 1

    def test_months_to_goal_small_remaining(self):
        assert _months_to_goal(100, 5000) == 1
