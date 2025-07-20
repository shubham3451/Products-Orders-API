# FastAPI MongoDB Products & Orders API

A simple FastAPI application for managing products and orders using MongoDB as the database.

---

## Features

- Create and retrieve products with support for partial name search and filtering by size.
- Create orders with validation against product availability (quantity check).
- Retrieve user-specific orders with embedded product details and total price calculation.

---

## Technology Stack

- Python 3.9+
- FastAPI
- Motor (async MongoDB driver)
- Pydantic (data validation)
- MongoDB Atlas / Local MongoDB

---

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
````

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root folder with the following variables:

```env
MONGO_URI=your_mongodb_uri
MONGO_DB_NAME=your_database_name
```


Use these variables when creating your MongoDB client connection.

### 5. Run the FastAPI server

```bash
uvicorn main:app --reload
```

---

## API Endpoints

### Products

* **POST /products**

  Create a new product.

  **Request Body:**

  ```json
  {
    "name": "T-Shirt",
    "price": 299,
    "size": [
      {
        "size": "M",
        "quantity": 10
      },
      {
        "size": "L",
        "quantity": 5
      }
    ]
  }
  ```

  **Response:**

  ```json
  {
    "id": "60d5ecf1234abcd567ef9012"
  }
  ```

* **GET /products**

  Retrieve products with optional filters.

  **Query Parameters:**

  * `name` (optional): partial case-insensitive match on product name.
  * `size` (optional): filter products that have this size.
  * `limit` (optional, default=10): max results to return.
  * `offset` (optional, default=0): pagination offset.

  **Response:**

  ```json
  {
    "data": [
      {
        "id": "60d5ecf1234abcd567ef9012",
        "name": "T-Shirt",
        "price": 299
      }
    ],
    "page": {
      "next": 10,
      "limit": 1,
      "previous": 0
    }
  }
  ```

---

### Orders

* **POST /orders**

  Create an order for a user with quantity validation.

  **Request Body:**

  ```json
  {
    "user_Id": "user_1",
    "items": [
      {
        "productId": "60d5ecf1234abcd567ef9012",
        "qty": 3
      },
      {
        "productId": "60d5ecf1234abcd567ef9013",
        "qty": 1
      }
    ]
  }
  ```

  **Response:**

  ```json
  {
    "id": "60d5ee1234abcd567ef9014"
  }
  ```

  **Validation:**

  * Will raise 400 error if requested quantity exceeds available quantity (summed across sizes).
  * Will raise 404 if any productId is invalid or not found.

* **GET /orders/{user\_Id}**

  Retrieve all orders placed by a user with product details and total price.

  **Response:**

  ```json
  {
    "data": [
      {
        "Id": "60d5ee1234abcd567ef9014",
        "items": [
          {
            "productDetails": {
              "name": "T-Shirt",
              "Id": "60d5ecf1234abcd567ef9012"
            },
            "qty": 3
          }
        ],
        "Total": 897
      }
    ],
    "page": {
      "next": "10",
      "limit": 1,
      "previous": "0"
    }
  }
  ```

---

## Database Models

### Product

```json
{
  "name": "string",
  "price": "integer",
  "size": [
    {
      "size": "string",
      "quantity": "integer"
    }
  ]
}
```

### Order

```json
{
  "user_Id": "string",
  "items": [
    {
      "productId": "string",
      "qty": "integer"
    }
  ]
}
```

---

## Notes on Implementation

* Products and orders use MongoDB ObjectId for identification.
* Quantity checks ensure stock availability before order creation.
* Aggregation and `$lookup` used to join orders and products for detailed order retrieval.
* Partial and case-insensitive search is implemented using MongoDB regex.
* Pagination supported for product and order listings.

---
