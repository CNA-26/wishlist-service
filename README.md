# Wishlist api
Kursprojekt för CNA26

## Testdata (Hårdkodat produktregister)
För att testa kopplingen och se hur bilder och priser hämtas, använd följande produktkoder i dina anrop:
* `P001` - Monstera (25€)
* `P002` - Alocasia (59€)
* `P003` - Strelitzia (139€)

### För att lägga till en produkt i wishlist:

**POST** `/wishlist`

**Request Body:**
```json
{
  "userId": "user1",
  "productCode": "P001"
}
```
**Response:**
```json
{
  "message": "Produkt tillsatt till önskelistan",
  "userId": "user1",
  "products": ["P001"]
}
```
### För att hämta wishlist för en användare:

**GET** `/wishlist/{userId}`

**Response:**
```json
{
  "userId": "user1",
  "products": [
    {
      "productCode": "P100",
      "name": "Monstera",
      "pris": 25,
      "image": "https://placehold.co/500x500?text=Strelitzia"
    }
  ]
}
```
### För att flytta en produkt från wishlist till cart:

**POST** `/wishlist/{userId}/move-to-cart`

**Request Body:**
```json
{
  "productCode": "P001",
  "quantity": 1
}
```
**Response:**
```json
{
  "message": "Produkten flyttad till kundvagnen",
  "userId": "user1",
  "moved": {
    "productCode": "P001",
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

