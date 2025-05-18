import unittest
from datetime import date
from src.vehicles import (
    Vehicle,
    Car,
    VehicleInventory,
    VehicleType,
    VehicleStatus,
)


class TestVehicle(unittest.TestCase):

    def setUp(self):
        self.vehicle = Vehicle(
            vehicle_id="TEST001",
            make="Toyota",
            model="Corolla",
            year=2020,
            registration_number="WA12345",
            daily_rate=150.0,
            vehicle_type=VehicleType.COMPACT,
        )

    def test_vehicle_initialization(self):
        """Test poprawnej inicjalizacji pojazdu"""
        self.assertEqual(self.vehicle.vehicle_id, "TEST001")
        self.assertEqual(self.vehicle.make, "Toyota")
        self.assertEqual(self.vehicle.model, "Corolla")
        self.assertEqual(self.vehicle.year, 2020)
        self.assertEqual(self.vehicle.registration_number, "WA12345")
        self.assertEqual(self.vehicle.daily_rate, 150.0)
        self.assertEqual(self.vehicle.vehicle_type, VehicleType.COMPACT)
        self.assertEqual(self.vehicle.status, VehicleStatus.AVAILABLE)
        self.assertEqual(self.vehicle.maintenance_history, [])

    def test_vehicle_str_representation(self):
        """Test reprezentacji tekstowej pojazdu"""
        expected_str = "Toyota Corolla (2020) - WA12345"
        self.assertEqual(str(self.vehicle), expected_str)

    def test_change_status(self):
        """Test zmiany statusu pojazdu"""
        self.assertEqual(self.vehicle.status, VehicleStatus.AVAILABLE)

        self.vehicle.change_status(VehicleStatus.RENTED)
        self.assertEqual(self.vehicle.status, VehicleStatus.RENTED)

        self.vehicle.change_status(VehicleStatus.MAINTENANCE)
        self.assertEqual(self.vehicle.status, VehicleStatus.MAINTENANCE)

    def test_change_status_invalid_type(self):
        """Test zmiany statusu pojazdu na niepoprawny typ"""
        with self.assertRaises(ValueError):
            self.vehicle.change_status("available")

    def test_is_available(self):
        """Test sprawdzania dostępności pojazdu"""
        self.assertTrue(self.vehicle.is_available())

        self.vehicle.change_status(VehicleStatus.RENTED)
        self.assertFalse(self.vehicle.is_available())

        self.vehicle.change_status(VehicleStatus.AVAILABLE)
        self.assertTrue(self.vehicle.is_available())

    def test_add_maintenance_record(self):
        """Test dodawania zapisów konserwacji"""
        today = date.today()
        self.vehicle.add_maintenance_record("Wymiana oleju", today, 250.0)

        self.assertEqual(len(self.vehicle.maintenance_history), 1)
        record = self.vehicle.maintenance_history[0]
        self.assertEqual(record["description"], "Wymiana oleju")
        self.assertEqual(record["date"], today)
        self.assertEqual(record["cost"], 250.0)

    def test_add_maintenance_record_invalid_data(self):
        """Test dodawania zapisów konserwacji z niepoprawnymi danymi"""
        today = date.today()

        with self.assertRaises(ValueError):
            self.vehicle.add_maintenance_record("", today, 250.0)

        with self.assertRaises(ValueError):
            self.vehicle.add_maintenance_record(
                "Wymiana oleju", "dzisiaj", 250.0
            )

        with self.assertRaises(ValueError):
            self.vehicle.add_maintenance_record("Wymiana oleju", today, -50.0)

    def test_vehicle_initialization_invalid_data(self):
        """Test inicjalizacji pojazdu z niepoprawnymi danymi"""
        with self.assertRaises(ValueError):
            Vehicle(
                "",
                "Toyota",
                "Corolla",
                2020,
                "WA12345",
                150.0,
                VehicleType.COMPACT,
            )

        with self.assertRaises(ValueError):
            Vehicle(
                "TEST001",
                "",
                "Corolla",
                2020,
                "WA12345",
                150.0,
                VehicleType.COMPACT,
            )

        with self.assertRaises(ValueError):
            Vehicle(
                "TEST001",
                "Toyota",
                "",
                2020,
                "WA12345",
                150.0,
                VehicleType.COMPACT,
            )

        with self.assertRaises(ValueError):
            Vehicle(
                "TEST001",
                "Toyota",
                "Corolla",
                1800,
                "WA12345",
                150.0,
                VehicleType.COMPACT,
            )

        with self.assertRaises(ValueError):
            Vehicle(
                "TEST001",
                "Toyota",
                "Corolla",
                2030,
                "WA12345",
                150.0,
                VehicleType.COMPACT,
            )

        with self.assertRaises(ValueError):
            Vehicle(
                "TEST001",
                "Toyota",
                "Corolla",
                2020,
                "",
                150.0,
                VehicleType.COMPACT,
            )

        with self.assertRaises(ValueError):
            Vehicle(
                "TEST001",
                "Toyota",
                "Corolla",
                2020,
                "WA12345",
                -10.0,
                VehicleType.COMPACT,
            )

        with self.assertRaises(ValueError):
            Vehicle(
                "TEST001",
                "Toyota",
                "Corolla",
                2020,
                "WA12345",
                150.0,
                "compact",
            )

    def test_add_maintenance_record_with_zero_cost(self):
        """Test dodawania zapisu konserwacji z zerowim kosztem"""
        today = date.today()
        self.vehicle.add_maintenance_record(
            "Przegląd gwarancyjny", today, 0.0
        )

        self.assertEqual(len(self.vehicle.maintenance_history), 1)
        record = self.vehicle.maintenance_history[0]
        self.assertEqual(record["cost"], 0.0)

    def test_change_status_multiple_times(self):
        """Test wielokrotnej zmiany statusu pojazdu"""
        self.assertEqual(self.vehicle.status, VehicleStatus.AVAILABLE)

        self.vehicle.change_status(VehicleStatus.RENTED)
        self.assertEqual(self.vehicle.status, VehicleStatus.RENTED)

        self.vehicle.change_status(VehicleStatus.MAINTENANCE)
        self.assertEqual(self.vehicle.status, VehicleStatus.MAINTENANCE)

        self.vehicle.change_status(VehicleStatus.OUT_OF_SERVICE)
        self.assertEqual(self.vehicle.status, VehicleStatus.OUT_OF_SERVICE)

        self.vehicle.change_status(VehicleStatus.AVAILABLE)
        self.assertEqual(self.vehicle.status, VehicleStatus.AVAILABLE)


