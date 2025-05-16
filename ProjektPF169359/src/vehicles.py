"""
Moduł vehicles.py definiuje klasy pojazdów dostępnych w wypożyczalni.
"""
from enum import Enum
from typing import Optional, List, Dict
from datetime import date


class VehicleStatus(Enum):
    AVAILABLE = "available"
    RENTED = "rented"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"


class VehicleType(Enum):
    ECONOMY = "economy"
    COMPACT = "compact"
    STANDARD = "standard"
    PREMIUM = "premium"
    SUV = "suv"
    VAN = "van"


class Vehicle:
    def __init__(
            self,
            vehicle_id: str,
            make: str,
            model: str,
            year: int,
            registration_number: str,
            daily_rate: float,
            vehicle_type: VehicleType
    ) -> None:
        if not vehicle_id or not isinstance(vehicle_id, str):
            raise ValueError("ID pojazdu musi być niepustym stringiem")
        if not make or not isinstance(make, str):
            raise ValueError("Marka pojazdu musi być niepustym stringiem")
        if not model or not isinstance(model, str):
            raise ValueError("Model pojazdu musi być niepustym stringiem")
        if not isinstance(year, int) or year < 1900 or year > date.today().year + 1:
            raise ValueError(f"Rok produkcji musi być liczbą całkowitą między 1900 a {date.today().year + 1}")
        if not registration_number or not isinstance(registration_number, str):
            raise ValueError("Numer rejestracyjny musi być niepustym stringiem")
        if not isinstance(daily_rate, (int, float)) or daily_rate <= 0:
            raise ValueError("Dzienna stawka musi być liczbą dodatnią")
        if not isinstance(vehicle_type, VehicleType):
            raise ValueError("Typ pojazdu musi być instancją VehicleType")

        self.vehicle_id = vehicle_id
        self.make = make
        self.model = model
        self.year = year
        self.registration_number = registration_number
        self.daily_rate = daily_rate
        self.vehicle_type = vehicle_type
        self.status = VehicleStatus.AVAILABLE
        self.maintenance_history: List[Dict] = []

    def __str__(self) -> str:
        return f"{self.make} {self.model} ({self.year}) - {self.registration_number}"

    def change_status(self, new_status: VehicleStatus) -> None:
        if not isinstance(new_status, VehicleStatus):
            raise ValueError("Status musi być instancją VehicleStatus")
        self.status = new_status

    def is_available(self) -> bool:
        return self.status == VehicleStatus.AVAILABLE

    def add_maintenance_record(self, description: str, date_performed: date, cost: float) -> None:
        if not description or not isinstance(description, str):
            raise ValueError("Opis konserwacji musi być niepustym stringiem")
        if not isinstance(date_performed, date):
            raise ValueError("Data musi być instancją datetime.date")
        if not isinstance(cost, (int, float)) or cost < 0:
            raise ValueError("Koszt musi być liczbą nieujemną")

        record = {
            "description": description,
            "date": date_performed,
            "cost": cost
        }
        self.maintenance_history.append(record)


class Car(Vehicle):
    def __init__(
            self,
            vehicle_id: str,
            make: str,
            model: str,
            year: int,
            registration_number: str,
            daily_rate: float,
            vehicle_type: VehicleType,
            doors: int,
            fuel_type: str,
            transmission: str
    ) -> None:
        super().__init__(vehicle_id, make, model, year, registration_number, daily_rate, vehicle_type)

        if not isinstance(doors, int) or doors <= 0:
            raise ValueError("Liczba drzwi musi być dodatnią liczbą całkowitą")
        if not fuel_type or not isinstance(fuel_type, str):
            raise ValueError("Rodzaj paliwa musi być niepustym stringiem")
        if not transmission or not isinstance(transmission, str):
            raise ValueError("Typ skrzyni biegów musi być niepustym stringiem")

        self.doors = doors
        self.fuel_type = fuel_type
        self.transmission = transmission

    def __str__(self) -> str:
        base_str = super().__str__()
        return f"{base_str}, {self.doors} drzwi, {self.fuel_type}, {self.transmission}"


class VehicleInventory:
    def __init__(self) -> None:
        self.vehicles: Dict[str, Vehicle] = {}

    def add_vehicle(self, vehicle: Vehicle) -> None:
        if not isinstance(vehicle, Vehicle):
            raise TypeError("Obiekt musi być instancją klasy Vehicle")

        if vehicle.vehicle_id in self.vehicles:
            raise ValueError(f"Pojazd o ID {vehicle.vehicle_id} już istnieje w inwentarzu")
        self.vehicles[vehicle.vehicle_id] = vehicle

    def remove_vehicle(self, vehicle_id: str) -> None:
        if not vehicle_id or not isinstance(vehicle_id, str):
            raise ValueError("ID pojazdu musi być niepustym stringiem")

        if vehicle_id not in self.vehicles:
            raise ValueError(f"Pojazd o ID {vehicle_id} nie istnieje w inwentarzu")
        del self.vehicles[vehicle_id]

    def get_vehicle(self, vehicle_id: str) -> Optional[Vehicle]:
        if not vehicle_id or not isinstance(vehicle_id, str):
            raise ValueError("ID pojazdu musi być niepustym stringiem")

        return self.vehicles.get(vehicle_id)

    def get_available_vehicles(self) -> List[Vehicle]:
        return [v for v in self.vehicles.values() if v.is_available()]

    def get_available_vehicles_by_type(self, vehicle_type: VehicleType) -> List[Vehicle]:
        if not isinstance(vehicle_type, VehicleType):
            raise ValueError("Typ pojazdu musi być instancją VehicleType")

        return [v for v in self.vehicles.values()
                if v.is_available() and v.vehicle_type == vehicle_type]

    def count_vehicles_by_status(self) -> Dict[VehicleStatus, int]:
        counts = {status: 0 for status in VehicleStatus}
        for vehicle in self.vehicles.values():
            counts[vehicle.status] += 1
        return counts