from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
import uuid


class UUIDModel(models.Model):
    """
    Abstract base model with UUID primary key.
    Provides a unique identifier for all models.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__}({self.id})"


class CodeModel(UUIDModel):
    """
    Abstract base model with UUID primary key and code field.
    Useful for models that need a human-readable identifier.
    """

    code = models.CharField(
        max_length=50,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9_-]+$",
                message="Code must contain only uppercase letters, numbers, underscores, and hyphens.",
            )
        ],
        help_text="Unique code identifier (uppercase letters, numbers, underscores, hyphens only)",
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.code}"


class TimeDataStampedModel(UUIDModel):
    """
    Abstract base model with UUID primary key, created_at, and updated_at fields.
    Automatically tracks creation and modification times.
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.__class__.__name__}({self.id}) - {self.created_at}"


class TimeDataStampedCodeModel(TimeDataStampedModel, CodeModel):
    """
    Abstract base model combining UUID, timestamps, and code fields.
    Most comprehensive base model for most use cases.
    """

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code}"


class SoftDeleteModel(TimeDataStampedModel):
    """
    Abstract base model with soft delete functionality.
    Records are marked as deleted instead of being physically removed.
    """

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        """Mark the record as deleted."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])

    def __str__(self):
        status = "DELETED" if self.is_deleted else "ACTIVE"
        return f"{self.__class__.__name__}({self.id}) - {status}"


class StatusModel(TimeDataStampedModel):
    """
    Abstract base model with status tracking.
    Useful for models that need to track different states.
    """

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("pending", "Pending"),
        ("suspended", "Suspended"),
    ]

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="active", db_index=True
    )

    class Meta:
        abstract = True

    def is_active(self) -> bool:
        """Check if the record is active."""
        return self.status == "active"

    def activate(self):
        """Set status to active."""
        self.status = "active"
        self.save(update_fields=["status"])

    def deactivate(self):
        """Set status to inactive."""
        self.status = "inactive"
        self.save(update_fields=["status"])

    def __str__(self):
        return f"{self.__class__.__name__}({self.id}) - {self.status}"


class NameDescriptionModel(TimeDataStampedModel):
    """
    Abstract base model with name and description fields.
    Common pattern for many business models.
    """

    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return self.name


class AuditModel(TimeDataStampedModel):
    """
    Abstract base model with audit fields.
    Tracks who created and last modified the record.
    """

    created_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
        help_text="User who created this record",
    )
    modified_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_modified",
        help_text="User who last modified this record",
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Override save to track modification user."""
        # This would need to be implemented based on your authentication system
        # For now, we'll just call the parent save
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.__class__.__name__}({self.id}) - Created by: {self.created_by}"
