from pydantic import BaseModel, Field
from typing import List

class ProductSize(BaseModel):
    """
    Model representing the size and quantity available for a product.
    """
    size: str = Field(..., description="Size identifier, e.g., 'S', 'M', 'L'")
    quantity: int = Field(..., ge=0, description="Quantity available for this size (must be >= 0)")

class Product(BaseModel):
    """
    Model representing a product with name, price, and available sizes.
    """
    name: str = Field(..., description="Name of the product")
    price: int = Field(..., ge=0, description="Price of the product (must be >= 0)")
    size: List[ProductSize] = Field(..., description="List of sizes with quantities available")





    