# yourapp/admin.py  (replace 'yourapp' with your actual app name, e.g. Parts/admin.py)

from django import forms
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
)

from .models import (
    Component,
    Frame,
    Motor,
    ESC,
    FC,
    Battery,
    Propeller,
    ChoiceArrayField,       # if you want to reference it
    MountingPattern,        # for choices reference if needed
)


# ────────────────────────────────────────────────
# Resources for Import / Export (per subclass)
# ────────────────────────────────────────────────

class FrameResource(resources.ModelResource):
    class Meta:
        model = Frame
        fields = (
            'id', 'name', 'slug', 'brand', 'mpn', 'image_url', 'description', 'weight_g',
            'frame_style', 'wheelbase_mm', 'prop_size_max_in',
            'fc_mounting_pattern', 'esc_mounting_pattern', 'motor_mounting',
            'stack_height_mm', 'dry_weight_g',
            'affiliate_provider', 'affiliate_url', 'asin',
        )
        export_order = fields

    # Handle motor_mounting array → comma-separated string for CSV
    def dehydrate_motor_mounting(self, obj):
        return ','.join(obj.motor_mounting) if obj.motor_mounting else ''

    # Optional: parse back on import if needed (usually ChoiceArrayField handles it)
    def before_import_row(self, row, row_result, **kwargs):
        if 'motor_mounting' in row and row['motor_mounting']:
            row['motor_mounting'] = row['motor_mounting'].split(',')
        return row


class MotorResource(resources.ModelResource):
    class Meta:
        model = Motor
        fields = (
            'id', 'name', 'slug', 'brand', 'mpn', 'image_url', 'description', 'weight_g',
            'kv_rating', 'stator_size', 'mount_pattern',
            'max_prop_size_in', 'max_voltage', 'test_thrust_g',
            'affiliate_provider', 'affiliate_url', 'asin',
        )


class ESCResource(resources.ModelResource):
    class Meta:
        model = ESC
        fields = (
            'id', 'name', 'slug', 'brand', 'mpn', 'image_url', 'description', 'weight_g',
            'continuous_current_a', 'burst_current_a',
            'voltage_min', 'voltage_max', 'protocol',
            'mount_pattern', 'is_4in1',
            'affiliate_provider', 'affiliate_url', 'asin',
        )


class FCResource(resources.ModelResource):
    class Meta:
        model = FC
        fields = (
            'id', 'name', 'slug', 'brand', 'mpn', 'image_url', 'description', 'weight_g',
            'mount_pattern', 'processor', 'gyro', 'firmware',
            'cells_supported', 'uart_count',
            'affiliate_provider', 'affiliate_url', 'asin',
        )

    def dehydrate_cells_supported(self, obj):
        return ','.join(map(str, obj.cells_supported)) if obj.cells_supported else ''


class BatteryResource(resources.ModelResource):
    class Meta:
        model = Battery
        fields = (
            'id', 'name', 'slug', 'brand', 'mpn', 'image_url', 'description', 'weight_g',
            'cells', 'capacity_mah', 'discharge_rate_c', 'connector',
            'affiliate_provider', 'affiliate_url', 'asin',
        )


class PropellerResource(resources.ModelResource):
    class Meta:
        model = Propeller
        fields = (
            'id', 'name', 'slug', 'brand', 'mpn', 'image_url', 'description', 'weight_g_per_prop',
            'size_in', 'pitch_in', 'blades', 'material',
            'affiliate_provider', 'affiliate_url', 'asin',
        )


# ────────────────────────────────────────────────
# Child Admin Classes (customize display & forms)
# ────────────────────────────────────────────────

