from typing import Dict, Any, List, Union, Optional
from dataclasses import dataclass
from enum import Enum


class MessageType(Enum):
    """Enum for message types."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class LemmoResponse:
    """Structured response class for Lemmo API responses."""

    success: bool
    message: str
    error_details: List[Union[str, Any]] = None
    data: Union[Dict[str, Any], Any] = None
    errors: List[Union[str, Any]] = None
    message_type: MessageType = None

    def __post_init__(self):
        if self.error_details is None:
            self.error_details = []
        if self.errors is None:
            self.errors = []
        if self.message_type is None:
            self.message_type = (
                MessageType.SUCCESS if self.success else MessageType.ERROR
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary format."""
        return {
            "success": self.success,
            "message": self.message,
            "error_details": self.error_details,
            "data": self.data,
            "errors": self.errors,
            "message_type": self.message_type.value,
        }


def lemmo_message(
    success: bool = False,
    message: str = "An error occurred",
    error_details: Optional[List[Union[str, Any]]] = None,
    data: Optional[Union[Dict[str, Any], Any]] = None,
    errors: Optional[List[Union[str, Any]]] = None,
    message_type: Optional[MessageType] = None,
) -> Dict[str, Any]:
    """
    Create a standardized Lemmo API response message.

    Args:
        success: Whether the operation was successful
        message: Human-readable message
        error_details: List of detailed error information
        data: Response data payload
        errors: List of error messages
        message_type: Type of message (success, error, warning, info)

    Returns:
        Dictionary with standardized response format
    """
    response = LemmoResponse(
        success=success,
        message=message,
        error_details=error_details or [],
        data=data or {},
        errors=errors or [],
        message_type=message_type,
    )
    return response.to_dict()


def success_message(
    message: str = "Operation completed successfully",
    data: Optional[Union[Dict[str, Any], Any]] = None,
) -> Dict[str, Any]:
    """Create a success response message."""
    return lemmo_message(
        success=True, message=message, data=data, message_type=MessageType.SUCCESS
    )


def error_message(
    message: str = "An error occurred",
    error_details: Optional[List[Union[str, Any]]] = None,
    errors: Optional[List[Union[str, Any]]] = None,
) -> Dict[str, Any]:
    """Create an error response message."""
    return lemmo_message(
        success=False,
        message=message,
        error_details=error_details or [],
        errors=errors or [],
        message_type=MessageType.ERROR,
    )


def warning_message(
    message: str = "Warning", data: Optional[Union[Dict[str, Any], Any]] = None
) -> Dict[str, Any]:
    """Create a warning response message."""
    return lemmo_message(
        success=True, message=message, data=data, message_type=MessageType.WARNING
    )


def info_message(
    message: str = "Information", data: Optional[Union[Dict[str, Any], Any]] = None
) -> Dict[str, Any]:
    """Create an info response message."""
    return lemmo_message(
        success=True, message=message, data=data, message_type=MessageType.INFO
    )


def validate_required_fields(
    data: Dict[str, Any], required_fields: List[str]
) -> List[str]:
    """
    Validate that required fields are present in data.

    Args:
        data: Dictionary to validate
        required_fields: List of required field names

    Returns:
        List of missing field names
    """
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    return missing_fields


def sanitize_data(data: Dict[str, Any], allowed_fields: List[str]) -> Dict[str, Any]:
    """
    Sanitize data by keeping only allowed fields.

    Args:
        data: Dictionary to sanitize
        allowed_fields: List of allowed field names

    Returns:
        Sanitized dictionary with only allowed fields
    """
    return {key: value for key, value in data.items() if key in allowed_fields}
