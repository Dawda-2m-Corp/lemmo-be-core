# Lazy imports to avoid Django app registry issues
def get_abstract_models():
    """Get abstract models when Django is ready."""
    from .abstract_models import (
        UUIDModel,
        CodeModel,
        TimeDataStampedModel,
        TimeDataStampedCodeModel,
        SoftDeleteModel,
        StatusModel,
        NameDescriptionModel,
        AuditModel,
    )

    return {
        "UUIDModel": UUIDModel,
        "CodeModel": CodeModel,
        "TimeDataStampedModel": TimeDataStampedModel,
        "TimeDataStampedCodeModel": TimeDataStampedCodeModel,
        "SoftDeleteModel": SoftDeleteModel,
        "StatusModel": StatusModel,
        "NameDescriptionModel": NameDescriptionModel,
        "AuditModel": AuditModel,
    }


# For backward compatibility, provide direct access when Django is ready
def __getattr__(name):
    """Lazy attribute access for model classes."""
    models = get_abstract_models()
    if name in models:
        return models[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Export all model names for introspection
__all__ = [
    "UUIDModel",
    "CodeModel",
    "TimeDataStampedModel",
    "TimeDataStampedCodeModel",
    "SoftDeleteModel",
    "StatusModel",
    "NameDescriptionModel",
    "AuditModel",
    "get_abstract_models",
]
