import unittest
from unittest.mock import Mock, patch
from datetime import date, timedelta
from src.rental import Rental, RentalManager, RentalStatus, RentalException
from src.customers import Customer, CustomerCategory, DrivingLicense
from src.vehicles import Vehicle, VehicleStatus, VehicleType


class TestRental(unittest.TestCase):

    def setUp(self):
        self.today = date.today()
        # Mock dla obiektu Customer
        self.customer = Mock(spec=Customer)
        self.customer.customer_id = "CUST001"
        self.customer.full_name.return_value = "Jan Kowalski"
        # Mock dla obiektu Vehicle
        self.vehicle = Mock(spec=Vehicle)
        self.vehicle.vehicle_id = "VEH001"
        self.vehicle.__str__ = Mock(return_value="Toyota Corolla (2020) - WA12345")
        # Tworzenie obiektu Rental
        self.rental = Rental(
            rental_id="RENT001",
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
            daily_rate=150.0,
        )

    def test_rental_initialization(self):
        self.assertEqual(self.rental.rental_id, "RENT001")
        self.assertEqual(self.rental.customer, self.customer)
        self.assertEqual(self.rental.vehicle, self.vehicle)
        self.assertEqual(self.rental.start_date, self.today)
        self.assertEqual(self.rental.end_date, self.today + timedelta(days=3))
        self.assertEqual(self.rental.daily_rate, 150.0)
        self.assertEqual(self.rental.status, RentalStatus.ACTIVE)
        self.assertIsNone(self.rental.actual_return_date)
        self.assertIsNone(self.rental.total_cost)
        self.assertEqual(self.rental.additional_charges, {})

    def test_rental_initialization_invalid_data(self):
        with self.assertRaises(ValueError):
            Rental(
                "",
                self.customer,
                self.vehicle,
                self.today,
                self.today + timedelta(days=3),
                150.0,
            )
        with self.assertRaises(ValueError):
            Rental(
                "RENT001",
                "nie_klient",
                self.vehicle,
                self.today,
                self.today + timedelta(days=3),
                150.0,
            )
        with self.assertRaises(ValueError):
            Rental(
                "RENT001",
                self.customer,
                "nie_pojazd",
                self.today,
                self.today + timedelta(days=3),
                150.0,
            )
        with self.assertRaises(ValueError):
            Rental(
                "RENT001",
                self.customer,
                self.vehicle,
                "nie_data",
                self.today + timedelta(days=3),
                150.0,
            )
        with self.assertRaises(ValueError):
            Rental(
                "RENT001", self.customer, self.vehicle, self.today, "nie_data", 150.0
            )
        with self.assertRaises(ValueError):
            Rental(
                "RENT001",
                self.customer,
                self.vehicle,
                self.today + timedelta(days=3),
                self.today,
                150.0,
            )
        with self.assertRaises(ValueError):
            Rental(
                "RENT001",
                self.customer,
                self.vehicle,
                self.today,
                self.today + timedelta(days=3),
                -10.0,
            )

    def test_str_representation(self):
        expected_str = (
            f"Wypożyczenie RENT001: Jan Kowalski - "
            f"Toyota Corolla (2020) - WA12345, {self.today} do {self.today + timedelta(days=3)}, "
            f"status: active"
        )
        self.assertEqual(str(self.rental), expected_str)

    def test_calculate_duration(self):
        self.assertEqual(self.rental.calculate_duration(), 4)
        rental_same_day = Rental(
            rental_id="RENT002",
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today,
            daily_rate=150.0,
        )
        self.assertEqual(rental_same_day.calculate_duration(), 1)

    def test_calculate_base_cost(self):
        self.assertEqual(self.rental.calculate_base_cost(), 600.0)
        rental_same_day = Rental(
            rental_id="RENT002",
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today,
            daily_rate=150.0,
        )
        self.assertEqual(rental_same_day.calculate_base_cost(), 150.0)

    def test_is_overdue(self):
        self.assertFalse(self.rental.is_overdue(self.today + timedelta(days=2)))
        self.assertFalse(self.rental.is_overdue(self.today + timedelta(days=3)))
        self.assertTrue(self.rental.is_overdue(self.today + timedelta(days=4)))
        self.rental.status = RentalStatus.COMPLETED
        self.assertFalse(self.rental.is_overdue(self.today + timedelta(days=4)))

    def test_add_charge(self):
        self.assertEqual(len(self.rental.additional_charges), 0)
        self.rental.add_charge("Ubezpieczenie", 50.0)
        self.assertEqual(len(self.rental.additional_charges), 1)
        self.assertEqual(self.rental.additional_charges["Ubezpieczenie"], 50.0)
        self.rental.add_charge("Pełny bak", 100.0)
        self.assertEqual(len(self.rental.additional_charges), 2)
        self.assertEqual(self.rental.additional_charges["Pełny bak"], 100.0)
        with self.assertRaises(ValueError):
            self.rental.add_charge("", 50.0)
        with self.assertRaises(ValueError):
            self.rental.add_charge("Ubezpieczenie", -10.0)

    def test_complete(self):
        self.vehicle.change_status = Mock()
        return_date = self.today + timedelta(days=3)
        cost = self.rental.complete(return_date)
        self.assertEqual(self.rental.status, RentalStatus.COMPLETED)
        self.assertEqual(self.rental.actual_return_date, return_date)
        self.assertEqual(cost, 600.0)
        self.vehicle.change_status.assert_called_once_with(VehicleStatus.AVAILABLE)

    def test_complete_with_additional_charges(self):
        self.vehicle.change_status = Mock()
        self.rental.add_charge("Ubezpieczenie", 50.0)
        self.rental.add_charge("Pełny bak", 100.0)
        return_date = self.today + timedelta(days=3)
        cost = self.rental.complete(return_date)
        self.assertEqual(cost, 750.0)

    def test_complete_with_late_return(self):
        self.vehicle.change_status = Mock()
        return_date = self.today + timedelta(days=5)
        cost = self.rental.complete(return_date)
        self.assertEqual(cost, 1050.0)
        self.assertIn("Opłata za opóźnienie", self.rental.additional_charges)
        self.assertEqual(self.rental.additional_charges["Opłata za opóźnienie"], 450.0)

    def test_complete_non_active_rental(self):
        self.rental.status = RentalStatus.CANCELLED
        with self.assertRaises(RentalException):
            self.rental.complete(self.today + timedelta(days=3))

    def test_cancel(self):
        self.vehicle.change_status = Mock()
        self.rental.cancel()
        self.assertEqual(self.rental.status, RentalStatus.CANCELLED)
        self.vehicle.change_status.assert_called_once_with(VehicleStatus.AVAILABLE)

    def test_cancel_completed_rental(self):
        self.rental.status = RentalStatus.COMPLETED
        with self.assertRaises(RentalException):
            self.rental.cancel()

    def test_cancel_already_cancelled_rental(self):
        self.rental.status = RentalStatus.CANCELLED
        with self.assertRaises(RentalException):
            self.rental.cancel()


