import unittest
from unittest.mock import Mock
from datetime import date, timedelta
from src.customers import Customer, CustomerRegistry, CustomerCategory, DrivingLicense


class TestDrivingLicense(unittest.TestCase):

    def setUp(self):
        """Ustawienie danych testowych"""
        self.today = date.today()
        self.license = DrivingLicense(
            license_number="ABC123456",
            issue_date=self.today - timedelta(days=365),
            expiry_date=self.today + timedelta(days=365),
            categories=["B", "C"],
        )

    def test_license_initialization(self):
        """Test poprawnej inicjalizacji prawa jazdy"""
        self.assertEqual(self.license.license_number, "ABC123456")
        self.assertEqual(self.license.issue_date, self.today - timedelta(days=365))
        self.assertEqual(self.license.expiry_date, self.today + timedelta(days=365))
        self.assertEqual(self.license.categories, ["B", "C"])

    def test_license_initialization_invalid_data(self):
        """Test inicjalizacji prawa jazdy z niepoprawnymi danymi"""
        # Pusty numer prawa jazdy
        with self.assertRaises(ValueError):
            DrivingLicense("", self.today, self.today + timedelta(days=365), ["B"])

        # Niepoprawny typ daty wydania
        with self.assertRaises(ValueError):
            DrivingLicense(
                "ABC123456", "niepoprawna_data", self.today + timedelta(days=365), ["B"]
            )

        # Niepoprawny typ daty ważności
        with self.assertRaises(ValueError):
            DrivingLicense("ABC123456", self.today, "niepoprawna_data", ["B"])

        # Data wydania późniejsza niż data ważności
        with self.assertRaises(ValueError):
            DrivingLicense(
                "ABC123456", self.today + timedelta(days=10), self.today, ["B"]
            )

        # Niepoprawny typ listy kategorii
        with self.assertRaises(ValueError):
            DrivingLicense(
                "ABC123456", self.today, self.today + timedelta(days=365), "B"
            )

        # Lista zawierająca elementy niebędące stringami
        with self.assertRaises(ValueError):
            DrivingLicense(
                "ABC123456", self.today, self.today + timedelta(days=365), ["B", 1]
            )

    def test_is_valid(self):
        """Test sprawdzania ważności prawa jazdy"""
        # Prawo jazdy ważne w dniu dzisiejszym
        self.assertTrue(self.license.is_valid())

        # Prawo jazdy ważne w określonym dniu (przed wygaśnięciem)
        check_date = self.today + timedelta(days=360)
        self.assertTrue(self.license.is_valid(check_date))

        # Prawo jazdy nieważne w określonym dniu (po wygaśnięciu)
        check_date = self.today + timedelta(days=366)
        self.assertFalse(self.license.is_valid(check_date))

        # Niepoprawny typ daty sprawdzenia
        with self.assertRaises(ValueError):
            self.license.is_valid("niepoprawna_data")

    def test_has_category(self):
        """Test sprawdzania posiadania kategorii prawa jazdy"""
        self.assertTrue(self.license.has_category("B"))
        self.assertTrue(self.license.has_category("C"))
        self.assertFalse(self.license.has_category("D"))

        # Niepoprawny typ kategorii
        with self.assertRaises(ValueError):
            self.license.has_category("")

        with self.assertRaises(ValueError):
            self.license.has_category(123)


