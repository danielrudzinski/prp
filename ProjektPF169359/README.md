
# 🚗 Vehicle Rental System

**Vehicle Rental System** to modułowy system napisany w Pythonie do zarządzania wypożyczalnią pojazdów. Umożliwia rejestrację klientów, dodawanie pojazdów, obsługę wypożyczeń i zarządzanie opiniami.

## 📦 Funkcje

- Zarządzanie klientami i prawami jazdy
- Obsługa pojazdów, ich dostępności i konserwacji
- Tworzenie, anulowanie i kończenie wypożyczeń
- Uwzględnianie rabatów w zależności od kategorii klienta
- Dodawanie i analizowanie opinii klientów
- Pełne pokrycie testami jednostkowymi (`unittest`)

## 🧾 Wymagania

- Python 3.8 lub nowszy
- Brak zewnętrznych bibliotek — projekt opiera się wyłącznie na standardowej bibliotece Pythona

## ▶️ Uruchomienie

1. Sklonuj repozytorium:

   ```bash
   git clone https://github.com/danielrudzinski/ProjektPF169359.git
   ProjektPF169359
   ```

2. Uruchom skrypt demonstracyjny:

   ```bash
   python main.py
   ```

   Skrypt `main.py` pokazuje pełny przepływ: tworzenie klientów, pojazdów, wypożyczeń, dodawanie opinii itp.

## 🧪 Testy

Wszystkie testy znajdują się w plikach `test_*.py` i są oparte o `unittest`.

Aby uruchomić wszystkie testy:

```bash
python -m unittest discover .
```

Lub pojedynczy zestaw testów, np.:

```bash
python test_rental.py
```

## 📁 Struktura

```
ProjektPF169359/
├── src/
│   ├── __init__.py
│   ├── customers.py      # Obsługa klientów
│   ├── vehicles.py       # Pojazdy i inwentarz
│   ├── rental.py         # Wypożyczenia
│   ├── reviews.py        # Opinie
│   └── main.py           # Demo aplikacji
│
├── tests/
│   ├── __init__.py
│   ├── test_customers.py
│   ├── test_vehicles.py
│   ├── test_rental.py
│   └── test_reviews.py

```

## 🔧 Przykład działania

Fragment z `main.py`:

```python
customer = Customer(
    customer_id="CUST001",
    first_name="Jan",
    last_name="Kowalski",
    email="jan.kowalski@example.com",
    phone="123456789",
    address="ul. Przykładowa 1, Warszawa",
    driving_license=license1
)
vehicle = Car(
    vehicle_id="CAR001",
    make="Toyota",
    model="Corolla",
    year=2020,
    registration_number="WA12345",
    daily_rate=150.0,
    vehicle_type=VehicleType.COMPACT,
    doors=5,
    fuel_type="Benzyna",
    transmission="Manualna"
)
rental = rental_manager.create_rental(customer, vehicle, start_date, end_date)
```

## 🧑‍💻 Autor
Daniel Rudziński
Projekt stworzony do celów edukacyjnych na Przedmiot Fakultatywny.
Projekt częściowo generowany przy użyciu claude.ai z użyciem Claude 3.7

---
