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
            review_date=self.today,
        )

    def test_review_initialization(self):
        """Test poprawnej inicjalizacji opinii"""
        self.assertEqual(self.review.rental_id, "RENT001")
        self.assertEqual(self.review.customer_id, "CUST001")
        self.assertEqual(self.review.rating, 4)
        self.assertEqual(
            self.review.comment,
            "Bardzo dobra obsługa i samochód w świetnym stanie.",
        )
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
        self.assertTrue(
            self.review.contains_keywords(["awaria", "obsługa", "problem"])
        )

        # Słowo kluczowe z inną wielkością liter
        self.assertTrue(self.review.contains_keywords(["OBSŁUGA"]))
        self.assertTrue(self.review.contains_keywords(["Samochód"]))

        # Słowo kluczowe nie występuje w komentarzu
        self.assertFalse(self.review.contains_keywords(["awaria"]))
        self.assertFalse(
            self.review.contains_keywords(["problem", "naprawa"])
        )

        # Pusta lista słów kluczowych
        self.assertFalse(self.review.contains_keywords([]))

    def test_str_representation(self):
        """Test reprezentacji tekstowej opinii"""
        expected_str = (f'[{self.today}] CUST001: 4/5 '
                        f'- "Bardzo dobra obsługa i samochód '
                        f'w świetnym stanie."')
        self.assertEqual(str(self.review), expected_str)

    def test_review_empty_comment(self):
        """Test inicjalizacji opinii z pustym komentarzem"""
        # Opinia z pustym komentarzem powinna być poprawnie utworzona
        empty_comment_review = Review("RENT001", "CUST001", 3, "", self.today)
        self.assertEqual(empty_comment_review.comment, "")
        self.assertEqual(empty_comment_review.rating, 3)
        self.assertEqual(empty_comment_review.rental_id, "RENT001")

    def test_review_minimum_rating(self):
        """Test opinii z minimalną dozwoloną oceną"""
        # Minimalna dozwolona ocena to 1
        min_rating_review = Review(
            "RENT001", "CUST001", 1, "Komentarz", self.today
        )
        self.assertEqual(min_rating_review.rating, 1)
        self.assertFalse(min_rating_review.is_positive())

    def test_review_with_special_characters(self):
        """Test komentarza zawierającego znaki specjalne"""
        special_char_comment = "Test ze znakami specjalnymi: !@#$%^&*()_+"
        review = Review(
            "RENT001", "CUST001", 5, special_char_comment, self.today
        )
        self.assertEqual(review.comment, special_char_comment)
        self.assertTrue(review.contains_keywords(["znakami", "specjalnymi"]))
        self.assertFalse(review.contains_keywords(["xyz", "123"]))

    def test_contains_keywords_partial_match(self):
        """Test sprawdzania częściowego dopasowania słów kluczowych"""
        review = Review(
            "RENT001",
            "CUST001",
            4,
            "Samochód był bardzo czysty i zadbany",
            self.today,
        )
        # Słowa kluczowe jako podciągi (nie pełne słowa)
        self.assertTrue(
            review.contains_keywords(["czyst"])
        )  # powinno znaleźć "czysty"
        self.assertTrue(
            review.contains_keywords(["mochód"])
        )  # powinno znaleźć "samochód"
        self.assertFalse(
            review.contains_keywords(["brudny"])
        )  # nie ma takiego podciągu

    def test_review_date_comparison(self):
        """Test porównywania dat w recenzjach"""
        yesterday = self.today - timedelta(days=1)
        tomorrow = self.today + timedelta(days=1)

        review_yesterday = Review(
            "RENT001", "CUST001", 5, "Komentarz z wczoraj", yesterday
        )
        review_today = Review(
            "RENT002", "CUST001", 4, "Komentarz z dzisiaj", self.today
        )
        review_tomorrow = Review(
            "RENT003", "CUST001", 3, "Komentarz z jutra", tomorrow
        )

        self.assertLess(
            review_yesterday.review_date, review_today.review_date
        )
        self.assertLess(review_today.review_date, review_tomorrow.review_date)
        self.assertNotEqual(
            review_yesterday.review_date, review_tomorrow.review_date
        )


if __name__ == "__main__":
    unittest.main()
