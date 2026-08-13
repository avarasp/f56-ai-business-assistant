from app.config import settings
from app.db import query_all
from app.schemas import ProductQuery

def get_products(query: ProductQuery) -> dict:
    params = []
    where_sql = ""

    if query.product_name:
        where_sql = "WHERE LOWER(name) LIKE LOWER(%s)"
        params.append(f"%{query.product_name}%")

    sql = f"""
        SELECT id, name
        FROM {settings.products_table}
        {where_sql}
        ORDER BY name
        LIMIT 100
    """

    return {
        "filters": query.model_dump(mode="json"),
        "rows": query_all(sql, tuple(params)),
        "available_fields": ["id", "name"],
    }