class TestCustomer(unittest.TestCase):
    """Testy dla klasy Customer"""

    def setUp(self):
        """Ustawienie danych testowych"""
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

    def test_customer_initialization(self):
        """Test poprawnej inicjalizacji klienta"""
        self.assertEqual(self.customer.customer_id, "CUST001")
        self.assertEqual(self.customer.first_name, "Jan")
        self.assertEqual(self.customer.last_name, "Kowalski")
        self.assertEqual(self.customer.email, "jan.kowalski@example.com")
        self.assertEqual(self.customer.phone, "123456789")
        self.assertEqual(self.customer.address, "ul. Przykładowa 1, Warszawa")
        self.assertEqual(self.customer.driving_license, self.license)
        self.assertEqual(self.customer.category, CustomerCategory.STANDARD)
        self.assertEqual(self.customer.rental_history, [])
        self.assertIsInstance(self.customer.registration_date, date)

    def test_customer_initialization_invalid_data(self):
        """Test inicjalizacji klienta z niepoprawnymi danymi"""
        # Pusty identyfikator klienta
        with self.assertRaises(ValueError):
            Customer(
                "",
                "Jan",
                "Kowalski",
                "jan.kowalski@example.com",
                "123456789",
                "ul. Przykładowa 1, Warszawa",
                self.license,
            )

        # Puste imię
        with self.assertRaises(ValueError):
            Customer(
                "CUST001",
                "",
                "Kowalski",
                "jan.kowalski@example.com",
                "123456789",
                "ul. Przykładowa 1, Warszawa",
                self.license,
            )

        # Puste nazwisko
        with self.assertRaises(ValueError):
            Customer(
                "CUST001",
                "Jan",
                "",
                "jan.kowalski@example.com",
                "123456789",
                "ul. Przykładowa 1, Warszawa",
                self.license,
            )

        # Pusty e-mail
        with self.assertRaises(ValueError):
            Customer(
                "CUST001",
                "Jan",
                "Kowalski",
                "",
                "123456789",
                "ul. Przykładowa 1, Warszawa",
                self.license,
            )

        # Pusty numer telefonu
        with self.assertRaises(ValueError):
            Customer(
                "CUST001",
                "Jan",
                "Kowalski",
                "jan.kowalski@example.com",
                "",
                "ul. Przykładowa 1, Warszawa",
                self.license,
            )

        # Pusty adres
        with self.assertRaises(ValueError):
            Customer(
                "CUST001",
                "Jan",
                "Kowalski",
                "jan.kowalski@example.com",
                "123456789",
                "",
                self.license,
            )

        # Niepoprawny obiekt prawa jazdy
        with self.assertRaises(ValueError):
            Customer(
                "CUST001",
                "Jan",
                "Kowalski",
                "jan.kowalski@example.com",
                "123456789",
                "ul. Przykładowa 1, Warszawa",
                "niepoprawne_prawo_jazdy",
            )

    def test_customer_str_representation(self):
        """Test reprezentacji tekstowej klienta"""
        expected_str = "Jan Kowalski (ID: CUST001)"
        self.assertEqual(str(self.customer), expected_str)

    def test_full_name(self):
        """Test metody full_name"""
        self.assertEqual(self.customer.full_name(), "Jan Kowalski")

    def test_can_rent(self):
        """Test sprawdzania możliwości wypożyczenia pojazdu"""
        # Prawo jazdy ważne
        self.assertTrue(self.customer.can_rent())

        # Mockowanie metody is_valid z DrivingLicense do zwracania False
        self.customer.driving_license.is_valid = Mock(return_value=False)
        self.assertFalse(self.customer.can_rent())

    def test_upgrade_category(self):
        """Test aktualizacji kategorii klienta"""
        self.assertEqual(self.customer.category, CustomerCategory.STANDARD)

        self.customer.upgrade_category(CustomerCategory.SILVER)
        self.assertEqual(self.customer.category, CustomerCategory.SILVER)

        self.customer.upgrade_category(CustomerCategory.GOLD)
        self.assertEqual(self.customer.category, CustomerCategory.GOLD)

        self.customer.upgrade_category(CustomerCategory.PLATINUM)
        self.assertEqual(self.customer.category, CustomerCategory.PLATINUM)

        # Niepoprawny typ kategorii
        with self.assertRaises(ValueError):
            self.customer.upgrade_category("silver")

    def test_add_rental_to_history(self):
        """Test dodawania wypożyczenia do historii klienta"""
        self.assertEqual(len(self.customer.rental_history), 0)

        self.customer.add_rental_to_history("RENT001")
        self.assertEqual(len(self.customer.rental_history), 1)
        self.assertEqual(self.customer.rental_history[0], "RENT001")

        self.customer.add_rental_to_history("RENT002")
        self.assertEqual(len(self.customer.rental_history), 2)
        self.assertEqual(self.customer.rental_history[1], "RENT002")

        # Niepoprawny identyfikator wypożyczenia
        with self.assertRaises(ValueError):
            self.customer.add_rental_to_history("")

        with self.assertRaises(ValueError):
            self.customer.add_rental_to_history(123)


