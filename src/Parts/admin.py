# Parts/admin.py  (or drone/parts/admin.py)
# Parts/admin.py
from django import forms
from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from .models import Component, Frame, Motor, ESC, FC, Battery  # add others later


# Child admins first (optional but good for organization)

@admin.register(Frame)
class FrameAdmin(PolymorphicChildModelAdmin):
    base_model = Frame
    # No get_form override needed anymore — ChoiceArrayField handles checkboxes + pre-checks
    # You can add list_display, search_fields, etc. here later if you want frame-specific columns

@admin.register(Motor)
class MotorAdmin(PolymorphicChildModelAdmin):
    base_model = Motor
    # Add motor-specific list_display, fields, etc. here later if needed

@admin.register(ESC)
class ESCAdmin(PolymorphicChildModelAdmin):
    base_model = ESC

@admin.register(FC)
class FCAdmin(PolymorphicChildModelAdmin):
    base_model = FC

@admin.register(Battery)
class BatteryAdmin(PolymorphicChildModelAdmin):
    base_model = Battery

# Parent admin — child_models is NOW just the models
@admin.register(Component)
class ComponentAdmin(PolymorphicParentModelAdmin):
    base_model = Component
    
    child_models = (Frame, Motor, ESC, FC, Battery)  # ← just the model classes, no tuples or admins here!
    
    list_display = ('name', 'brand', 'get_real_instance_class_name')
    search_fields = ('name', 'brand')
    
    def get_real_instance_class_name(self, obj):
        return obj.get_real_instance_class().__name__
    get_real_instance_class_name.short_description = 'Type'

    