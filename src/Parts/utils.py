from django.utils.text import slugify


def generate_model_slug(instance, model_class):
    """Generate or validate slug for a model instance."""
    mpn = getattr(instance, "mpn", "")
    brand = getattr(instance, "brand", "")
    base_slug = slugify(f"{brand}-{mpn}")

    # Use existing slug if present and unique
    if getattr(instance, "slug", None):
        existing_slug = instance.slug
        if not model_class.objects.filter(slug=existing_slug).exclude(pk=instance.pk).exists():
            return existing_slug  # existing slug is valid

    # # Otherwise, generate a new unique slug
    # slug = base_slug
    # n = 1
    # while model_class.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
    #     slug = f"{base_slug}-{n}"
    #     n += 1
    # return slug