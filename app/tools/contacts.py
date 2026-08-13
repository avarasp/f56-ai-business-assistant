from app.config import settings
from app.db import query_all
from app.schemas import ContactQuery

def get_contacts(query: ContactQuery) -> dict:
    where = []
    params = []

    if query.email:
        where.append("LOWER(email) = LOWER(%s)")
        params.append(query.email)

    if query.name_contains:
        where.append("LOWER(name) LIKE LOWER(%s)")
        params.append(f"%{query.name_contains}%")

    if query.text_contains:
        where.append("LOWER(message) LIKE LOWER(%s)")
        params.append(f"%{query.text_contains}%")

    if query.date_from:
        where.append("DATE(date) >= %s")
        params.append(query.date_from)

    if query.date_to:
        where.append("DATE(date) <= %s")
        params.append(query.date_to)

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    sql = f"""
        SELECT id, name, email, message, date
        FROM {settings.contacts_table}
        {where_sql}
        ORDER BY date DESC
        LIMIT %s
    """
    params.append(query.limit)

    return {
        "filters": query.model_dump(mode="json"),
        "rows": query_all(sql, tuple(params)),
        "available_fields": ["id", "name", "email", "message", "date"],
    }
