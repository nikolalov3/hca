# HCA 2.0 - Basketball Court Reservation System
## Architektura Aplikacji

### Cel Projektu
Telegram WebApp do rezerwacji hal koszykowki z TON Wallet logowaniem i dwoma schematami kolorystycznymi.

---

## 1. STRUKTURA BAZY DANYCH (SQLAlchemy + SQLite)

### users
- id (PK), telegram_id (UNIQUE), ton_wallet, name, email, balance, theme, created_at

### courts
- id (PK), name, location, address, lat, lng, surface_type, hoops, price_per_hour, image

### time_slots
- id (PK), court_id (FK), date, start_time, end_time, is_available, price

### reservations
- id (PK), user_id (FK), court_id (FK), date, start_time, end_time, status, payment_status

### transactions
- id (PK), user_id (FK), reservation_id (FK), tx_hash, amount, status (TON blockchain)

### reviews
- id (PK), user_id (FK), court_id (FK), rating, comment, created_at

---

## 2. BACKEND API ENDPOINTS

### Auth (TON Wallet)
- POST /api/auth/ton-login - Logowanie Tonkeeper
- POST /api/auth/logout
- GET /api/auth/verify

### Courts
- GET /api/courts - Lista hal
- GET /api/courts/{id}/availability - Sloty czasowe

### Reservations
- POST /api/reservations - Rezerwuj
- GET /api/reservations - Moje rezerwacje
- DELETE /api/reservations/{id} - Anuluj

### Payments
- POST /api/payments/create - Transakcja TON
- GET /api/payments/history

---

## 3. TON/TONKEEPER INTEGRATION

Flow: Frontend -> Tonkeeper SDK -> Sign Message -> Backend Verify -> JWT Token

Libs: ton-sdk, tonkeeper-api

---

## 4. SCHEMAT #1 - LIGHT (Jasny/Swiezy)
Primary: #667eea (Fioletowy)
Secondary: #48bb78 (Zielony) 
Background: #f7fafc
Text: #2d3748
Accent: #ed8936 (Pomaranczowy)

## 5. SCHEMAT #2 - DARK (Ciemny/Sportowy)
Primary: #9f7aea (Jasny fioletowy)
Secondary: #38b2ac (Turkusowy)
Background: #1a202c (Bardzo ciemny)
Text: #e2e8f0
Accent: #ed64a6 (Rozowy)
