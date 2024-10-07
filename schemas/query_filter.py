import re, json
from types import NoneType
from datetime import datetime, timedelta
from fastapi import Query
from utils.exceptions import CustomException
from typing import List

QueryFilterSchema = Query(
    None,
    description="""List of params to filter - OPTIONAL.<br><br>
            <b>Operators allowed:</b><br>
                <ul>
                <li><b>str:</b>       &nbsp;<code>["contains", "not_contains", "!=", "=="]</code></li>
                <li><b>int/float:</b> &nbsp;<code>["==", "!=", "<", "<=", ">", ">="]</code></li>
                <li><b>date:</b>      &nbsp;<code>["<", "<=", ">", ">="]</code></li>
                <li><b>bool:</b>      &nbsp;<code>["==", "!="]</code></li>
            </ul>
            <b>Examples:</b><br>
            <ul>
                <li><pre>[{"field": "name", "operator": "contains", "value": "test"}]</pre></li>
                <li><pre>[{"field": "age", "operator": ">=", "value": 30}]</pre></li>
                <li><pre>[<br>&nbsp;&nbsp;&nbsp;{"field": "date_created", "operator": ">=", "value": "2024-05-01"},<br>&nbsp;&nbsp;&nbsp;{"field": "date_created", "operator": "<", "value": "2024-06-01"}<br>]</pre></li>
            </ul>
        """,
)

required_keys = ["field", "operator", "value"]
valid_operators = ["contains", "not_contains", "<", "<=", ">=", ">", "==", "!="]
valid_value_types = ["str", "int", "float", "date", "bool", "null"]
valid_operators_per_value_type = {
    "str": ["contains", "not_contains", "==", "!="],
    "date": ["<", "<=", ">=", ">"],
    "int": ["<", "<=", ">=", ">", "==", "!="],
    "float": ["<", "<=", ">=", ">", "==", "!="],
    "bool": ["==", "!="],
    "null": ["==", "!="],
}


def validate_filters(filters: str) -> List[dict]:
    # No filters
    if filters == None:
        return []

    # Validate filters is a valid Array
    try:
        filters_array = json.loads(filters)
        if not isinstance(filters_array, list):
            raise CustomException("Filters are not a valid list", None, 400)
    except Exception as e:
        raise CustomException("Filters are not a valid list", None, 400)

    # Validate each filter inside Array
    for i, filter in enumerate(filters_array):
        # Validate filter is a valid dict
        if not isinstance(filter, dict):
            raise CustomException(f"Filter '{filter}' is not valid dict", None, 400)
        else:
            # Validate filter has all required keys
            if not set(required_keys).issubset(filter.keys()):
                raise CustomException(
                    f"Filter '{filter}' does not contain all required keys: {required_keys}",
                    None,
                    400,
                )

            # Validate filter field and operator are valid strings
            if not isinstance(filter["field"], str) or len(filter["field"]) == 0:
                raise CustomException(
                    f"Filter '{filter}' has an empty or not string field", None, 400
                )
            if not isinstance(filter["operator"], str) or len(filter["operator"]) == 0:
                raise CustomException(
                    f"Filter '{filter}' has an empty or not string field", None, 400
                )

            # Validate filter operator is a valid one
            if filter["operator"] not in valid_operators:
                raise CustomException(
                    f"Filter '{filter}' has an invalid operator. Valid operators: {valid_operators}",
                    None,
                    400,
                )

            # Validate filter use case (operator + value) is a valid one
            validate_use_case(filter)

            # Save filter in case it has been modified
            filters_array[i] = filter

    return filters_array


def validate_use_case(filter):
    operator = filter["operator"]
    value = filter["value"]

    if isinstance(value, str):
        # Date value
        if bool(re.match(r"^\d{4}-\d{2}-\d{2}$", value)):
            value_type = "date"
            # Include next 24 hours for including all day with <= and excluding this day with >
            if operator in {"<=", ">"}:
                filter["value"] = datetime.strptime(value, "%Y-%m-%d") + timedelta(hours=24)
            else:
                filter["value"] = datetime.strptime(value, "%Y-%m-%d")
        else:
            value_type = "str"
    elif isinstance(value, int):
        value_type = "int"
    elif isinstance(value, float):
        value_type = "float"
    elif isinstance(value, bool):
        value_type = "bool"
    elif isinstance(value, NoneType):
        value_type = "null"
    else:
        raise CustomException(
            f"Filter '{filter}' has a value with invalid format. Valid formats: {valid_value_types}",
            None,
            400,
        )

    if operator not in valid_operators_per_value_type[value_type]:
        raise CustomException(
            f"Filter '{filter}' has a value of type '{value_type}' with an incompatible operator. Compatible operators: {valid_operators_per_value_type[value_type]}",
            None,
            400,
        )

    return True, None
