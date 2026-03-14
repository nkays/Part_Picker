# models.py
import os
import random

from django import forms
from django.db import models
from django.urls import reverse
from django.contrib.postgres.fields import ArrayField
from django.templatetags.static import static
from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager, PolymorphicQuerySet

from .utils import generate_model_slug, unique_slug_generator

import uuid

def upload_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"Parts/{filename}"


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class ComponentQuerySet(PolymorphicQuerySet):

    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True, active=True)

class ComponentManager(PolymorphicManager):
    def get_queryset(self):
        return ComponentQuerySet(self.model, using=self._db).filter(active=True)

    def active(self):
        return self.get_queryset().active()
    
    def featured(self):
        return self.get_queryset().featured()
    

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id) # Component.objects == self.get_queryset()
        if qs.count() == 1:
            return qs.first()
        return None

FALLBACK_ICONS = {
    'Frame': 'images/icons/frame.png',
    'Motor': 'images/icons/Motor.png',
    'ESC': 'images/icons/ESC.png',
    'FC': 'images/icons/FC.png',
    'Battery': 'images/icons/battery.png',
    'Propeller': 'images/icons/prop.png',
}

class ChoiceArrayField(ArrayField):
    """
    ArrayField rendered as checkboxes in forms/admin.
    Compatible with Django 5+.
    """

    def formfield(self, **kwargs):
        defaults = {
            "required": not self.blank,
            "label": self.verbose_name,
            "help_text": self.help_text,
            "choices": self.base_field.choices,
            "widget": forms.CheckboxSelectMultiple,
        }

        defaults.update(kwargs)

        return forms.MultipleChoiceField(**defaults)


# Mounting pattern choices (pulled from your original code – define this before using it)
class MountingPattern(models.TextChoices):
    mm1616   = "16x16_mm",   "16x16 mm"
    mm1619   = "16x19_mm",   "16x19 mm"
    mm1212   = "12x12_mm",   "12x12 mm"
    mm9      = "9_mm",       "9 mm"
    # Add more patterns as needed, e.g. mm20x20 = "20x20_mm", "20x20 mm"

class Component(TimeStampedModel, PolymorphicModel):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True, db_index=True)  # auto-gen from name for URLs
    brand = models.CharField(max_length=100, blank=True, db_index=True )
    mpn = models.CharField(max_length=100, blank=True, null=True, verbose_name="Manufacturer Part Number", unique=True)
    current_price = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)  # optional for now, expand later with PriceSnapshot model
    affiliate_url = models.URLField(blank=True)  # optional for now, expand later with PriceSnapshot model
    image_url = models.URLField(max_length=500, verbose_name="Affiliate Image URL", help_text="Direct link to the product image on the affiliate site", blank=True, null=True)  # approved affiliate hotlink
    description = models.TextField(blank=True)
    featured = models.BooleanField(default=False)  # for homepage or special listings
    active = models.BooleanField(default=True)  # for soft-deletion or discontinued parts
    weight_g = models.PositiveIntegerField(null=True, blank=True, verbose_name="Weight (g)")  # common across many

    # Affiliate basics (expand later with PriceSnapshot model)
    affiliate_provider = models.CharField(max_length=50, blank=True)  # 'amazon', 'getfpv', 'banggood'
    asin = models.CharField(max_length=10, blank=True)  # Amazon-specific


    objects = ComponentManager()
    all_objects = PolymorphicManager()

    def get_absolute_url(self):
        #return "/Parts/{slug}/".format(slug=self.slug)
        return reverse("Parts:detail", kwargs={"slug": self.slug})


 

    def __str__(self):
        return f"{self.name} ({self.get_real_instance_class().__name__})"
    
    @property
    def latest_price_snapshot(self):
        return self.price_history.order_by('-captured_at').first()

    @property
    def display_image(self):
        """
        Returns the best available image URL:
        1. Affiliate URL if present
        2. Category-specific fallback using Django static
        """
        if self.image_url:
            return self.image_url

        fallback_path = FALLBACK_ICONS.get(self.__class__.__name__)
        if fallback_path:
            return static(fallback_path)

        return ''  # optional ultimate generic
    
    def save(self, *args, **kwargs):
        self.slug = generate_model_slug(self, Component)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
        verbose_name = "Component"
        verbose_name_plural = "Components"
        constraints = [
            models.UniqueConstraint(
                fields=["brand", "name"],
                name="unique_part",
                condition=~models.Q(brand="")
            )
        ]

