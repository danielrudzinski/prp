from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import date
import uuid
from src.reviews import Review
from src.vehicles import Vehicle, VehicleStatus
from src.customers import Customer, CustomerCategory


class RentalStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class RentalException(Exception):
    pass


class Rental:
    def __init__(
        self,
        rental_id: str,
        customer: Customer,
        vehicle: Vehicle,
        start_date: date,
        end_date: date,
        daily_rate: float,
    ) -> None:
        if not rental_id or not isinstance(rental_id, str):
            raise ValueError("ID wypożyczenia musi być niepustym stringiem")
        if not isinstance(customer, Customer):
            raise ValueError("Klient musi być instancją klasy Customer")
        if not isinstance(vehicle, Vehicle):
            raise ValueError("Pojazd musi być instancją klasy Vehicle")
        if not isinstance(start_date, date):
            raise ValueError(
                "Data rozpoczęcia musi być instancją datetime.date"
            )
        if not isinstance(end_date, date):
            raise ValueError(
                "Data zakończenia musi być instancją datetime.date"
            )
        if start_date > end_date:
            raise ValueError(
                "Data rozpoczęcia nie może być późniejsza niż data zakończenia"
            )
        if not isinstance(daily_rate, (int, float)) or daily_rate <= 0:
            raise ValueError("Dzienna stawka musi być dodatnią liczbą")

        self.rental_id = rental_id
        self.customer = customer
        self.vehicle = vehicle
        self.start_date = start_date
        self.end_date = end_date
        self.daily_rate = daily_rate
        self.reviews: list[Review] = []
        self.status = RentalStatus.ACTIVE
        self.actual_return_date: Optional[date] = None
        self.total_cost: Optional[float] = None
        self.additional_charges: Dict[str, float] = {}

    def calculate_duration(self) -> int:
        delta = self.end_date - self.start_date
        return delta.days + 1

    def calculate_base_cost(self) -> float:
        return self.calculate_duration() * self.daily_rate

    def is_overdue(self, current_date: Optional[date] = None) -> bool:
        if current_date is None:
            current_date = date.today()
        if not isinstance(current_date, date):
            raise ValueError(
                "Data sprawdzenia musi być instancją datetime.date"
            )

        if self.status != RentalStatus.ACTIVE:
            return False

        return current_date > self.end_date

    def add_charge(self, description: str, amount: float) -> None:
        if not description or not isinstance(description, str):
            raise ValueError("Opis opłaty musi być niepustym stringiem")
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Kwota opłaty musi być dodatnią liczbą")

        self.additional_charges[description] = amount

    def complete(self, return_date: date) -> float:
        if not isinstance(return_date, date):
            raise ValueError("Data zwrotu musi być instancją datetime.date")

        if self.status != RentalStatus.ACTIVE:
            raise RentalException(
                "Nie można zakończyć wypożyczenia, które nie jest aktywne"
            )

        self.actual_return_date = return_date
        self.status = RentalStatus.COMPLETED

        base_cost = self.calculate_base_cost()
        total_additional_charges = sum(self.additional_charges.values())

        if return_date > self.end_date:
            delay_days = (return_date - self.end_date).days
            late_fee = delay_days * self.daily_rate * 1.5
            self.add_charge("Opłata za opóźnienie", late_fee)
            total_additional_charges += late_fee

        self.total_cost = base_cost + total_additional_charges

        self.vehicle.change_status(VehicleStatus.AVAILABLE)

        return self.total_cost

    def cancel(self) -> None:
        if self.status in [RentalStatus.COMPLETED, RentalStatus.CANCELLED]:
            raise RentalException(
                "Nie można anulować wypożyczenia,"
                " które zostało już zakończone lub anulowane"
            )

        self.status = RentalStatus.CANCELLED
        self.vehicle.change_status(VehicleStatus.AVAILABLE)

    def __str__(self) -> str:
        return (
            f"Wypożyczenie {self.rental_id}: {self.customer.full_name()} - "
            f"{self.vehicle}, {self.start_date} do {self.end_date}, "
            f"status: {self.status.value}"
        )


