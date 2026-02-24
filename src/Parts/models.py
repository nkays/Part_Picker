# models.py
from django.db import models
from polymorphic.models import PolymorphicModel

class Component(PolymorphicModel):
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_real_instance_class().__name__})"  # or whatever you like

# Now the subclasses — same indentation level as Component
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