"""
Moduł customers.py zarządza klientami wypożyczalni.
"""
from enum import Enum
from typing import Optional, Dict, List
from datetime import datetime, date


class CustomerCategory(Enum):
    STANDARD = "standard"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class DrivingLicense:
    def __init__(
            self,
            license_number: str,
            issue_date: date,
            expiry_date: date,
            categories: List[str]
    ) -> None:
        if not license_number or not isinstance(license_number, str):
            raise ValueError("Numer prawa jazdy musi być niepustym stringiem")
        if not isinstance(issue_date, date):
            raise ValueError("Data wydania musi być instancją datetime.date")
        if not isinstance(expiry_date, date):
            raise ValueError("Data ważności musi być instancją datetime.date")
        if issue_date > expiry_date:
            raise ValueError("Data wydania nie może być późniejsza niż data ważności")
        if not isinstance(categories, list) or not all(isinstance(c, str) for c in categories):
            raise ValueError("Kategorie muszą być listą stringów")

        self.license_number = license_number
        self.issue_date = issue_date
        self.expiry_date = expiry_date
        self.categories = categories

    def is_valid(self, check_date: Optional[date] = None) -> bool:
        if check_date is None:
            check_date = date.today()
        if not isinstance(check_date, date):
            raise ValueError("Data sprawdzenia musi być instancją datetime.date")

        return check_date <= self.expiry_date

    def has_category(self, category: str) -> bool:
        if not category or not isinstance(category, str):
            raise ValueError("Kategoria musi być niepustym stringiem")

        return category in self.categories


class Customer:
    def __init__(
            self,
            customer_id: str,
            first_name: str,
            last_name: str,
            email: str,
            phone: str,
            address: str,
            driving_license: DrivingLicense
    ) -> None:
        if not customer_id or not isinstance(customer_id, str):
            raise ValueError("ID klienta musi być niepustym stringiem")
        if not first_name or not isinstance(first_name, str):
            raise ValueError("Imię musi być niepustym stringiem")
        if not last_name or not isinstance(last_name, str):
            raise ValueError("Nazwisko musi być niepustym stringiem")
        if not email or not isinstance(email, str):
            raise ValueError("Email musi być niepustym stringiem")
        if not phone or not isinstance(phone, str):
            raise ValueError("Telefon musi być niepustym stringiem")
        if not address or not isinstance(address, str):
            raise ValueError("Adres musi być niepustym stringiem")
        if not isinstance(driving_license, DrivingLicense):
            raise ValueError("Prawo jazdy musi być instancją DrivingLicense")

        self.customer_id = customer_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.address = address
        self.driving_license = driving_license
        self.registration_date = datetime.now().date()
        self.category = CustomerCategory.STANDARD
        self.rental_history: List[str] = []

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} (ID: {self.customer_id})"

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def can_rent(self) -> bool:
        return self.driving_license.is_valid()

    def upgrade_category(self, new_category: CustomerCategory) -> None:
        if not isinstance(new_category, CustomerCategory):
            raise ValueError("Kategoria musi być instancją CustomerCategory")

        self.category = new_category

    def add_rental_to_history(self, rental_id: str) -> None:
        if not rental_id or not isinstance(rental_id, str):
            raise ValueError("ID wypożyczenia musi być niepustym stringiem")

        self.rental_history.append(rental_id)


class CustomerRegistry:
    def __init__(self) -> None:
        self.customers: Dict[str, Customer] = {}

    def register_customer(self, customer: Customer) -> None:
        if not isinstance(customer, Customer):
            raise TypeError("Obiekt musi być instancją klasy Customer")

        if customer.customer_id in self.customers:
            raise ValueError(f"Klient o ID {customer.customer_id} już istnieje w rejestrze")
        self.customers[customer.customer_id] = customer

    def remove_customer(self, customer_id: str) -> None:
        if not customer_id or not isinstance(customer_id, str):
            raise ValueError("ID klienta musi być niepustym stringiem")

        if customer_id not in self.customers:
            raise ValueError(f"Klient o ID {customer_id} nie istnieje w rejestrze")
        del self.customers[customer_id]

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        if not customer_id or not isinstance(customer_id, str):
            raise ValueError("ID klienta musi być niepustym stringiem")

        return self.customers.get(customer_id)

    def find_customers_by_last_name(self, last_name: str) -> List[Customer]:
        if not last_name or not isinstance(last_name, str):
            raise ValueError("Nazwisko musi być niepustym stringiem")

        return [c for c in self.customers.values() if c.last_name.lower() == last_name.lower()]

    def get_customers_by_category(self, category: CustomerCategory) -> List[Customer]:
        if not isinstance(category, CustomerCategory):
            raise ValueError("Kategoria musi być instancją CustomerCategory")

        return [c for c in self.customers.values() if c.category == category]

    def count_customers(self) -> int:
        return len(self.customers)
