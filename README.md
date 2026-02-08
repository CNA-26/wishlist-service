# Wishlist api
Kursprojekt för CNA26

### För att lägga till en produkt i wishlist:

**POST** `/wishlist`

**Request Body:**
```json
{
  "userId": "user1",
  "productCode": "prod1"
}
```
**Response:**
```json
{
  "message": "Produkt tillsatt till önskelistan",
  "userId": "user1",
  "products": ["prod1"]
}
```
### För att hämta wishlist för en användare:

**GET** `/wishlist/{userId}`

**Response:**
```json
{
"userId": "user1",
"products": ["prod1"]
}
```
### För att flytta en produkt från wishlist till cart:

**POST** `/wishlist/{userId}/move-to-cart`

**Request Body:**
```json
{
  "productCode": "prod1",
  "quantity": 1
}
```
**Response:**
```json
{
  "message": "Produkten flyttad till kundvgnen",
  "userId": "user1",
  "moved": {
    "productCode": "prod1",
    "quantity": 1
  },
  "wishlistNow": []
}
```

#### Dessa endpoints är testade med swagger och restclient och fungerar
#### Specs:
| Endpoint                               | Method | Request                                                | Response                                                                    |
| -------------------------------------- | ------ | ------------------------------------------------------ | --------------------------------------------------------------------------- |
| /wishlist                              | POST   | `{"userId":"string","productCode":"string"}`           | `{"message":"Produkt tillsatt...","userId":"string","products":["string"]}` |
| /wishlist/{userId}                     | GET    | -                                                      | `{"userId":"string","products":["string"]}`                                 |
| /wishlist/{userId}/move-to-cart        | POST   | `{"productCode":"string","quantity":number}`           | `{"message":"Produkt flyttad...","userId":"string","moved":{...},"wishlistNow":[...]}` |

