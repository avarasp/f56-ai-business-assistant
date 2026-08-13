from app.db import query_all
from app.schemas import SalesQuery


GROUP_EXPRESSIONS = {
    "none": None,
    "product": "product_name",
    "country": "country_code",
    "platform": "pay_platform_name",
    "month": "DATE_FORMAT(sale_date, '%Y-%m')",
    "year": "YEAR(sale_date)",
}


METRIC_EXPRESSIONS = {
    "copies": "COUNT(*)",
    "gross_revenue": "COALESCE(SUM(gross_amount), 0)",
    "fees": "COALESCE(SUM(fee_amount), 0)",
    "net_revenue": "COALESCE(SUM(net_amount), 0)",
}


def get_sales(query: SalesQuery) -> dict:
    metric_expr = METRIC_EXPRESSIONS[query.metric]
    group_expr = GROUP_EXPRESSIONS[query.group_by]

    where = []
    params = []

    if query.date_from:
        where.append("sale_date >= %s")
        params.append(query.date_from)

    if query.date_to:
        # date_to is inclusive at the business-query level.
        # Using DATE() keeps the behavior simple for now because sale_date
        # contains a full datetime.
        where.append("DATE(sale_date) <= %s")
        params.append(query.date_to)

    if query.product_name:
        where.append("LOWER(product_name) LIKE LOWER(%s)")
        params.append(f"%{query.product_name}%")

    if query.country_code:
        where.append("UPPER(country_code) = UPPER(%s)")
        params.append(query.country_code)

    if query.platform_name:
        where.append("LOWER(pay_platform_name) LIKE LOWER(%s)")
        params.append(f"%{query.platform_name}%")

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    if query.metric == "copies":
        if group_expr:
            sql = f"""
                SELECT
                    {group_expr} AS group_key,
                    {metric_expr} AS value
                FROM vw_sales
                {where_sql}
                GROUP BY {group_expr}
                ORDER BY value DESC, group_key ASC
            """
        else:
            sql = f"""
                SELECT
                    {metric_expr} AS value
                FROM vw_sales
                {where_sql}
            """

    else:
        if group_expr:
            sql = f"""
                SELECT
                    {group_expr} AS group_key,
                    currency,
                    {metric_expr} AS value
                FROM vw_sales
                {where_sql}
                GROUP BY {group_expr}, currency
                ORDER BY value DESC, group_key ASC
            """
        else:
            sql = f"""
                SELECT
                    currency,
                    {metric_expr} AS value
                FROM vw_sales
                {where_sql}
                GROUP BY currency
                ORDER BY value DESC
            """

    rows = query_all(sql, tuple(params))

    return {
        "metric": query.metric,
        "group_by": query.group_by,
        "filters": query.model_dump(mode="json"),
        "rows": rows,
        "semantics": {
            "copies": "one vw_sales row = one recorded sale",
            "gross_revenue": "SUM(vw_sales.gross_amount)",
            "fees": "SUM(vw_sales.fee_amount)",
            "net_revenue": "SUM(vw_sales.net_amount)",
        },
    }