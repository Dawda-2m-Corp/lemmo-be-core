from typing import Dict, Any

def lemmo_message(success: bool = False, message: str = "An error occurred", error_details: list[str | Any] = [], data: Any | Dict[str, Any] = {}, errors: list[str | Any] = []):


    return {
        "success": success,
        "message": message,
        "error_details": error_details,
        "data": data,
        "errors": errors
    }
