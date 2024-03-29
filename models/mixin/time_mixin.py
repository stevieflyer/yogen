import datetime

from pydantic import Field, BaseModel

from stevools.string_utils import generate_random_id


class LastModifiedMixin(BaseModel):
    """Mixin for common that need to track the last time they were modified."""
    last_modified: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    """Datetime when the model was last modified."""

    def _update_last_modified(self) -> None:
        """Updates the last modified datetime to the current time."""
        self.last_modified = datetime.datetime.utcnow()


class CreatedAtMixin(BaseModel):
    """Mixin for common that need to track the time they were created."""
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    """Datetime when the model was created."""


class AutoGeneratedIdMixin(BaseModel):
    """Mixin for common that need to have a unique ID."""

    class Config:
        populate_by_name = True

    id: str = Field(default_factory=lambda: generate_random_id(), alias='_id')


__all__ = [
    'LastModifiedMixin',
    'CreatedAtMixin',
    'AutoGeneratedIdMixin',
]
