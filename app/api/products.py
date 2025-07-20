from fastapi import APIRouter, HTTPException, status, Query
from ..schemas.products import Product
from ..core.database import db
from pymongo.errors import PyMongoError
from typing import Optional

router = APIRouter()

@router.post('/products', 
             status_code=status.HTTP_201_CREATED,
             summary="Create a new product",
             description="""
            This endpoint creates a new product in the database.
    
            Request body must include:
            - `name`: Name of the product
            - `price`: Price of the product
            - `size`: A list of sizes, each with a size label and quantity available
            
            Returns the inserted product ID.
            """)
async def create_product(product: Product):
   try:
     
     data = product.model_dump()
     product_data = await db.products.insert_one(data)
     return {"id": str(product_data.inserted_id)}
   
   except PyMongoError:
      raise HTTPException(
         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
         detail="failed to insert in database")
   
   except Exception:
      raise HTTPException(
         status_code=status.HTTP_400_BAD_REQUEST, 
         detail="Internal server error")
      




@router.get("/products",
            status_code=status.HTTP_200_OK,
            summary="Get list of products",
            description="""
            Returns a paginated list of products. Supports optional filters:
            
            - `name`: Partial or full name search (case-insensitive)
            - `size`: Filter by available product size
            - `limit`: Number of results to return (default: 10, max: 100)
            - `offset`: Number of results to skip (default: 0)
            
            Each product includes:
            - `id`
            - `name`
            - `price`
            
            Sizes are not included in the response.
            """)
async def get_product(
   name: Optional[str] = Query(None, description="Text search on name"),
   size: Optional[str] = Query(None, description="Filter by size "),
   limit: int = Query(10, ge=1, le=100),
   offset: int = Query(0, ge=0)
):
   try:
      query = {}
      if name:
         query["name"] = {"$regex": name, "$options": "i"}

      if size:
         query["size.size"] = size

      cursor = (
         db.products.find(query, {"name":1, "price":1})
         .sort("_id",1)
         .skip(offset)
         .limit(limit))
      
      products = []
      async for doc in cursor:
         products.append({
                "id": str(doc["_id"]),
                "name": doc.get("name"),
                "price": doc.get("price")
            })
      response = {
         "data":products,
         "page":{
            "next": offset + limit,
            "limit": len(products),
            "previous": max(offset - limit, 0)
         }
      }

      return response
   
   except Exception:
      raise HTTPException(
         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
         detail="Error fetching data")
      


