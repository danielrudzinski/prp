import unittest
from datetime import date, timedelta
from src.reviews import Review


class TestReview(unittest.TestCase):

    def setUp(self):

        self.today = date.today()
        self.review = Review(
            rental_id="RENT001",
            customer_id="CUST001",
            rating=4,
            comment="Bardzo dobra obsługa i samochód w świetnym stanie.",
            review_date=self.today
        )

    def test_review_initialization(self):
        """Test poprawnej inicjalizacji opinii"""
        self.assertEqual(self.review.rental_id, "RENT001")
        self.assertEqual(self.review.customer_id, "CUST001")
        self.assertEqual(self.review.rating, 4)
        self.assertEqual(self.review.comment, "Bardzo dobra obsługa i samochód w świetnym stanie.")
        self.assertEqual(self.review.review_date, self.today)

    def test_review_initialization_invalid_data(self):
        """Test inicjalizacji opinii z niepoprawnymi danymi"""
        # Niepoprawna ocena - poniżej zakresu
        with self.assertRaises(ValueError):
            Review("RENT001", "CUST001", 0, "Komentarz", self.today)

        # Niepoprawna ocena - powyżej zakresu
        with self.assertRaises(ValueError):
            Review("RENT001", "CUST001", 6, "Komentarz", self.today)

        # Puste ID wypożyczenia
        with self.assertRaises(ValueError):
            Review("", "CUST001", 4, "Komentarz", self.today)

        # Puste ID klienta
        with self.assertRaises(ValueError):
            Review("RENT001", "", 4, "Komentarz", self.today)

    def test_is_positive(self):
        """Test sprawdzania czy opinia jest pozytywna"""
        # Opinia z oceną 4 - pozytywna
        self.assertTrue(self.review.is_positive())

        # Opinia z oceną 5 - pozytywna
        review_5 = Review("RENT001", "CUST001", 5, "Komentarz", self.today)
        self.assertTrue(review_5.is_positive())

        # Opinia z oceną 3 - niepozytywna
        review_3 = Review("RENT001", "CUST001", 3, "Komentarz", self.today)
        self.assertFalse(review_3.is_positive())

        # Opinia z oceną 1 - niepozytywna
        review_1 = Review("RENT001", "CUST001", 1, "Komentarz", self.today)
        self.assertFalse(review_1.is_positive())

    def test_contains_keywords(self):
        """Test sprawdzania czy komentarz zawiera słowa kluczowe"""
        # Słowo kluczowe występuje w komentarzu
        self.assertTrue(self.review.contains_keywords(["dobra"]))
        self.assertTrue(self.review.contains_keywords(["samochód"]))

        # Kilka słów kluczowych, jedno występuje
        self.assertTrue(self.review.contains_keywords(["awaria", "obsługa", "problem"]))

        # Słowo kluczowe z inną wielkością liter
        self.assertTrue(self.review.contains_keywords(["OBSŁUGA"]))
        self.assertTrue(self.review.contains_keywords(["Samochód"]))

        # Słowo kluczowe nie występuje w komentarzu
        self.assertFalse(self.review.contains_keywords(["awaria"]))
        self.assertFalse(self.review.contains_keywords(["problem", "naprawa"]))

        # Pusta lista słów kluczowych
        self.assertFalse(self.review.contains_keywords([]))

    def test_str_representation(self):
        """Test reprezentacji tekstowej opinii"""
        expected_str = f"[{self.today}] CUST001: 4/5 - \"Bardzo dobra obsługa i samochód w świetnym stanie.\""
        self.assertEqual(str(self.review), expected_str)


