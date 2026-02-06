# Wishlist api
Kursprojekt för CNA26

### För att lägga till en produkt i wishlist:

POST /wishlist
Body:
{
  "userId": "user1",
  "productCode": "prod1"
}
Svar:
{
  "message": "Product added to wishlist",
  "userId": "user1",
  "products": ["prod1"]
}

#### Specs:
| Endpoint           | Method | Request                                      | Response                                                                    |
| ------------------ | ------ | -------------------------------------------- | --------------------------------------------------------------------------- |
| /wishlist          | POST   | `{"userId":"string","productCode":"string"}` | `{"message":"Product tillsatt...","userId":"string","products":["string"]}` |
| /wishlist/{userId} | GET    | —                                            | `{"userId":"string","products":["string"]}`                                 |