class TestCustomerRegistry(unittest.TestCase):
    """Testy dla klasy CustomerRegistry"""

    def setUp(self):
        """Ustawienie danych testowych"""
        self.registry = CustomerRegistry()
        self.today = date.today()

        # Tworzenie pierwszego klienta
        self.license1 = DrivingLicense(
            license_number="ABC123456",
            issue_date=self.today - timedelta(days=365),
            expiry_date=self.today + timedelta(days=365),
            categories=["B", "C"],
        )
        self.customer1 = Customer(
            customer_id="CUST001",
            first_name="Jan",
            last_name="Kowalski",
            email="jan.kowalski@example.com",
            phone="123456789",
            address="ul. Przykładowa 1, Warszawa",
            driving_license=self.license1,
        )

        # Tworzenie drugiego klienta
        self.license2 = DrivingLicense(
            license_number="DEF789012",
            issue_date=self.today - timedelta(days=730),
            expiry_date=self.today + timedelta(days=730),
            categories=["B"],
        )
        self.customer2 = Customer(
            customer_id="CUST002",
            first_name="Anna",
            last_name="Nowak",
            email="anna.nowak@example.com",
            phone="987654321",
            address="ul. Kwiatowa 2, Kraków",
            driving_license=self.license2,
        )

        # Tworzenie trzeciego klienta o tym samym nazwisku
        self.license3 = DrivingLicense(
            license_number="GHI345678",
            issue_date=self.today - timedelta(days=500),
            expiry_date=self.today + timedelta(days=500),
            categories=["B", "D"],
        )
        self.customer3 = Customer(
            customer_id="CUST003",
            first_name="Adam",
            last_name="Kowalski",
            email="adam.kowalski@example.com",
            phone="456789123",
            address="ul. Leśna 3, Gdańsk",
            driving_license=self.license3,
        )

    def test_register_customer(self):
        """Test rejestracji klienta"""
        self.assertEqual(len(self.registry.customers), 0)

        self.registry.register_customer(self.customer1)
        self.assertEqual(len(self.registry.customers), 1)
        self.assertIn("CUST001", self.registry.customers)

        self.registry.register_customer(self.customer2)
        self.assertEqual(len(self.registry.customers), 2)
        self.assertIn("CUST002", self.registry.customers)

    def test_register_invalid_customer(self):
        """Test rejestracji niepoprawnego obiektu jako klienta"""
        with self.assertRaises(TypeError):
            self.registry.register_customer("nie_klient")

    def test_register_duplicate_customer(self):
        """Test rejestracji klienta z istniejącym ID"""
        self.registry.register_customer(self.customer1)

        with self.assertRaises(ValueError):
            self.registry.register_customer(self.customer1)

    def test_remove_customer(self):
        """Test usuwania klienta z rejestru"""
        self.registry.register_customer(self.customer1)
        self.registry.register_customer(self.customer2)
        self.assertEqual(len(self.registry.customers), 2)

        self.registry.remove_customer("CUST001")
        self.assertEqual(len(self.registry.customers), 1)
        self.assertNotIn("CUST001", self.registry.customers)
        self.assertIn("CUST002", self.registry.customers)

    def test_remove_nonexistent_customer(self):
        """Test usuwania nieistniejącego klienta"""
        with self.assertRaises(ValueError):
            self.registry.remove_customer("NIEISTNIEJACY")

    def test_get_customer(self):
        """Test pobierania klienta z rejestru"""
        self.registry.register_customer(self.customer1)
        self.registry.register_customer(self.customer2)

        customer = self.registry.get_customer("CUST001")
        self.assertEqual(customer, self.customer1)

        customer = self.registry.get_customer("CUST002")
        self.assertEqual(customer, self.customer2)

        customer = self.registry.get_customer("NIEISTNIEJACY")
        self.assertIsNone(customer)

    def test_find_customers_by_last_name(self):
        """Test wyszukiwania klientów po nazwisku"""
        self.registry.register_customer(self.customer1)
        self.registry.register_customer(self.customer2)
        self.registry.register_customer(self.customer3)

        kowalski_customers = self.registry.find_customers_by_last_name("Kowalski")
        self.assertEqual(len(kowalski_customers), 2)
        self.assertIn(self.customer1, kowalski_customers)
        self.assertIn(self.customer3, kowalski_customers)
        self.assertNotIn(self.customer2, kowalski_customers)

        nowak_customers = self.registry.find_customers_by_last_name("Nowak")
        self.assertEqual(len(nowak_customers), 1)
        self.assertIn(self.customer2, nowak_customers)

        # Sprawdzenie case insensitive
        kowalski_lower = self.registry.find_customers_by_last_name("kowalski")
        self.assertEqual(len(kowalski_lower), 2)
        self.assertIn(self.customer1, kowalski_lower)
        self.assertIn(self.customer3, kowalski_lower)

        # Nieistniejące nazwisko
        nieistniejacy = self.registry.find_customers_by_last_name("Nieistniejący")
        self.assertEqual(len(nieistniejacy), 0)

    def test_get_customers_by_category(self):
        """Test pobierania klientów według kategorii"""
        self.registry.register_customer(self.customer1)
        self.registry.register_customer(self.customer2)
        self.registry.register_customer(self.customer3)

        # Wszyscy klienci są początkowo w kategorii STANDARD
        standard_customers = self.registry.get_customers_by_category(
            CustomerCategory.STANDARD
        )
        self.assertEqual(len(standard_customers), 3)

        # Zmieńmy kategorię jednego klienta
        self.customer2.upgrade_category(CustomerCategory.GOLD)

        standard_customers = self.registry.get_customers_by_category(
            CustomerCategory.STANDARD
        )
        self.assertEqual(len(standard_customers), 2)
        self.assertIn(self.customer1, standard_customers)
        self.assertIn(self.customer3, standard_customers)
        self.assertNotIn(self.customer2, standard_customers)

        gold_customers = self.registry.get_customers_by_category(CustomerCategory.GOLD)
        self.assertEqual(len(gold_customers), 1)
        self.assertIn(self.customer2, gold_customers)

        # Nieistniejąca kategoria
        with self.assertRaises(ValueError):
            self.registry.get_customers_by_category("gold")

    def test_count_customers(self):
        """Test liczenia klientów w rejestrze"""
        self.assertEqual(self.registry.count_customers(), 0)

        self.registry.register_customer(self.customer1)
        self.assertEqual(self.registry.count_customers(), 1)

        self.registry.register_customer(self.customer2)
        self.assertEqual(self.registry.count_customers(), 2)

        self.registry.register_customer(self.customer3)
        self.assertEqual(self.registry.count_customers(), 3)

        self.registry.remove_customer("CUST001")
        self.assertEqual(self.registry.count_customers(), 2)


