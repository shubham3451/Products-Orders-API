from fastapi import APIRouter, HTTPException, status, Query
from ..schemas.orders import Order
from ..core.database import db
from bson import ObjectId
from pymongo.errors import PyMongoError

router = APIRouter()

@router.post("/orders",
             status_code=status.HTTP_201_CREATED,
             summary="Create a new order",
             description="""
             Creates a new order for a user with one or more product items.
             
             Validates that:
             - All product IDs are valid and exist in the database
             - The total quantity requested is available across all sizes
             
             Request body must include:
             - `user_Id`: ID of the user placing the order
             - `items`: List of products with productId and qty
             
             Returns the inserted order ID if successful.
             """)
async def create_orders(order:Order):
    try:
        product_ids = []
        for item in order.items:
            try:
              product_ids.append(ObjectId(item.productId))
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"Invalid productId :{item.productId}")
            
        products_cursor = db.products.find({"_id": {"$in": product_ids}})
        product_map = {}
        async for product in products_cursor:
            product_map[product["_id"]] = product

        if len(product_map) != len(product_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more products not found"
            )

        for item in order.items:
            product = product_map.get(ObjectId(item.productId))
            available_qty = sum(size["quantity"] for size in product.get("size", []))
            if item.qty > available_qty:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Only {available_qty} items available for product {item.productId}"
                )
            

        data = {
            "user_Id":order.user_Id,
            "items":[
                {
                    "productId": ObjectId(item.productId),
                    "qty": item.qty
                }for item in order.items
            ]
        }
        order_data = await db.orders.insert_one(data)

        return {"id": str(order_data.inserted_id)}
    
    except HTTPException as e:
        raise e
    
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
              detail="failed to save data in database")
    
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error")
    


@router.get("/orders/{user_Id}",
             status_code=status.HTTP_200_OK,
             summary="Fetch user orders",
             description="""
             Returns a list of orders placed by a specific user.
         
             Supports pagination using:
             - `limit`: Number of records to return (default: 10)
             - `offset`: Records to skip (for pagination)
         
             Each order contains:
             - `Id`: Order ID
             - `items`: List of items with product details and quantity
             - `Total`: Total price of the order
             """)
async def get_orders(
    user_Id: str,
    limit: int = Query(10, ge=0, le=100),
    offset: int = Query(0, ge=0)
):
    try:
        print("hello1")
        cursor = db.orders.aggregate([
             {"$match": {"user_Id": user_Id}},
            {"$sort": {"_id": 1}},
            {"$skip": offset},
            {"$limit": limit},
            {
                "$lookup": {
                    "from": "products",
                    "localField": "items.productId",
                    "foreignField": "_id",
                    "as": "product_docs"
                }
            }
        ])
     
        data = []
        async for order in cursor:
            item_list = []
            total_price = 0

            for item in order['items']:
                product = next((p for p in order["product_docs"] if p["_id"] == item["productId"]), None)
                if product:
                    item_list.append({
                        "productDetails": {
                            "name": product["name"],
                            "Id": str(product["_id"])
                        },
                        "qty": item["qty"]
                    })
                    total_price += item["qty"] * product["price"]

            data.append({
                "Id": str(order["_id"]),
                "items": item_list,
                "Total": total_price
            })

        return {
            "data": data,
            "page": {
                "next": str(offset + limit),
                "limit": len(data),
                "previous": str(max(offset - limit, 0))
            }
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user orders")



