# Wishlist Service
Kursprojekt för CNA26

En mikroservice byggd med FastAPI som hanterar en användares önskelista. Produktinfo hämtas från ett externt Produktregister-API och wishlist-data lagras i PostgreSQL. Alla endpoints (utom stats och hälsokontroller) kräver JWT-autentisering.

## Teknikstack
- **Python 3.10** + **FastAPI**
- **SQLAlchemy** + **PostgreSQL** (psycopg2)
- **PyJWT** – validering av JWT-tokens
- **httpx** – HTTP-anrop till Produktregister och Cart Service
- **Docker** + docker-compose
- Driftsatt på **Rahti/CSC**: https://wishlist-service-git-wishlist-service.2.rahtiapp.fi

## Komma igång

### 1. Konfigurera miljövariabler
```bash
cp .env.example .env
# Fyll i värden i .env
```

| Variabel | Beskrivning |
| --- | --- |
| `DATABASE_URL` | PostgreSQL-anslutning, t.ex. `postgresql://user:pass@host:5432/wishlist_db` |
| `JWT_SECRET` | Delad hemlighet med Auth Service (HS256) |
| `PRODUCTS_API_URL` | Bas-URL till Produktregister-API (default: `https://product-service-products-service.2.rahtiapp.fi`) |
| `PLACEHOLDER_API_KEY` | API-nyckel till Cart Service |
| `MODE` | `development` (hot-reload) eller `production` (default) |

### 2. Starta med Docker
```bash
docker-compose up --build
```
Appen lyssnar på port **8080**.

---

## Autentisering
Alla skyddade endpoints kräver ett giltigt JWT i headern:
```
Authorization: Bearer <token>
```
`user_id` hämtas automatiskt ur JWT-payloadens `sub`, `user_id` eller `id`-fält. Du behöver **inte** skicka med `userId` i request-bodyn (utom för `move-to-cart`).

Hämta en token från Auth Service:
```
POST https://user-service-cna-26-user-service.2.rahtiapp.fi/api/auth/login
```

---

## API-endpoints

### Hälsokontroller

**GET** `/`
```json
{ "message": "Wishlist service funkkar!" }
```

**GET** `/db-check`
```json
{ "message": "Databasen är ansluten!" }
```

---

### Lägg till produkt i önskelistan
**POST** `/wishlist` *(kräver JWT)*

**Request Body:**
```json
{
  "productCode": "P001"
}
```

**Response 200:**
```json
{
  "message": "Produkt tillsatt till önskelistan!",
  "userId": "42",
  "products": ["P001"]
}
```

**Response 409** – Produkten finns redan i önskelistan.

---

### Hämta önskelistan
**GET** `/wishlist` *(kräver JWT)*

Produktinfo hämtas från Produktregister-API:t.

**Response 200:**
```json
{
  "userId": "42",
  "products": [
    {
      "productCode": "P001",
      "product_name": "Monstera",
      "price": 25,
      "img": "https://...",
      "description": "En fin växt"
    }
  ]
}
```
Om Produktregister inte svarar returneras `"product_name": "Okänd produkt"` och `null` för pris/bild.

---

### Ta bort produkt från önskelistan
**DELETE** `/wishlist/{product_code}` *(kräver JWT)*

**Response 200:**
```json
{
  "message": "Produkt raderad från önskelistan.",
  "userId": "42",
  "products": []
}
```

**Response 404** – Produkten finns inte i önskelistan.

---

### Flytta produkt till kundvagnen
**POST** `/wishlist/move-to-cart` *(kräver JWT)*

Anropar Cart Service via API, tar bort produkten från önskelistan och returnerar kvarvarande produkter.

**Request Body:**
```json
{
  "userId": "42",
  "productCode": "P001"
}
```

**Response 200:**
```json
{
  "message": "Produkten flyttades till varukorgen och togs bort från önskelistan.",
  "userId": "42",
  "productCode": "P001",
  "remainingWishlist": []
}
```

**Response 403** – `userId` i bodyn matchar inte token-användaren.
**Response 404** – Produkten finns inte i önskelistan.
**Response 502** – Kunde inte nå Cart Service.

---

### Statistik (öppen endpoint)
**GET** `/wishlist/stats`

Returnerar antal användare som har varje produktkod i sin önskelista.

**Response 200:**
```json
{
  "P001": 3,
  "P002": 1
}
```

---

## Endpoints – sammanfattning

| Endpoint | Method | Auth | Beskrivning |
| --- | --- | --- | --- |
| `/` | GET | Nej | Hälsokontroll |
| `/db-check` | GET | Nej | Databaskontroll |
| `/wishlist` | POST | JWT | Lägg till produkt |
| `/wishlist` | GET | JWT | Hämta önskelistan med produktinfo |
| `/wishlist/{product_code}` | DELETE | JWT | Ta bort produkt |
| `/wishlist/move-to-cart` | POST | JWT | Flytta produkt till kundvagnen |
| `/wishlist/stats` | GET | Nej | Statistik per produktkod |

---

## Externa beroenden

| Tjänst | URL |
| --- | --- |
| Produktregister API | `https://product-service-products-service.2.rahtiapp.fi` |
| Cart Service | `https://cart-services-git-cartservices.2.rahtiapp.fi` |
| Auth Service (login) | `https://user-service-cna-26-user-service.2.rahtiapp.fi` |

---

## Databas
SQLAlchemy skapar tabellen automatiskt vid uppstart.

**Tabell:** `wishlist_items`

| Kolumn | Typ | Beskrivning |
| --- | --- | --- |
| `id` | Integer PK | Auto-incrementerat ID |
| `user_id` | String | Hämtas från JWT |
| `product_code` | String | Produktens kod |

Kombinationen `(user_id, product_code)` är unik – samma produkt kan inte läggas till två gånger.
