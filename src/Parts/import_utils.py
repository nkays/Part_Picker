from django.utils.text import slugify
from Parts.models import Component

def generate_row_slug(row):
    """Generate or validate slug for an import-export row (dict/OrderedDict)."""
    existing_slug = row.get("slug")
    mpn = row.get("mpn", "")
    brand = row.get("brand", "")

    # Build a queryset to check uniqueness
    qs = Component.objects.filter(slug=existing_slug) if existing_slug else Component.objects.none()
    
    # If row has an 'id', exclude it (so we don’t collide with itself)
    row_id = row.get("id")  # make sure your import provides id if updating
    if row_id:
        qs = qs.exclude(pk=row_id)

    # Keep existing slug if unique
    if existing_slug and not qs.exists():
        return existing_slug

    # Otherwise generate new slug from brand+mpn
    base_slug = slugify(f"{brand}-{mpn}")
    slug = base_slug
    n = 1
    while Component.objects.filter(slug=slug).exclude(pk=row_id).exists():
        slug = f"{base_slug}-{n}"
        n += 1

    return slug