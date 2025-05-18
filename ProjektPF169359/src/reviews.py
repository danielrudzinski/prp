from datetime import date


class Review:
    def __init__(
        self,
        rental_id: str,
        customer_id: str,
        rating: int,
        comment: str,
        review_date: date,
    ):
        if not (1 <= rating <= 5):
            raise ValueError("Ocena musi być w zakresie 1–5")
        if not rental_id or not customer_id:
            raise ValueError("ID wypożyczenia i klienta nie mogą być puste")

        self.rental_id = rental_id
        self.customer_id = customer_id
        self.rating = rating
        self.comment = comment
        self.review_date = review_date

    def is_positive(self) -> bool:
        """Czy opinia jest pozytywna (ocena 4 lub 5)."""
        return self.rating >= 4

    def contains_keywords(self, keywords: list[str]) -> bool:
        """Czy komentarz zawiera jedno z podanych słów kluczowych."""
        comment_lower = self.comment.lower()
        return any(keyword.lower() in comment_lower for keyword in keywords)

    def __str__(self) -> str:
        return (f'[{self.review_date}] {self.customer_id}: '
                f'{self.rating}/5 - "{self.comment}"')