@admin.register(Frame)
class FrameAdmin(ImportExportModelAdmin, PolymorphicChildModelAdmin):
    base_model = Frame
    resource_class = FrameResource

    list_display = ('name', 'brand', 'frame_style', 'wheelbase_mm', 'prop_size_max_in', 'dry_weight_g')
    list_filter = ('frame_style', 'brand')
    search_fields = ('name', 'brand', 'mpn', 'frame_style')
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'brand', 'mpn', 'description', 'image_url')
        }),
        ('Affiliate & Pricing', {
            'fields': ('affiliate_provider', 'affiliate_url', 'asin')
        }),
        ('Weights', {
            'fields': ('weight_g', 'dry_weight_g')
        }),
        ('Frame Specifications', {
            'fields': (
                'frame_style', 'wheelbase_mm', 'prop_size_max_in',
                'fc_mounting_pattern', 'esc_mounting_pattern', 'motor_mounting',
                'stack_height_mm',
            )
        }),
    )


@admin.register(Motor)
class MotorAdmin(ImportExportModelAdmin, PolymorphicChildModelAdmin):
    base_model = Motor
    resource_class = MotorResource

    list_display = ('name', 'brand', 'kv_rating', 'stator_size', 'mount_pattern', 'weight_g')
    list_filter = ('brand',)
    search_fields = ('name', 'brand', 'mpn', 'stator_size')
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        ('Basic Info', {'fields': ('name', 'slug', 'brand', 'mpn', 'description', 'image_url')}),
        ('Affiliate', {'fields': ('affiliate_provider', 'affiliate_url', 'asin')}),
        ('Motor Specs', {'fields': ('kv_rating', 'stator_size', 'mount_pattern', 'max_prop_size_in', 'max_voltage', 'test_thrust_g')}),
        ('Weight', {'fields': ('weight_g',)}),
    )


@admin.register(ESC)
class ESCAdmin(ImportExportModelAdmin, PolymorphicChildModelAdmin):
    base_model = ESC
    resource_class = ESCResource

    list_display = ('name', 'brand', 'continuous_current_a', 'voltage_max', 'is_4in1', 'mount_pattern')
    list_filter = ('is_4in1', 'brand')
    search_fields = ('name', 'brand', 'mpn')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(FC)
class FCAdmin(ImportExportModelAdmin, PolymorphicChildModelAdmin):
    base_model = FC
    resource_class = FCResource

    list_display = ('name', 'brand', 'processor', 'gyro', 'mount_pattern')
    list_filter = ('brand', 'firmware')
    search_fields = ('name', 'brand', 'mpn', 'processor', 'gyro')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Battery)
class BatteryAdmin(ImportExportModelAdmin, PolymorphicChildModelAdmin):
    base_model = Battery
    resource_class = BatteryResource

    list_display = ('name', 'brand', 'cells', 'capacity_mah', 'connector')
    list_filter = ('cells', 'brand')
    search_fields = ('name', 'brand', 'mpn')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Propeller)
class PropellerAdmin(ImportExportModelAdmin, PolymorphicChildModelAdmin):
    base_model = Propeller
    resource_class = PropellerResource

    list_display = ('name', 'brand', 'size_in', 'pitch_in', 'blades')
    list_filter = ('blades', 'brand')
    search_fields = ('name', 'brand', 'mpn')
    prepopulated_fields = {'slug': ('name',)}


# ────────────────────────────────────────────────
# Parent Admin – unified view of all components
# ────────────────────────────────────────────────

@admin.register(Component)
class ComponentParentAdmin(PolymorphicParentModelAdmin):
    base_model = Component

    # REQUIRED: list all concrete child models here
    child_models = (
        Frame,
        Motor,
        ESC,
        FC,
        Battery,
        Propeller,
    )

    # Optional: custom admin classes for each child
    child_admin_classes = (
        FrameAdmin,
        MotorAdmin,
        ESCAdmin,
        FCAdmin,
        BatteryAdmin,
        PropellerAdmin,
    )

    list_display = ('name', 'get_type', 'brand', 'mpn')
    list_filter = (PolymorphicChildModelFilter,)
    search_fields = ('name', 'brand', 'mpn')

    def get_type(self, obj):
        return obj.get_real_instance_class().__name__
    get_type.short_description = 'Type'