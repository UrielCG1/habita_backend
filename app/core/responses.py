from typing import Any


def success_response(data: Any):
    return {
        "success": True,
        "data": data,
    }


def paginated_response(items: list, total: int, skip: int, limit: int):
    return {
        "success": True,
        "data": {
            "items": items,
            "pagination": {
                "total": total,
                "skip": skip,
                "limit": limit,
                "returned": len(items),
            },
        },
    }


def error_response(error_type: str, message: str, details=None):
    return {
        "success": False,
        "error": {
            "type": error_type,
            "message": message,
            "details": details,
        },
    }