def test_upgrade_category_to_same_level(self):
    """Test aktualizacji kategorii klienta do tego samego poziomu"""
    self.assertEqual(self.customer.category, CustomerCategory.STANDARD)

    # Aktualizacja do tej samej kategorii
    self.customer.upgrade_category(CustomerCategory.STANDARD)
    self.assertEqual(self.customer.category, CustomerCategory.STANDARD)


def test_driving_license_with_boundary_dates(self):
    """Test prawa jazdy z granicznymi datami"""
    today = date.today()

    # Prawo jazdy wydane i wygasające tego samego dnia
    with self.assertRaises(ValueError):
        DrivingLicense(
            license_number="TEST123",
            issue_date=today,
            expiry_date=today - timedelta(days=1),
            categories=["B"],
        )

    # Prawo jazdy wydane i wygasające tego samego dnia (powinno być ważne)
    license_same_day = DrivingLicense(
        license_number="TEST123", issue_date=today, expiry_date=today, categories=["B"]
    )

    self.assertTrue(license_same_day.is_valid())


def test_upgrade_category_to_same_level(self):
    """Test aktualizacji kategorii klienta do tego samego poziomu"""
    self.assertEqual(self.customer.category, CustomerCategory.STANDARD)

    # Aktualizacja do tej samej kategorii
    self.customer.upgrade_category(CustomerCategory.STANDARD)
    self.assertEqual(self.customer.category, CustomerCategory.STANDARD)


def test_driving_license_with_boundary_dates(self):
    """Test prawa jazdy z granicznymi datami"""
    today = date.today()

    # Prawo jazdy wydane i wygasające tego samego dnia
    with self.assertRaises(ValueError):
        DrivingLicense(
            license_number="TEST123",
            issue_date=today,
            expiry_date=today - timedelta(days=1),
            categories=["B"],
        )

    # Prawo jazdy wydane i wygasające tego samego dnia (powinno być ważne)
    license_same_day = DrivingLicense(
        license_number="TEST123", issue_date=today, expiry_date=today, categories=["B"]
    )

    self.assertTrue(license_same_day.is_valid())


if __name__ == "__main__":
    unittest.main()
