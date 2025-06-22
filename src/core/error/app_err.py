class AppErr(Exception):
    """
    A structured application exception.

    Attributes:
        - message: Required user-facing message (short or full)
        - description: Optional, longer user guidance
        - debug_message: Internal message for logs/debugging
        - code: Optional error code (for i18n/tracking)
    """
    def __init__(
        self,
        message: str,
        description: str = "",
        debug_message: str = "",
        code: str | None = None,
    ):
        self.code = code
        self.message = message
        self.description = description
        self.debug_message = debug_message
        super().__init__(message)

    def __str__(self):
        return f"[{self.code}] {self.message}" if self.code else self.message

    def to_dict(self) -> dict:
        return {
            "message": self.message,
            "description": self.description,
            "debug_message": self.debug_message,
            "code": self.code
        }