# Frame (your existing + compatibility prep)
class Frame(Component):
    class FrameStyle(models.TextChoices):
        FREESTYLE   = "freestyle",   "Freestyle"
        RACING      = "racing",      "Racing"
        CINEWHOOP   = "cinewhoop",   "Cinewhoop"
        LONG_RANGE  = "long_range",  "Long Range"
        CINELIFTER  = "cinelifter",  "Cinelifter"
        TOOTHPICK   = "toothpick",   "Toothpick"

    frame_style = models.CharField(
        max_length=20,
        choices=FrameStyle.choices,
        default=FrameStyle.FREESTYLE,
    )
    
    wheelbase_mm = models.PositiveIntegerField(default=220, help_text="Diagonal motor-to-motor distance in mm")
    prop_size_max_in = models.PositiveIntegerField(default=5, help_text="Max recommended prop diameter (inches)")
    
    # Mounting patterns – fixed version
    fc_mounting_pattern = models.CharField(max_length=50, blank=True, help_text="e.g. '20x20_mm', '30.5x30.5_mm'")
    esc_mounting_pattern = models.CharField(max_length=50, blank=True)  # often same as FC
    
    motor_mounting = ChoiceArrayField(                          # ← no quotes, actual class
        models.CharField(max_length=20, choices=MountingPattern.choices),  # ← use the defined enum
        blank=True,
        default=list,
        size=None,  # optional but good
        help_text="Supported motor mounting patterns, e.g. ['16x16_mm', '19x19_mm']"
    )
    
    stack_height_mm = models.PositiveIntegerField(null=True, blank=True, help_text="Max stack height clearance")
    dry_weight_g = models.PositiveIntegerField(null=True, blank=True, verbose_name="Dry Weight (g)")

# Motor
class Motor(Component):
    kv_rating = models.PositiveIntegerField(help_text="RPM per volt")
    stator_size = models.CharField(max_length=50, blank=True, help_text="e.g. '2207', '2306'")
    mount_pattern = models.CharField(max_length=20, blank=True, help_text="e.g. '16x16_mm' – matches Frame.motor_mounting")
    max_prop_size_in = models.PositiveIntegerField(null=True, blank=True)
    max_voltage = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="e.g. 6.0 for 6S max")  # for battery compat
    test_thrust_g = models.PositiveIntegerField(null=True, blank=True)  # optional for estimates

# ESC (Electronic Speed Controller)
class ESC(Component):
    continuous_current_a = models.PositiveIntegerField(help_text="Continuous amp rating")
    burst_current_a = models.PositiveIntegerField(null=True, blank=True)
    voltage_min = models.PositiveIntegerField(default=3, help_text="Min cells, e.g. 3 for 3S")
    voltage_max = models.PositiveIntegerField(default=6, help_text="Max cells, e.g. 6 for 6S")
    protocol = models.CharField(max_length=50, blank=True, help_text="e.g. 'DShot600', 'PWM'")
    mount_pattern = models.CharField(max_length=50, blank=True, help_text="e.g. '20x20_mm' or '30.5x30.5_mm'")
    is_4in1 = models.BooleanField(default=True, help_text="4-in-1 stack style?")

# Flight Controller (FC)
class FC(Component):
    mount_pattern = models.CharField(max_length=50, choices=[('20x20_mm', '20x20 mm'), ('30.5x30.5_mm', '30.5x30.5 mm')], blank=True)
    processor = models.CharField(max_length=50, blank=True, help_text="e.g. 'F722', 'H7'")
    gyro = models.CharField(max_length=50, blank=True, help_text="e.g. 'ICM42688P'")
    firmware = models.CharField(max_length=50, blank=True, help_text="e.g. 'Betaflight', 'INAV'")
    cells_supported = ArrayField(models.PositiveIntegerField(), blank=True, default=list, help_text="[3,4,6] for voltage compat")
    uart_count = models.PositiveIntegerField(null=True, blank=True)  # for peripherals

# Battery
class Battery(Component):
    cells = models.PositiveIntegerField(choices=[(3,'3S'), (4,'4S'), (6,'6S'), (8,'8S')])
    capacity_mah = models.PositiveIntegerField()
    discharge_rate_c = models.CharField(max_length=50, blank=True, help_text="e.g. '120C'")
    connector = models.CharField(max_length=50, blank=True, help_text="e.g. 'XT60', 'XT30'")

# Propeller (add this one early – often overlooked but critical)
class Propeller(Component):
    size_in = models.DecimalField(max_digits=4, decimal_places=2, help_text="e.g. 5.1")
    pitch_in = models.DecimalField(max_digits=4, decimal_places=2, help_text="e.g. 4.3")
    blades = models.PositiveIntegerField(default=3)
    material = models.CharField(max_length=50, blank=True, help_text="e.g. 'Polycarbonate'")
    weight_g_per_prop = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    # Future compat: recommended for motor stator / KV

# Separate model, same indentation level as Component
class PriceSnapshot(models.Model):
    component = models.ForeignKey(
        Component,
        on_delete=models.CASCADE,
        related_name='price_history'  # so you can do component.price_history.all()
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    captured_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=100, blank=True)       # e.g. 'getfpv', 'manual', 'pyrodrone'
    notes = models.TextField(blank=True)                        # optional: sale info, currency, etc.

    class Meta:
        ordering = ['-captured_at']                             # newest first
        verbose_name = "Price Snapshot"
        verbose_name_plural = "Price Snapshots"

    def __str__(self):
        return f"${self.price} for {self.component} on {self.captured_at.date()}"


