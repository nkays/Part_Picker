# models.py
from django import forms
from django.db import models
from polymorphic.models import PolymorphicModel
from django.contrib.postgres.fields import ArrayField
# Your custom ChoiceArrayField from before...
# Custom ArrayField that renders as checkboxes in forms/admin
from django import forms
from django.contrib.postgres.fields import ArrayField


class ChoiceArrayField(ArrayField):
    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.MultipleChoiceField,
            'choices': self.base_field.choices,
            'widget': forms.CheckboxSelectMultiple,
        }
        # Pop any kwargs that MultipleChoiceField won't accept
        kwargs.pop('base_field', None)  # just in case
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)


# Mounting pattern choices (pulled from your original code – define this before using it)
class MountingPattern(models.TextChoices):
    mm1616   = "16x16_mm",   "16x16 mm"
    mm1619   = "16x19_mm",   "16x19 mm"
    mm1212   = "12x12_mm",   "12x12 mm"
    mm9      = "9_mm",       "9 mm"
    # Add more patterns as needed, e.g. mm20x20 = "20x20_mm", "20x20 mm"

class Component(PolymorphicModel):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)  # auto-gen from name for URLs
    brand = models.CharField(max_length=100, blank=True)
    mpn = models.CharField(max_length=100, blank=True, verbose_name="Manufacturer Part Number", unique=True, null=True)  # great for matching affiliates
    image_url = models.URLField(blank=True)  # approved affiliate hotlink
    description = models.TextField(blank=True)
    weight_g = models.PositiveIntegerField(null=True, blank=True, verbose_name="Weight (g)")  # common across many
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Affiliate basics (expand later with PriceSnapshot model)
    affiliate_provider = models.CharField(max_length=50, blank=True)  # 'amazon', 'getfpv', 'banggood'
    affiliate_url = models.URLField(blank=True)
    asin = models.CharField(max_length=10, blank=True)  # Amazon-specific

    def __str__(self):
        return f"{self.name} ({self.get_real_instance_class().__name__})"

    class Meta:
        ordering = ['name']

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