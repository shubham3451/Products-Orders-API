from pydantic import BaseModel, Field
from typing import List

class OrderItems(BaseModel):
    """
    Represents a single item in an order.
    
    Attributes:
        productId (str): The ID of the product being ordered.
        qty (int): The quantity of the product ordered. Must be zero or greater.
    """
    productId: str = Field(..., description="The ID of the product")
    qty: int = Field(..., gt=0, description="Quantity of the product, minimum 0")

class Order(BaseModel):
    """
    Represents a complete order from a user.
    
    Attributes:
        user_Id (str): The ID of the user placing the order.
        items (List[OrderItems]): List of products and quantities in the order.
    """
    user_Id: str = Field(..., description="User ID placing the order")
    items: List[OrderItems] = Field(..., description="List of order items")



