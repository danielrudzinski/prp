from datetime import date, timedelta


from vehicles import Car, VehicleInventory, VehicleType
from customers import (
    Customer,
    CustomerRegistry,
    DrivingLicense,
    CustomerCategory,
)
from rental import RentalManager


def main():
    print("System Wypożyczalni Pojazdów - Demonstracja")
    print("=" * 50)

    # Inicjalizacja rejestrów
    vehicle_inventory = VehicleInventory()
    customer_registry = CustomerRegistry()
    rental_manager = RentalManager()

    # Dodawanie przykładowych pojazdów
    print("\n[ Dodawanie pojazdów do inwentarza ]")
    vehicle1 = Car(
        vehicle_id="CAR001",
        make="Toyota",
        model="Corolla",
        year=2020,
        registration_number="WA12345",
        daily_rate=150.0,
        vehicle_type=VehicleType.COMPACT,
        doors=5,
        fuel_type="Benzyna",
        transmission="Manualna",
    )
    vehicle_inventory.add_vehicle(vehicle1)
    print(f"Dodano pojazd: {vehicle1}")

    vehicle2 = Car(
        vehicle_id="CAR002",
        make="Ford",
        model="Focus",
        year=2021,
        registration_number="WA54321",
        daily_rate=170.0,
        vehicle_type=VehicleType.STANDARD,
        doors=5,
        fuel_type="Diesel",
        transmission="Automatyczna",
    )
    vehicle_inventory.add_vehicle(vehicle2)
    print(f"Dodano pojazd: {vehicle2}")

    vehicle3 = Car(
        vehicle_id="CAR003",
        make="BMW",
        model="X5",
        year=2022,
        registration_number="WA99999",
        daily_rate=350.0,
        vehicle_type=VehicleType.PREMIUM,
        doors=5,
        fuel_type="Benzyna",
        transmission="Automatyczna",
    )
    vehicle_inventory.add_vehicle(vehicle3)
    print(f"Dodano pojazd: {vehicle3}")

    # Dodawanie przykładowych klientów
    print("\n[ Rejestracja klientów ]")
    license1 = DrivingLicense(
        license_number="ABC123456",
        issue_date=date(2015, 5, 15),
        expiry_date=date(2025, 5, 15),
        categories=["B"],
    )
    customer1 = Customer(
        customer_id="CUST001",
        first_name="Jan",
        last_name="Kowalski",
        email="jan.kowalski@example.com",
        phone="123456789",
        address="ul. Przykładowa 1, Warszawa",
        driving_license=license1,
    )
    customer_registry.register_customer(customer1)
    print(f"Zarejestrowano klienta: {customer1}")

    license2 = DrivingLicense(
        license_number="DEF789012",
        issue_date=date(2018, 6, 20),
        expiry_date=date(2028, 6, 20),
        categories=["B", "C"],
    )
    customer2 = Customer(
        customer_id="CUST002",
        first_name="Anna",
        last_name="Nowak",
        email="anna.nowak@example.com",
        phone="987654321",
        address="ul. Kwiatowa 2, Kraków",
        driving_license=license2,
    )
    customer_registry.register_customer(customer2)
    print(f"Zarejestrowano klienta: {customer2}")

    # Podnieśmy kategorię jednego klienta
    customer2.upgrade_category(CustomerCategory.GOLD)
    print(
        f"Zaktualizowano kategorię klienta {customer2}"
        f" na {customer2.category.value}"
    )

    # Tworzenie wypożyczeń
    print("\n[ Tworzenie wypożyczeń ]")
    today = date.today()

    # Wypożyczenie 1
    try:
        rental1 = rental_manager.create_rental(
            customer=customer1,
            vehicle=vehicle1,
            start_date=today,
            end_date=today + timedelta(days=3),
        )
        print(f"Utworzono wypożyczenie: {rental1}")
    except Exception as e:
        print(f"Błąd podczas tworzenia wypożyczenia: {e}")

    # Wypożyczenie 2
    try:
        rental2 = rental_manager.create_rental(
            customer=customer2,
            vehicle=vehicle2,
            start_date=today,
            end_date=today + timedelta(days=5),
        )
        print(f"Utworzono wypożyczenie: {rental2}")
    except Exception as e:
        print(f"Błąd podczas tworzenia wypożyczenia: {e}")

    # Sprawdzanie statusu pojazdów
    print("\n[ Status pojazdów ]")
    print(
        f"Pojazd {vehicle1.registration_number} jest "
        f"dostępny: {vehicle1.is_available()}"
    )
    print(
        f"Pojazd {vehicle2.registration_number} jest "
        f"dostępny: {vehicle2.is_available()}"
    )
    print(
        f"Pojazd {vehicle3.registration_number} jest"
        f" dostępny: {vehicle3.is_available()}"
    )

    # Lista aktywnych wypożyczeń
    print("\n[ Aktywne wypożyczenia ]")
    active_rentals = rental_manager.get_active_rentals()
    for rental in active_rentals:
        print(f"- {rental}")

    # Symulacja zakończenia wypożyczenia
    print("\n[ Zwrot pojazdu ]")
    try:
        return_date = today + timedelta(days=2)
        total_cost = rental_manager.complete_rental(
            rental1.rental_id, return_date
        )
        review = rental_manager.add_review(
            rental_id=rental1.rental_id,
            rating=5,
            comment="Bardzo sprawna obsługa i wygodny samochód",
            review_date=return_date,
        )
        print(f"Dodano opinię: {review}")
        print(
            f"Zakończono wypożyczenie {rental1.rental_id}."
            f" Całkowity koszt: {total_cost} PLN"
        )
    except Exception as e:
        print(f"Błąd podczas zwrotu pojazdu: {e}")

    # Symulacja anulowania wypożyczenia
    print("\n[ Anulowanie wypożyczenia ]")
    try:
        rental_manager.cancel_rental(rental2.rental_id)
        print(f"Anulowano wypożyczenie {rental2.rental_id}")
    except Exception as e:
        print(f"Błąd podczas anulowania wypożyczenia: {e}")

    # Sprawdzanie statusu pojazdów po zakończeniu/anulowaniu
    print("\n[ Status pojazdów po zwrocie/anulowaniu ]")
    print(
        f"Pojazd {vehicle1.registration_number} jest"
        f" dostępny: {vehicle1.is_available()}"
    )
    print(
        f"Pojazd {vehicle2.registration_number} jest "
        f"dostępny: {vehicle2.is_available()}"
    )

    # Generowanie raportu
    print("\n[ Raport wypożyczeń ]")
    report_start = today - timedelta(days=7)
    report_end = today + timedelta(days=7)
    report = rental_manager.generate_rental_report(report_start, report_end)

    print(
        f"Raport za okres: {report['period_start']} - {report['period_end']}"
    )
    print(f"Łączna liczba wypożyczeń: {report['total_rentals']}")
    print(f"Zakończone wypożyczenia: {report['completed_rentals']}")
    print(f"Aktywne wypożyczenia: {report['active_rentals']}")
    print(f"Anulowane wypożyczenia: {report['cancelled_rentals']}")
    print(f"Przeterminowane wypożyczenia: {report['overdue_rentals']}")
    print(f"Łączny przychód: {report['total_revenue']} PLN")
    print(
        f"Średni czas trwania wypożyczenia:"
        f"{report['average_rental_duration']:.1f} dni"
    )
    print("\n[ Oceny klientów ]")
    for customer in [customer1, customer2]:
        avg = rental_manager.get_average_rating_for_customer(
            customer.customer_id
        )
        print(f"{customer.full_name()}: Średnia ocena: {avg:.1f}/5")
        reviews = rental_manager.get_reviews_for_customer(
            customer.customer_id
        )
        for r in reviews:
            print(f" - {r}")


if __name__ == "__main__":
    main()
