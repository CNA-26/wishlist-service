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
#### Dessa endpoints är testade med swagger och restclient och fungerar
#### Specs:
| Endpoint           | Method | Request                                      | Response                                                                    |
| ------------------ | ------ | -------------------------------------------- | --------------------------------------------------------------------------- |
| /wishlist          | POST   | `{"userId":"string","productCode":"string"}` | `{"message":"Produkt tillsatt...","userId":"string","products":["string"]}` |
| /wishlist/{userId} | GET    | -                                            | `{"userId":"string","products":["string"]}`                                 |