class TestReviewIntegration(unittest.TestCase):
    """Testy integracyjne dla klasy Review z RentalManager"""

    def setUp(self):
        """Ustawienie danych testowych"""
        from src.rental import RentalManager
        from src.customers import Customer, DrivingLicense
        from src.vehicles import Vehicle, VehicleType

        self.today = date.today()
        self.manager = RentalManager()

        # Tworzenie licencji
        self.license = DrivingLicense(
            license_number="ABC123456",
            issue_date=self.today - timedelta(days=365),
            expiry_date=self.today + timedelta(days=365),
            categories=["B"]
        )

        # Tworzenie klienta
        self.customer = Customer(
            customer_id="CUST001",
            first_name="Jan",
            last_name="Kowalski",
            email="jan.kowalski@example.com",
            phone="123456789",
            address="ul. Przykładowa 1, Warszawa",
            driving_license=self.license
        )


        self.vehicle = Vehicle(
            vehicle_id="VEH001",
            make="Toyota",
            model="Corolla",
            year=2020,
            registration_number="WA12345",
            daily_rate=150.0,
            vehicle_type=VehicleType.COMPACT
        )

    def test_add_review_to_rental(self):

        rental = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3)
        )


        self.manager.complete_rental(rental.rental_id, self.today + timedelta(days=3))

        # Dodanie opinii
        review = self.manager.add_review(
            rental_id=rental.rental_id,
            rating=5,
            comment="Świetne auto, polecam!",
            review_date=self.today + timedelta(days=4)
        )


        customer_reviews = self.manager.get_reviews_for_customer(self.customer.customer_id)
        self.assertEqual(len(customer_reviews), 1)
        self.assertEqual(customer_reviews[0], review)


        avg_rating = self.manager.get_average_rating_for_customer(self.customer.customer_id)
        self.assertEqual(avg_rating, 5.0)

    def test_add_multiple_reviews(self):

        rental1 = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today,
            end_date=self.today + timedelta(days=3)
        )


        self.manager.complete_rental(rental1.rental_id, self.today + timedelta(days=3))


        rental2 = self.manager.create_rental(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date=self.today + timedelta(days=4),
            end_date=self.today + timedelta(days=7)
        )


        self.manager.complete_rental(rental2.rental_id, self.today + timedelta(days=7))


        review1 = self.manager.add_review(
            rental_id=rental1.rental_id,
            rating=5,
            comment="Świetne auto, polecam!",
            review_date=self.today + timedelta(days=4)
        )


        review2 = self.manager.add_review(
            rental_id=rental2.rental_id,
            rating=3,
            comment="Tym razem auto miało drobne problemy.",
            review_date=self.today + timedelta(days=8)
        )


        customer_reviews = self.manager.get_reviews_for_customer(self.customer.customer_id)
        self.assertEqual(len(customer_reviews), 2)
        self.assertIn(review1, customer_reviews)
        self.assertIn(review2, customer_reviews)


        avg_rating = self.manager.get_average_rating_for_customer(self.customer.customer_id)
        self.assertEqual(avg_rating, 4.0)

    def test_add_review_for_nonexistent_rental(self):
        """Test dodawania opinii dla nieistniejącego wypożyczenia"""
        from src.rental import RentalException

        with self.assertRaises(RentalException):
            self.manager.add_review(
                rental_id="NIEISTNIEJACE",
                rating=5,
                comment="Komentarz",
                review_date=self.today
            )

    def test_get_reviews_for_nonexistent_customer(self):
        """Test pobierania opinii dla nieistniejącego klienta"""
        reviews = self.manager.get_reviews_for_customer("NIEISTNIEJACY")
        self.assertEqual(len(reviews), 0)

    def test_get_average_rating_for_customer_with_no_reviews(self):
        """Test pobierania średniej oceny dla klienta bez opinii"""
        avg_rating = self.manager.get_average_rating_for_customer(self.customer.customer_id)
        self.assertEqual(avg_rating, 0.0)


def test_review_with_empty_comment(self):
    """Test tworzenia opinii z pustym komentarzem"""
    review = Review(
        rental_id="RENT001",
        customer_id="CUST001",
        rating=3,
        comment="",
        review_date=date.today()
    )

    self.assertFalse(review.is_positive())
    self.assertEqual(review.comment, "")


def test_review_with_boundary_ratings(self):
    """Test opinii z granicznymi ocenami"""
    today = date.today()


    review_min = Review(
        rental_id="RENT001",
        customer_id="CUST001",
        rating=1,
        comment="Bardzo słabo",
        review_date=today
    )

    self.assertFalse(review_min.is_positive())


    review_max = Review(
        rental_id="RENT001",
        customer_id="CUST001",
        rating=5,
        comment="Doskonale",
        review_date=today
    )

    self.assertTrue(review_max.is_positive())

    # Próba utworzenia opinii z oceną poza zakresem
    with self.assertRaises(ValueError):
        Review(
            rental_id="RENT001",
            customer_id="CUST001",
            rating=0,  # Poniżej minimalnej
            comment="Komentarz",
            review_date=today
        )

    with self.assertRaises(ValueError):
        Review(
            rental_id="RENT001",
            customer_id="CUST001",
            rating=6,  # Powyżej maksymalnej
            comment="Komentarz",
            review_date=today
        )


def test_review_with_empty_comment(self):
    """Test tworzenia opinii z pustym komentarzem"""
    review = Review(
        rental_id="RENT001",
        customer_id="CUST001",
        rating=3,
        comment="",
        review_date=date.today()
    )

    self.assertFalse(review.is_positive())
    self.assertEqual(review.comment, "")


def test_review_with_boundary_ratings(self):
    """Test opinii z granicznymi ocenami"""
    today = date.today()

    # Minimalna ocena (1)
    review_min = Review(
        rental_id="RENT001",
        customer_id="CUST001",
        rating=1,
        comment="Bardzo słabo",
        review_date=today
    )

    self.assertFalse(review_min.is_positive())

    # Maksymalna ocena (5)
    review_max = Review(
        rental_id="RENT001",
        customer_id="CUST001",
        rating=5,
        comment="Doskonale",
        review_date=today
    )

    self.assertTrue(review_max.is_positive())

    # Próba utworzenia opinii z oceną poza zakresem
    with self.assertRaises(ValueError):
        Review(
            rental_id="RENT001",
            customer_id="CUST001",
            rating=0,  # Poniżej minimalnej
            comment="Komentarz",
            review_date=today
        )

    with self.assertRaises(ValueError):
        Review(
            rental_id="RENT001",
            customer_id="CUST001",
            rating=6,  # Powyżej maksymalnej
            comment="Komentarz",
            review_date=today
        )


if __name__ == '__main__':
    unittest.main()
