from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Dict, Any, Union, Awaitable


class ValidationErrorHandler:
    """Reusable validation error handler for FastAPI applications"""

    @staticmethod
    def format_error_message(error: Dict[str, Any]) -> str:
        """Format a single validation error into a clean message"""
        field_name = error['loc'][-1] if error['loc'] else 'unknown'
        error_type = error['type']
        error_msg = error['msg']
        ctx = error.get('ctx', {})
        input_value = error.get('input', '')

        # Handle empty strings as missing fields for better UX
        if error_type == 'string_too_short' and input_value == '':
            return f"Field required -> {field_name}"

        # Custom error messages based on error type
        error_mappings = {
            'missing': f"Field required -> {field_name}",
            'string_too_short': f"{field_name} should have at least {ctx.get('min_length', '')} characters",
            'string_too_long': f"{field_name} should have at most {ctx.get('max_length', '')} characters",
            'value_error': ValidationErrorHandler._handle_value_error(field_name, error_msg),
            'type_error': f"Invalid type for {field_name}",
            'greater_than': f"{field_name} should be greater than {ctx.get('gt', '')}",
            'greater_than_equal': f"{field_name} should be greater than or equal to {ctx.get('ge', '')}",
            'less_than': f"{field_name} should be less than {ctx.get('lt', '')}",
            'less_than_equal': f"{field_name} should be less than or equal to {ctx.get('le', '')}",
            'string_pattern_mismatch': f"Invalid format for {field_name}",
        }

        return error_mappings.get(error_type, f"{field_name}: {error_msg}")

    @staticmethod
    def _handle_value_error(field_name: str, error_msg: str) -> str:
        """Handle specific value errors with better messages"""
        if 'email' in field_name.lower() or 'email' in error_msg.lower():
            return f"Invalid email format for {field_name}"
        elif 'password' in field_name.lower():
            return f"Invalid password format for {field_name}"
        else:
            return f"Invalid value for {field_name}"

    @staticmethod
    async def handle_validation_error(request: Request, exc: Exception) -> JSONResponse:
        """Main handler for validation errors"""
        if not isinstance(exc, RequestValidationError):
            # Fallback for other exceptions
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Validation error"}
            )

        errors = exc.errors()

        if len(errors) == 1:
            # Single error - return as string
            detail = ValidationErrorHandler.format_error_message(errors[0])
        else:
            # Multiple errors - return as array
            detail = [ValidationErrorHandler.format_error_message(error) for error in errors]

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": detail}
        )