class TestCar(unittest.TestCase):
    """Testy dla klasy Car"""

    def setUp(self):
        """Ustawienie danych testowych"""
        self.car = Car(
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

    def test_car_initialization(self):
        """Test poprawnej inicjalizacji samochodu"""
        self.assertEqual(self.car.vehicle_id, "CAR001")
        self.assertEqual(self.car.make, "Toyota")
        self.assertEqual(self.car.model, "Corolla")
        self.assertEqual(self.car.year, 2020)
        self.assertEqual(self.car.registration_number, "WA12345")
        self.assertEqual(self.car.daily_rate, 150.0)
        self.assertEqual(self.car.vehicle_type, VehicleType.COMPACT)
        self.assertEqual(self.car.doors, 5)
        self.assertEqual(self.car.fuel_type, "Benzyna")
        self.assertEqual(self.car.transmission, "Manualna")

    def test_car_str_representation(self):
        """Test reprezentacji tekstowej samochodu"""
        expected_str = (
            "Toyota Corolla (2020) - WA12345, 5 drzwi, Benzyna, Manualna"
        )
        self.assertEqual(str(self.car), expected_str)

    def test_car_initialization_invalid_data(self):
        """Test inicjalizacji samochodu z niepoprawnymi danymi"""
        with self.assertRaises(ValueError):
            Car(
                "CAR001",
                "Toyota",
                "Corolla",
                2020,
                "WA12345",
                150.0,
                VehicleType.COMPACT,
                0,
                "Benzyna",
                "Manualna",
            )

        with self.assertRaises(ValueError):
            Car(
                "CAR001",
                "Toyota",
                "Corolla",
                2020,
                "WA12345",
                150.0,
                VehicleType.COMPACT,
                5,
                "",
                "Manualna",
            )

        with self.assertRaises(ValueError):
            Car(
                "CAR001",
                "Toyota",
                "Corolla",
                2020,
                "WA12345",
                150.0,
                VehicleType.COMPACT,
                5,
                "Benzyna",
                "",
            )


class TestVehicleInventory(unittest.TestCase):
    """Testy dla klasy VehicleInventory"""

    def setUp(self):
        """Ustawienie danych testowych"""
        self.inventory = VehicleInventory()

        self.vehicle1 = Vehicle(
            vehicle_id="TEST001",
            make="Toyota",
            model="Corolla",
            year=2020,
            registration_number="WA12345",
            daily_rate=150.0,
            vehicle_type=VehicleType.COMPACT,
        )

        self.vehicle2 = Vehicle(
            vehicle_id="TEST002",
            make="Ford",
            model="Focus",
            year=2021,
            registration_number="WA54321",
            daily_rate=170.0,
            vehicle_type=VehicleType.STANDARD,
        )

        self.vehicle3 = Vehicle(
            vehicle_id="TEST003",
            make="BMW",
            model="X5",
            year=2022,
            registration_number="WA99999",
            daily_rate=350.0,
            vehicle_type=VehicleType.PREMIUM,
        )

    def test_add_vehicle(self):
        """Test dodawania pojazdu do inwentarza"""
        self.inventory.add_vehicle(self.vehicle1)
        self.assertEqual(len(self.inventory.vehicles), 1)
        self.assertIn("TEST001", self.inventory.vehicles)
        self.assertEqual(self.inventory.vehicles["TEST001"], self.vehicle1)

    def test_add_duplicate_vehicle(self):
        """Test dodawania pojazdu z istniejącym ID"""
        self.inventory.add_vehicle(self.vehicle1)
        with self.assertRaises(ValueError):
            self.inventory.add_vehicle(self.vehicle1)

    def test_add_invalid_vehicle_type(self):
        """Test dodawania niepoprawnego typu jako pojazdu"""
        with self.assertRaises(TypeError):
            self.inventory.add_vehicle("nie_pojazd")

    def test_remove_vehicle(self):
        """Test usuwania pojazdu z inwentarza"""
        self.inventory.add_vehicle(self.vehicle1)
        self.inventory.add_vehicle(self.vehicle2)

        self.assertEqual(len(self.inventory.vehicles), 2)

        self.inventory.remove_vehicle("TEST001")

        self.assertEqual(len(self.inventory.vehicles), 1)
        self.assertNotIn("TEST001", self.inventory.vehicles)
        self.assertIn("TEST002", self.inventory.vehicles)

    def test_remove_nonexistent_vehicle(self):
        """Test usuwania nieistniejącego pojazdu"""
        with self.assertRaises(ValueError):
            self.inventory.remove_vehicle("NIEISTNIEJE")

    def test_get_vehicle(self):
        """Test pobierania pojazdu z inwentarza"""
        self.inventory.add_vehicle(self.vehicle1)
        self.inventory.add_vehicle(self.vehicle2)

        retrieved_vehicle = self.inventory.get_vehicle("TEST001")
        self.assertEqual(retrieved_vehicle, self.vehicle1)

        retrieved_vehicle = self.inventory.get_vehicle("TEST002")
        self.assertEqual(retrieved_vehicle, self.vehicle2)

        retrieved_vehicle = self.inventory.get_vehicle("NIEISTNIEJE")
        self.assertIsNone(retrieved_vehicle)

    def test_get_available_vehicles(self):
        """Test pobierania dostępnych pojazdów"""
        self.inventory.add_vehicle(self.vehicle1)
        self.inventory.add_vehicle(self.vehicle2)
        self.inventory.add_vehicle(self.vehicle3)

        available = self.inventory.get_available_vehicles()
        self.assertEqual(len(available), 3)

        self.vehicle2.change_status(VehicleStatus.RENTED)
        available = self.inventory.get_available_vehicles()
        self.assertEqual(len(available), 2)
        self.assertIn(self.vehicle1, available)
        self.assertIn(self.vehicle3, available)
        self.assertNotIn(self.vehicle2, available)

    def test_get_available_vehicles_by_type(self):
        """Test pobierania dostępnych pojazdów według typu"""
        self.inventory.add_vehicle(self.vehicle1)  # COMPACT
        self.inventory.add_vehicle(self.vehicle2)  # STANDARD
        self.inventory.add_vehicle(self.vehicle3)  # PREMIUM

        compact_vehicles = self.inventory.get_available_vehicles_by_type(
            VehicleType.COMPACT
        )
        self.assertEqual(len(compact_vehicles), 1)
        self.assertIn(self.vehicle1, compact_vehicles)

        standard_vehicles = self.inventory.get_available_vehicles_by_type(
            VehicleType.STANDARD
        )
        self.assertEqual(len(standard_vehicles), 1)
        self.assertIn(self.vehicle2, standard_vehicles)

        self.vehicle3.change_status(VehicleStatus.MAINTENANCE)
        premium_vehicles = self.inventory.get_available_vehicles_by_type(
            VehicleType.PREMIUM
        )
        self.assertEqual(len(premium_vehicles), 0)

    def test_count_vehicles_by_status(self):
        """Test zliczania pojazdów według statusu"""
        self.inventory.add_vehicle(self.vehicle1)
        self.inventory.add_vehicle(self.vehicle2)
        self.inventory.add_vehicle(self.vehicle3)

        counts = self.inventory.count_vehicles_by_status()
        self.assertEqual(counts[VehicleStatus.AVAILABLE], 3)
        self.assertEqual(counts[VehicleStatus.RENTED], 0)
        self.assertEqual(counts[VehicleStatus.MAINTENANCE], 0)
        self.assertEqual(counts[VehicleStatus.OUT_OF_SERVICE], 0)

        self.vehicle1.change_status(VehicleStatus.RENTED)
        self.vehicle2.change_status(VehicleStatus.MAINTENANCE)

        counts = self.inventory.count_vehicles_by_status()
        self.assertEqual(counts[VehicleStatus.AVAILABLE], 1)
        self.assertEqual(counts[VehicleStatus.RENTED], 1)
        self.assertEqual(counts[VehicleStatus.MAINTENANCE], 1)
        self.assertEqual(counts[VehicleStatus.OUT_OF_SERVICE], 0)


if __name__ == "__main__":
    unittest.main()
