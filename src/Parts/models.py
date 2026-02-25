# models.py
from django.db import models
from polymorphic.models import PolymorphicModel
from django.contrib.postgres.fields import ArrayField


class Component(PolymorphicModel):
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_real_instance_class().__name__})"  # or whatever you like

# Now the subclasses — same indentation level as Component

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
    
    class MountingPattern(models.TextChoices):
        mm1616        = "16x16_mm", "16x16 mm"
        mm1619        = "16x19_mm", "16x19 mm"
        mm1212        = "12x12_mm", "12x12 mm"
        mm9           = "9_mm",        "9 mm"
    motor_mounting = ArrayField(
        base_field=models.CharField(
            max_length=20,
            choices=MountingPattern.choices,
        ),
        blank=True,
        default=list,
    )

    Motor_Count     = models.IntegerField(default=4)
    Wheelbase       = models.IntegerField(default=6)
    Prop_Size       = models.IntegerField(default=6)
    dry_weight_g    = models.IntegerField(
    verbose_name="Dry Weight",
    help_text="in grams (g)",
    db_comment="Frame weight without electronics, in grams",
    )

class Motor(Component):
    kv_rating = models.IntegerField()
    stator_size = models.CharField(max_length=50, blank=True)
    # add mounting pattern, weight, etc.

class ESC(Component):
    continuous_current = models.IntegerField()  # amps
    burst_current = models.IntegerField(blank=True, null=True)
    # protocol, etc.

class Battery(Component):
    cells = models.PositiveIntegerField(choices=[(3, '3S'), (4, '4S'), (6, '6S')])
    capacity_mah = models.PositiveIntegerField()
    discharge_rate = models.CharField(max_length=50, blank=True)  # e.g., "120C"

# And so on for Propeller, Frame, FC, etc.