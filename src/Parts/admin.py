# Parts/admin.py  (or drone/parts/admin.py)
# Parts/admin.py
from django.contrib import admin
from django import forms  # ← add this
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from .models import Component, Frame, Motor, ESC, Battery  # add others later
from django import forms

# Child admins first (optional but good for organization)

@admin.register(Frame)
class FrameAdmin(PolymorphicChildModelAdmin):
    base_model = Frame

    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     form.base_fields['motor_mounting'].widget = forms.CheckboxSelectMultiple(
    #     choices=Frame.MountingPattern.choices  # ← Frame.MountingPattern works without importing the inner class
    #     )
    #     return form

@admin.register(Motor)
class MotorAdmin(PolymorphicChildModelAdmin):
    base_model = Motor
    # Add motor-specific list_display, fields, etc. here later if needed

@admin.register(ESC)
class ESCAdmin(PolymorphicChildModelAdmin):
    base_model = ESC

@admin.register(Battery)
class BatteryAdmin(PolymorphicChildModelAdmin):
    base_model = Battery

# Parent admin — child_models is NOW just the models
@admin.register(Component)
class ComponentAdmin(PolymorphicParentModelAdmin):
    base_model = Component
    
    child_models = (Frame, Motor, ESC, Battery)  # ← just the model classes, no tuples or admins here!
    
    list_display = ('name', 'brand', 'get_real_instance_class_name')
    search_fields = ('name', 'brand')
    
    def get_real_instance_class_name(self, obj):
        return obj.get_real_instance_class().__name__
    get_real_instance_class_name.short_description = 'Type'