from app.application.common.exceptions import ResourceNotFoundError


class DemoIntakeScenarioNotFoundError(ResourceNotFoundError):
    """Raised when a demo intake scenario cannot be found."""