class TestRentalManager(unittest.TestCase):

    def setUp(self):
        self.today = date.today()
        self.license = DrivingLicense(
            license_number="ABC123456",
            issue_date=self.today - timedelta(days=365),
            expiry_date=self.today + timedelta(days=365),
            categories=["B", "C"],
        )

        self.customer = Customer(
            customer_id="CUST001",
            first_name="Jan",
            last_name="Kowalski",
            email="jan.kowalski@example.com",
            phone="123456789",
            address="ul. Przykładowa 1, Warszawa",
            driving_license=self.license,
        )

        self.vehicle = Vehicle(
            vehicle_id="VEH001",
            make="Toyota",
            model="Corolla",
            year=2020,
            registration_number="WA12345",
            daily_rate=150.0,
            vehicle_type=VehicleType.COMPACT,
        )

        self.manager = RentalManager()

        self.rental = Rental(
            rental_id="RENT001",
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
            daily_rate=150.0,
        )
        self.manager = RentalManager()

    @patch("uuid.uuid4")
    def test_create_rental(self, mock_uuid):
        mock_uuid.return_value = "mocked-uuid"
        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )
        self.assertEqual(rental.rental_id, "mocked-uuid")
        self.assertEqual(rental.customer, self.customer)
        self.assertEqual(rental.vehicle, self.vehicle)
        self.assertEqual(rental.start_date, self.today)
        self.assertEqual(rental.end_date, self.today + timedelta(days=3))
        self.assertEqual(rental.daily_rate, 150.0)
        self.assertEqual(rental.status, RentalStatus.ACTIVE)
        self.assertEqual(self.vehicle.status, VehicleStatus.RENTED)
        self.assertIn(rental.rental_id, self.customer.rental_history)
        self.assertIn(rental.rental_id, self.manager.rentals)

    def test_create_rental_with_category_discount(self):
        self.customer.category = CustomerCategory.SILVER
        # Resetowanie statusu pojazdu
        self.vehicle.change_status(VehicleStatus.AVAILABLE)
        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )
        self.assertEqual(rental.daily_rate, 142.5)

        # Resetowanie statusu pojazdu
        self.vehicle.change_status(VehicleStatus.AVAILABLE)
        self.customer.category = CustomerCategory.GOLD
        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )
        self.assertEqual(rental.daily_rate, 135.0)

        # Resetowanie statusu pojazdu
        self.vehicle.change_status(VehicleStatus.AVAILABLE)
        self.customer.category = CustomerCategory.PLATINUM
        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )
        self.assertEqual(rental.daily_rate, 127.5)

    def test_create_rental_invalid_customer(self):
        with self.assertRaises(ValueError):
            self.manager.create_rental(
                customer="nie_klient",
                vehicle=self.vehicle,
                start_date=self.today,
                end_date=self.today + timedelta(days=3),
            )

    def test_create_rental_invalid_vehicle(self):
        with self.assertRaises(ValueError):
            self.manager.create_rental(
                customer=self.customer,
                vehicle="nie_pojazd",
                start_date=self.today,
                end_date=self.today + timedelta(days=3),
            )

    def test_create_rental_with_invalid_dates(self):
        with self.assertRaises(RentalException):
            self.manager.create_rental(
                customer=self.customer,
                vehicle=self.vehicle,
                start_date=self.today + timedelta(days=3),
                end_date=self.today,
            )
        with self.assertRaises(RentalException):
            self.manager.create_rental(
                customer=self.customer,
                vehicle=self.vehicle,
                start_date=self.today - timedelta(days=1),
                end_date=self.today + timedelta(days=3),
            )

    def test_create_rental_with_unavailable_vehicle(self):
        self.vehicle.change_status(VehicleStatus.RENTED)
        with self.assertRaises(RentalException):
            self.manager.create_rental(
                customer=self.customer,
                vehicle=self.vehicle,
                start_date=self.today,
                end_date=self.today + timedelta(days=3),
            )

    def test_create_rental_with_invalid_license(self):
        self.customer.can_rent = Mock(return_value=False)
        with self.assertRaises(RentalException):
            self.manager.create_rental(
                customer=self.customer,
                vehicle=self.vehicle,
                start_date=self.today,
                end_date=self.today + timedelta(days=3),
            )

    def test_get_rental(self):
        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )
        retrieved_rental = self.manager.get_rental(rental.rental_id)
        self.assertEqual(retrieved_rental, rental)
        retrieved_rental = self.manager.get_rental("nieistniejace_id")
        self.assertIsNone(retrieved_rental)

    def test_complete_rental(self):
        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )
        cost = self.manager.complete_rental(
            rental.rental_id, self.today + timedelta(days=3)
        )
        self.assertEqual(rental.status, RentalStatus.COMPLETED)
        self.assertEqual(rental.actual_return_date, self.today + timedelta(days=3))
        self.assertEqual(cost, 600.0)

    def test_complete_nonexistent_rental(self):
        with self.assertRaises(RentalException):
            self.manager.complete_rental("nieistniejace_id", self.today)

    def test_cancel_rental(self):
        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )
        self.manager.cancel_rental(rental.rental_id)
        self.assertEqual(rental.status, RentalStatus.CANCELLED)
        self.assertEqual(self.vehicle.status, VehicleStatus.AVAILABLE)

    def test_cancel_nonexistent_rental(self):
        with self.assertRaises(RentalException):
            self.manager.cancel_rental("nieistniejace_id")

    def test_get_active_rentals(self):
        active_rentals = self.manager.get_active_rentals()
        self.assertEqual(len(active_rentals), 0)
        rental1 = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )
        vehicle2 = Vehicle(
            vehicle_id="VEH002",
            make="Ford",
            model="Focus",
            year=2021,
            registration_number="WA54321",
            daily_rate=170.0,
            vehicle_type=VehicleType.STANDARD,
        )
        rental2 = self.manager.create_rental(
            customer=self.customer,
            vehicle=vehicle2,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )
        active_rentals = self.manager.get_active_rentals()
        self.assertEqual(len(active_rentals), 2)
        self.assertIn(rental1, active_rentals)
        self.assertIn(rental2, active_rentals)
        self.manager.cancel_rental(rental1.rental_id)
        active_rentals = self.manager.get_active_rentals()
        self.assertEqual(len(active_rentals), 1)
        self.assertIn(rental2, active_rentals)

    def test_get_overdue_rentals(self):
        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )

        # symulujemy, że dziś jest późniejszy dzień
        simulated_today = self.today + timedelta(days=10)
        overdue_rentals = self.manager.get_overdue_rentals(current_date=simulated_today)

        self.assertEqual(len(overdue_rentals), 1)
        self.assertIn(rental, overdue_rentals)

    def test_get_customer_rentals(self):
        license2 = DrivingLicense(
            license_number="XYZ789012",
            issue_date=self.today - timedelta(days=365),
            expiry_date=self.today + timedelta(days=365),
            categories=["B"],
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
        vehicle2 = Vehicle(
            vehicle_id="VEH002",
            make="Ford",
            model="Focus",
            year=2021,
            registration_number="WA54321",
            daily_rate=170.0,
            vehicle_type=VehicleType.STANDARD,
        )
        rental1 = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )
        rental2 = self.manager.create_rental(
            customer=customer2,
            vehicle=vehicle2,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )
        customer_rentals = self.manager.get_customer_rentals(self.customer.customer_id)
        self.assertEqual(len(customer_rentals), 1)
        self.assertIn(rental1, customer_rentals)
        self.assertNotIn(rental2, customer_rentals)
        customer_rentals = self.manager.get_customer_rentals(customer2.customer_id)
        self.assertEqual(len(customer_rentals), 1)
        self.assertIn(rental2, customer_rentals)
        self.assertNotIn(rental1, customer_rentals)
        customer_rentals = self.manager.get_customer_rentals("NIEISTNIEJACY")
        self.assertEqual(len(customer_rentals), 0)

    def test_get_vehicle_rental_history(self):
        rental1 = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )
        self.manager.complete_rental(rental1.rental_id, self.today + timedelta(days=3))
        rental2 = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today + timedelta(days=4),
            end_date=self.today + timedelta(days=7),
        )
        vehicle_history = self.manager.get_vehicle_rental_history(
            self.vehicle.vehicle_id
        )
        self.assertEqual(len(vehicle_history), 2)
        self.assertIn(rental1, vehicle_history)
        self.assertIn(rental2, vehicle_history)
        vehicle_history = self.manager.get_vehicle_rental_history("NIEISTNIEJACY")
        self.assertEqual(len(vehicle_history), 0)

    def test_generate_rental_report(self):
        """Test generowania raportu wypożyczeń"""
        # Tworzenie wypożyczeń
        rental1 = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )
        vehicle2 = Vehicle(
            vehicle_id="VEH002",
            make="Ford",
            model="Focus",
            year=2021,
            registration_number="WA54321",
            daily_rate=170.0,
            vehicle_type=VehicleType.STANDARD,
        )
        rental2 = self.manager.create_rental(
            customer=self.customer,
            vehicle=vehicle2,
            start_date=self.today + timedelta(days=1),
            end_date=self.today + timedelta(days=6),
        )
        self.manager.complete_rental(rental1.rental_id, self.today + timedelta(days=3))
        self.manager.cancel_rental(rental2.rental_id)
        vehicle3 = Vehicle(
            vehicle_id="VEH003",
            make="BMW",
            model="X5",
            year=2022,
            registration_number="WA99999",
            daily_rate=350.0,
            vehicle_type=VehicleType.PREMIUM,
        )
        rental3 = self.manager.create_rental(
            customer=self.customer,
            vehicle=vehicle3,
            start_date=self.today + timedelta(days=2),
            end_date=self.today + timedelta(days=5),
        )
        report = self.manager.generate_rental_report(
            start_date=self.today, end_date=self.today + timedelta(days=10)
        )
        self.assertEqual(report["total_rentals"], 3)
        self.assertEqual(report["completed_rentals"], 1)
        self.assertEqual(report["cancelled_rentals"], 1)
        self.assertEqual(report["active_rentals"], 1)
        self.assertEqual(report["overdue_rentals"], 0)
        self.assertEqual(report["total_revenue"], 600.0)
        self.assertAlmostEqual(report["average_rental_duration"], 4.666666666666667)

    # Dodatkowe testy walidacyjne
    def test_generate_rental_report_invalid_dates(self):
        with self.assertRaises(ValueError):
            self.manager.generate_rental_report("nie_data", self.today)
        with self.assertRaises(ValueError):
            self.manager.generate_rental_report(self.today, "nie_data")
        with self.assertRaises(ValueError):
            self.manager.generate_rental_report(
                self.today + timedelta(days=1), self.today
            )

    def test_get_rental_invalid_id(self):
        with self.assertRaises(ValueError):
            self.manager.get_rental("")
        with self.assertRaises(ValueError):
            self.manager.get_rental(123)

    def test_get_customer_rentals_invalid_id(self):
        with self.assertRaises(ValueError):
            self.manager.get_customer_rentals("")
        with self.assertRaises(ValueError):
            self.manager.get_customer_rentals(123)

    def test_get_vehicle_rental_history_invalid_id(self):
        with self.assertRaises(ValueError):
            self.manager.get_vehicle_rental_history("")

        with self.assertRaises(ValueError):
            self.manager.get_vehicle_rental_history(123)

    def test_complete_rental_invalid_params(self):
        """Test zakończenia wypożyczenia z niepoprawnymi parametrami"""
        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )

        with self.assertRaises(ValueError):
            self.manager.complete_rental("", self.today + timedelta(days=3))

        with self.assertRaises(ValueError):
            self.manager.complete_rental(rental.rental_id, "nie_data")

    def test_cancel_rental_invalid_id(self):
        """Test anulowania wypożyczenia z niepoprawnym ID"""
        with self.assertRaises(ValueError):
            self.manager.cancel_rental("")

        with self.assertRaises(ValueError):
            self.manager.cancel_rental(123)

    def test_multiple_rentals_same_vehicle(self):
        """Test wypożyczenia tego samego pojazdu wielokrotnie"""
        rental1 = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )

        # Próba wypożyczenia już wypożyczonego pojazdu
        with self.assertRaises(RentalException):
            rental2 = self.manager.create_rental(
                customer=self.customer,
                vehicle=self.vehicle,
                start_date=self.today + timedelta(days=1),
                end_date=self.today + timedelta(days=5),
            )

        # Zakończenie pierwszego wypożyczenia
        self.manager.complete_rental(rental1.rental_id, self.today + timedelta(days=3))

        rental3 = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today + timedelta(days=4),
            end_date=self.today + timedelta(days=7),
        )

        self.assertEqual(rental3.vehicle, self.vehicle)
        self.assertEqual(rental3.status, RentalStatus.ACTIVE)

    def test_rental_status_changes(self):
        """Test zmian statusu wypożyczenia"""
        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )

        self.assertEqual(rental.status, RentalStatus.ACTIVE)

        # Anulowanie wypożyczenia
        self.manager.cancel_rental(rental.rental_id)
        self.assertEqual(rental.status, RentalStatus.CANCELLED)

        # Tworzenie nowego wypożyczenia
        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )

        # Zakończenie wypożyczenia
        self.manager.complete_rental(rental.rental_id, self.today + timedelta(days=3))
        self.assertEqual(rental.status, RentalStatus.COMPLETED)

    def test_rental_with_late_return_status(self):
        """Test statusu wypożyczenia z opóźnionym zwrotem"""
        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )

        # Symulacja opóźnionego zwrotu
        late_return_date = self.today + timedelta(days=5)
        self.manager.complete_rental(rental.rental_id, late_return_date)

        # Sprawdzenie naliczenia opłaty za opóźnienie
        self.assertIn("Opłata za opóźnienie", rental.additional_charges)
        self.assertEqual(
            rental.additional_charges["Opłata za opóźnienie"], 450.0
        )  # 2 dni * 150 * 1.5
        self.assertEqual(rental.status, RentalStatus.COMPLETED)

    def test_rental_with_multiple_additional_charges(self):
        """Test wypożyczenia z wieloma dodatkowymi opłatami"""
        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )

        rental.add_charge("Ubezpieczenie", 50.0)
        rental.add_charge("Pełny bak", 100.0)
        rental.add_charge("GPS", 30.0)
        rental.add_charge("Fotelik dziecięcy", 25.0)

        self.assertEqual(len(rental.additional_charges), 4)

        cost = self.manager.complete_rental(
            rental.rental_id, self.today + timedelta(days=3)
        )
        expected_cost = 600.0 + 50.0 + 100.0 + 30.0 + 25.0
        self.assertEqual(cost, expected_cost)

    def test_is_overdue_with_invalid_date(self):
        """Test sprawdzania przekroczenia terminu z niepoprawną datą"""
        with self.assertRaises(ValueError):
            self.rental.is_overdue("niepoprawna_data")

    def test_get_overdue_rentals_with_no_rentals(self):
        """Test pobierania przeterminowanych wypożyczeń gdy nie ma żadnych wypożyczeń"""
        overdue_rentals = self.manager.get_overdue_rentals()
        self.assertEqual(len(overdue_rentals), 0)

    def test_generate_rental_report_with_empty_period(self):
        """Test generowania raportu dla okresu bez wypożyczeń"""
        future_date = self.today + timedelta(days=100)
        report = self.manager.generate_rental_report(
            start_date=future_date, end_date=future_date + timedelta(days=10)
        )

        self.assertEqual(report["total_rentals"], 0)
        self.assertEqual(report["completed_rentals"], 0)
        self.assertEqual(report["cancelled_rentals"], 0)
        self.assertEqual(report["active_rentals"], 0)
        self.assertEqual(report["overdue_rentals"], 0)
        self.assertEqual(report["total_revenue"], 0)
        self.assertEqual(report["average_rental_duration"], 0)

    def test_complete_rental_with_invalid_return_date(self):
        """Test zakończenia wypożyczenia z niepoprawną datą zwrotu"""
        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )
        # Próba zakończenia wypożyczenia z datą zwrotu wcześniejszą niż data rozpoczęcia
        invalid_return_date = self.today - timedelta(days=1)
        with self.assertRaises(ValueError):
            self.manager.complete_rental(rental.rental_id, invalid_return_date)

    def test_add_review_to_active_rental(self):
        """Test dodawania opinii do aktywnego wypożyczenia"""
        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )

        # Próba dodania opinii do aktywnego wypożyczenia
        with self.assertRaises(RentalException):
            self.manager.add_review(
                rental_id=rental.rental_id,
                rating=5,
                comment="Świetne auto!",
                review_date=self.today,
            )

    def test_create_rental_with_minimum_duration(self):
        """Test tworzenia wypożyczenia na minimalny okres (1 dzień)"""
        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today,
        )

        self.assertEqual(rental.calculate_duration(), 1)
        self.assertEqual(rental.calculate_base_cost(), self.vehicle.daily_rate)

    def test_create_rental_with_exact_license_expiry(self):
        """Test wypożyczenia z prawem jazdy wygasającym dokładnie w dniu zakończenia wypożyczenia"""
        # Modyfikujemy datę ważności prawa jazdy
        original_expiry = self.customer.driving_license.expiry_date
        self.customer.driving_license.expiry_date = self.today + timedelta(days=3)

        try:
            rental = self.manager.create_rental(
                customer=self.customer,
                vehicle=self.vehicle,
                start_date=self.today,
                end_date=self.today + timedelta(days=3),
            )

            self.assertEqual(rental.status, RentalStatus.ACTIVE)
        finally:
            # Przywracamy oryginalną datę ważności
            self.customer.driving_license.expiry_date = original_expiry

    def test_rental_with_license_expiring_during_rental(self):
        """Test wypożyczenia gdy prawo jazdy wygasa w trakcie okresu wypożyczenia"""
        # Ustawienie prawa jazdy wygasającego w trakcie wypożyczenia
        today = date.today()
        original_expiry = self.customer.driving_license.expiry_date
        self.customer.driving_license.expiry_date = today + timedelta(days=1)

        try:
            # Próba wypożyczenia na okres dłuższy niż ważność prawa jazdy
            with self.assertRaises(RentalException):
                self.manager.create_rental(
                    customer=self.customer,
                    vehicle=self.vehicle,
                    start_date=today,
                    end_date=today + timedelta(days=5),
                )
        finally:
            # Przywrócenie oryginalnej daty ważności
            self.customer.driving_license.expiry_date = original_expiry

    def test_complete_rental_with_return_date_before_start_date(self):
        """Test zakończenia wypożyczenia z datą zwrotu wcześniejszą niż data rozpoczęcia"""
        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )

        # Próba zakończenia wypożyczenia z datą zwrotu wcześniejszą niż data rozpoczęcia
        with self.assertRaises(ValueError):
            self.manager.complete_rental(
                rental_id=rental.rental_id, return_date=self.today - timedelta(days=1)
            )

    def test_vehicle_status_change_during_active_rental(self):
        """Test zmiany statusu pojazdu podczas aktywnego wypożyczenia"""
        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )

        # Sprawdzenie czy status pojazdu jest RENTED
        self.assertEqual(self.vehicle.status, VehicleStatus.RENTED)

        # Ręczna zmiana statusu pojazdu podczas aktywnego wypożyczenia
        self.vehicle.change_status(VehicleStatus.MAINTENANCE)

        # Sprawdzenie czy zmiana statusu została zastosowana
        self.assertEqual(self.vehicle.status, VehicleStatus.MAINTENANCE)

        # Próba zakończenia wypożyczenia - powinno przywrócić status na AVAILABLE
        self.manager.complete_rental(
            rental_id=rental.rental_id, return_date=self.today + timedelta(days=3)
        )

        # Sprawdzenie czy status pojazdu został zmieniony na AVAILABLE
        self.assertEqual(self.vehicle.status, VehicleStatus.AVAILABLE)

    # W klasie TestRental
    def test_complete_rental_with_invalid_return_date(self):
        """Test zakończenia wypożyczenia z niepoprawną datą zwrotu"""
        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )

        # Próba zakończenia wypożyczenia z datą zwrotu wcześniejszą niż data rozpoczęcia
        invalid_return_date = self.today - timedelta(days=1)
        with self.assertRaises(ValueError):
            self.manager.complete_rental(rental.rental_id, invalid_return_date)

    def test_add_review_to_active_rental(self):
        """Test dodawania opinii do aktywnego wypożyczenia"""
        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3),
        )

        # Próba dodania opinii do aktywnego wypożyczenia
        with self.assertRaises(RentalException):
            self.manager.add_review(
                rental_id=rental.rental_id,
                rating=5,
                comment="Świetne auto!",
                review_date=self.today,
            )

    def test_create_rental_with_minimum_duration(self):
        """Test tworzenia wypożyczenia na minimalny okres (1 dzień)"""
        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today,  # Ten sam dzień
        )

        self.assertEqual(rental.calculate_duration(), 1)
        self.assertEqual(rental.calculate_base_cost(), self.vehicle.daily_rate)

    def test_rental_with_license_expiring_during_rental(self):
        """Test wypożyczenia gdy prawo jazdy wygasa w trakcie okresu wypożyczenia"""
        # Ustawienie prawa jazdy wygasającego w trakcie wypożyczenia
        today = date.today()
        original_expiry = self.customer.driving_license.expiry_date
        self.customer.driving_license.expiry_date = today + timedelta(days=1)

        try:
            # Próba wypożyczenia na okres dłuższy niż ważność prawa jazdy
            with self.assertRaises(RentalException):
                self.manager.create_rental(
                    customer=self.customer,
                    vehicle=self.vehicle,
                    start_date=today,
                    end_date=today + timedelta(days=5),
                )
        finally:
            # Przywrócenie oryginalnej daty ważności
            self.customer.driving_license.expiry_date = original_expiry

    if __name__ == "__main__":
        unittest.main()