class RentalManager:
    def __init__(self) -> None:
        self.rentals: Dict[str, Rental] = {}
        self.reviews: List[Review] = []

    def create_rental(
        self,
        customer: Customer,
        vehicle: Vehicle,
        start_date: date,
        end_date: date,
    ) -> Rental:
        if not isinstance(customer, Customer):
            raise ValueError("Klient musi być instancją klasy Customer")
        if not isinstance(vehicle, Vehicle):
            raise ValueError("Pojazd musi być instancją klasy Vehicle")
        if not isinstance(start_date, date):
            raise ValueError(
                "Data rozpoczęcia musi być instancją datetime.date"
            )
        if not isinstance(end_date, date):
            raise ValueError(
                "Data zakończenia musi być instancją datetime.date"
            )

        if not customer.can_rent():
            raise RentalException(
                "Klient nie może wypożyczyć pojazdu - nieważne prawo jazdy"
            )

        if customer.driving_license.expiry_date < end_date:
            raise RentalException(
                "Prawo jazdy klienta wygasa przed końcem okresu wypożyczenia"
            )

        if not vehicle.is_available():
            raise RentalException(
                f"Pojazd {vehicle.vehicle_id} nie jest dostępny"
            )

        if start_date > end_date:
            raise RentalException(
                "Data rozpoczęcia nie może być późniejsza niż data zakończenia"
            )

        if start_date < date.today():
            raise RentalException(
                "Data rozpoczęcia nie może być wcześniejsza niż dzisiejsza"
            )

        daily_rate = vehicle.daily_rate
        if customer.category == CustomerCategory.SILVER:
            daily_rate *= 0.95
        elif customer.category == CustomerCategory.GOLD:
            daily_rate *= 0.9
        elif customer.category == CustomerCategory.PLATINUM:
            daily_rate *= 0.85

        rental_id = str(uuid.uuid4())
        rental = Rental(
            rental_id, customer, vehicle, start_date, end_date, daily_rate
        )

        vehicle.change_status(VehicleStatus.RENTED)

        customer.add_rental_to_history(rental_id)

        self.rentals[rental_id] = rental

        return rental

    def get_rental(self, rental_id: str) -> Optional[Rental]:
        if not rental_id or not isinstance(rental_id, str):
            raise ValueError("ID wypożyczenia musi być niepustym stringiem")

        return self.rentals.get(rental_id)

    def complete_rental(self, rental_id: str, return_date: date) -> float:
        if not rental_id or not isinstance(rental_id, str):
            raise ValueError("ID wypożyczenia musi być niepustym stringiem")
        if not isinstance(return_date, date):
            raise ValueError("Data zwrotu musi być instancją datetime.date")

        rental = self.get_rental(rental_id)
        if not rental:
            raise RentalException(
                f"Wypożyczenie o ID {rental_id} nie istnieje"
            )

        if return_date < rental.start_date:
            raise ValueError(
                "Data zwrotu nie może być wcześniejsza "
                "niż data rozpoczęcia wypożyczenia"
            )

        return rental.complete(return_date)

    def cancel_rental(self, rental_id: str) -> None:
        if not rental_id or not isinstance(rental_id, str):
            raise ValueError("ID wypożyczenia musi być niepustym stringiem")

        rental = self.get_rental(rental_id)
        if not rental:
            raise RentalException(
                f"Wypożyczenie o ID {rental_id} nie istnieje"
            )

        rental.cancel()

    def get_active_rentals(self) -> List[Rental]:
        return [
            r
            for r in self.rentals.values()
            if r.status == RentalStatus.ACTIVE
        ]

    def get_overdue_rentals(
        self, current_date: Optional[date] = None
    ) -> List[Rental]:
        if current_date is None:
            current_date = date.today()
        return [
            r for r in self.rentals.values() if r.is_overdue(current_date)
        ]

    def get_customer_rentals(self, customer_id: str) -> List[Rental]:
        if not customer_id or not isinstance(customer_id, str):
            raise ValueError("ID klienta musi być niepustym stringiem")

        return [
            r
            for r in self.rentals.values()
            if r.customer.customer_id == customer_id
        ]

    def get_vehicle_rental_history(self, vehicle_id: str) -> List[Rental]:
        if not vehicle_id or not isinstance(vehicle_id, str):
            raise ValueError("ID pojazdu musi być niepustym stringiem")

        return [
            r
            for r in self.rentals.values()
            if r.vehicle.vehicle_id == vehicle_id
        ]

    def add_review(
        self, rental_id: str, rating: int, comment: str, review_date: date
    ) -> Review:
        rental = self.get_rental(rental_id)
        if not rental:
            raise RentalException(
                f"Wypożyczenie o ID {rental_id} nie istnieje"
            )

        if rental.status != RentalStatus.COMPLETED:
            raise RentalException(
                "Nie można dodać opinii do wypożyczenia,"
                "które nie zostało zakończone"
            )

        review = Review(
            rental_id=rental_id,
            customer_id=rental.customer.customer_id,
            rating=rating,
            comment=comment,
            review_date=review_date,
        )

        self.reviews.append(review)
        return review

    def get_reviews_for_customer(self, customer_id: str) -> list[Review]:
        return [r for r in self.reviews if r.customer_id == customer_id]

    def get_average_rating_for_customer(self, customer_id: str) -> float:
        reviews = self.get_reviews_for_customer(customer_id)
        return (
            sum(r.rating for r in reviews) / len(reviews) if reviews else 0.0
        )

    def generate_rental_report(
        self, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        if not isinstance(start_date, date):
            raise ValueError(
                "Data początkowa musi być instancją datetime.date"
            )
        if not isinstance(end_date, date):
            raise ValueError("Data końcowa musi być instancją datetime.date")
        if start_date > end_date:
            raise ValueError(
                "Data początkowa nie może być późniejsza niż data końcowa"
            )

        relevant_rentals = [
            r
            for r in self.rentals.values()
            if (
                r.start_date <= end_date
                and (
                    r.actual_return_date is None
                    or r.actual_return_date >= start_date
                )
            )
        ]

        total_revenue = sum(
            r.total_cost or 0
            for r in relevant_rentals
            if r.status == RentalStatus.COMPLETED
        )
        total_rentals = len(relevant_rentals)
        avg_duration = (
            sum(r.calculate_duration() for r in relevant_rentals)
            / total_rentals
            if total_rentals > 0
            else 0
        )

        completed_rentals = [
            r for r in relevant_rentals if r.status == RentalStatus.COMPLETED
        ]
        overdue_rentals = [
            r
            for r in relevant_rentals
            if r.status == RentalStatus.OVERDUE
            or (
                r.status == RentalStatus.COMPLETED
                and r.actual_return_date
                and r.actual_return_date > r.end_date
            )
        ]

        report = {
            "period_start": start_date,
            "period_end": end_date,
            "total_rentals": total_rentals,
            "completed_rentals": len(completed_rentals),
            "active_rentals": len(
                [
                    r
                    for r in relevant_rentals
                    if r.status == RentalStatus.ACTIVE
                ]
            ),
            "cancelled_rentals": len(
                [
                    r
                    for r in relevant_rentals
                    if r.status == RentalStatus.CANCELLED
                ]
            ),
            "overdue_rentals": len(overdue_rentals),
            "total_revenue": total_revenue,
            "average_rental_duration": avg_duration,
        }

        return report
