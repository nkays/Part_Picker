import random
import string

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




def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance 
    has a model with a slug field and a title character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.name)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
                    slug=slug,
                    randstr=random_string_generator(size=4)
                )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug