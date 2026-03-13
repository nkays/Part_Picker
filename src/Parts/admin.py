# admin.py

from django.contrib import admin
from import_export import resources, fields
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
    PriceSnapshot,
)

from .import_utils import generate_row_slug
from .widget import CommaSeparatedListWidget


# ────────────────────────────────────────────────
# Price History
# ────────────────────────────────────────────────

@admin.register(PriceSnapshot)
class PriceSnapshotAdmin(admin.ModelAdmin):
    list_display = ("component", "price", "captured_at", "source")
    list_filter = ("source", "captured_at")
    search_fields = ("component__name",)
    date_hierarchy = "captured_at"


# ────────────────────────────────────────────────
# Import / Export Resources
# ────────────────────────────────────────────────

class BaseComponentResource(resources.ModelResource):

    def before_import_row(self, row, **kwargs):
        row["slug"] = generate_row_slug(row)


class FrameResource(BaseComponentResource):

    motor_mounting = fields.Field(
        column_name="motor_mounting",
        attribute="motor_mounting",
        widget=CommaSeparatedListWidget()
    )

    class Meta:
        model = Frame
        import_id_fields = ("mpn",)

        fields = (
            "id", "name", "slug", "brand", "mpn",
            "image_url", "description", "weight_g",

            "frame_style", "wheelbase_mm", "prop_size_max_in",
            "fc_mounting_pattern", "esc_mounting_pattern",
            "motor_mounting", "stack_height_mm", "dry_weight_g",

            "affiliate_provider", "affiliate_url", "asin",
        )

        export_order = fields
        skip_unchanged = True
        report_skipped = True


class MotorResource(BaseComponentResource):
    class Meta:
        model = Motor
        fields = (
            "id","name","slug","brand","mpn","image_url","description","weight_g",
            "kv_rating","stator_size","mount_pattern",
            "max_prop_size_in","max_voltage","test_thrust_g",
            "affiliate_provider","affiliate_url","asin",
        )


class ESCResource(BaseComponentResource):
    class Meta:
        model = ESC
        fields = (
            "id","name","slug","brand","mpn","image_url","description","weight_g",
            "continuous_current_a","burst_current_a",
            "voltage_min","voltage_max","protocol",
            "mount_pattern","is_4in1",
            "affiliate_provider","affiliate_url","asin",
        )


class FCResource(BaseComponentResource):
    class Meta:
        model = FC
        fields = (
            "id","name","slug","brand","mpn","image_url","description","weight_g",
            "mount_pattern","processor","gyro","firmware",
            "cells_supported","uart_count",
            "affiliate_provider","affiliate_url","asin",
        )

    def dehydrate_cells_supported(self, obj):
        return ",".join(map(str, obj.cells_supported)) if obj.cells_supported else ""


class BatteryResource(BaseComponentResource):
    class Meta:
        model = Battery
        fields = (
            "id","name","slug","brand","mpn","image_url","description","weight_g",
            "cells","capacity_mah","discharge_rate_c","connector",
            "affiliate_provider","affiliate_url","asin",
        )


class PropellerResource(BaseComponentResource):
    class Meta:
        model = Propeller
        fields = (
            "id","name","slug","brand","mpn","image_url","description",
            "weight_g_per_prop",
            "size_in","pitch_in","blades","material",
            "affiliate_provider","affiliate_url","asin",
        )


# ────────────────────────────────────────────────
# Shared Child Admin
# ────────────────────────────────────────────────

class ComponentChildAdmin(ImportExportModelAdmin, PolymorphicChildModelAdmin):
    base_model = Component

    search_fields = ("name", "brand", "mpn")
    prepopulated_fields = {"slug": ("name",)}

    list_display = (
        "name",
        "current_price",
        "brand",
        "mpn",
    )


# ────────────────────────────────────────────────
# Frame Admin
# ────────────────────────────────────────────────

@admin.register(Frame)
class FrameAdmin(ComponentChildAdmin):

    resource_class = FrameResource

    list_display = ComponentChildAdmin.list_display + (
        "frame_style",
        "wheelbase_mm",
        "prop_size_max_in",
        "dry_weight_g",
    )

    list_filter = ("frame_style", "brand")

    fieldsets = (
        ("Basic Info", {
            "fields": (
                "name","slug", "current_price","brand","mpn",
                "description","image_url"
            )
        }),

        ("Affiliate", {
            "fields": ("affiliate_provider","affiliate_url","asin")
        }),

        ("Weights", {
            "fields": ("weight_g","dry_weight_g")
        }),

        ("Frame Specs", {
            "fields": (
                "frame_style",
                "wheelbase_mm",
                "prop_size_max_in",
                "fc_mounting_pattern",
                "esc_mounting_pattern",
                "motor_mounting",
                "stack_height_mm",
            )
        }),
    )


# ────────────────────────────────────────────────
# Motor
# ────────────────────────────────────────────────

@admin.register(Motor)
class MotorAdmin(ComponentChildAdmin):

    resource_class = MotorResource

    list_display = ComponentChildAdmin.list_display + (
        "kv_rating",
        "stator_size",
        "mount_pattern",
        "weight_g",
    )

    list_filter = ("brand",)

    fieldsets = (
        ("Basic Info", {"fields": ("name", "current_price", "slug","brand","mpn","description","image_url")}),

        ("Affiliate", {"fields": ("affiliate_provider","affiliate_url","asin")}),

        ("Motor Specs", {
            "fields": (
                "kv_rating",
                "stator_size",
                "mount_pattern",
                "max_prop_size_in",
                "max_voltage",
                "test_thrust_g",
            )
        }),

        ("Weight", {"fields": ("weight_g",)}),
    )


# ────────────────────────────────────────────────
# ESC
# ────────────────────────────────────────────────

@admin.register(ESC)
class ESCAdmin(ComponentChildAdmin):

    resource_class = ESCResource

    list_display = ComponentChildAdmin.list_display + (
        "continuous_current_a",
        "voltage_max",
        "is_4in1",
        "mount_pattern",
    )

    list_filter = ("is_4in1", "brand")


# ────────────────────────────────────────────────
# FC
# ────────────────────────────────────────────────

@admin.register(FC)
class FCAdmin(ComponentChildAdmin):

    resource_class = FCResource

    list_display = ComponentChildAdmin.list_display + (
        "processor",
        "gyro",
        "mount_pattern",
    )

    list_filter = ("brand", "firmware")


# ────────────────────────────────────────────────
# Battery
# ────────────────────────────────────────────────

@admin.register(Battery)
class BatteryAdmin(ComponentChildAdmin):

    resource_class = BatteryResource

    list_display = ComponentChildAdmin.list_display + (
        "cells",
        "capacity_mah",
        "connector",
    )

    list_filter = ("cells", "brand")


# ────────────────────────────────────────────────
# Propeller
# ────────────────────────────────────────────────

@admin.register(Propeller)
class PropellerAdmin(ComponentChildAdmin):

    resource_class = PropellerResource

    list_display = ComponentChildAdmin.list_display + (
        "size_in",
        "pitch_in",
        "blades",
    )

    list_filter = ("blades", "brand")


# ────────────────────────────────────────────────
# Parent Admin (All Components)
# ────────────────────────────────────────────────

@admin.register(Component)
class ComponentParentAdmin(PolymorphicParentModelAdmin):

    base_model = Component

    child_models = (
        Frame,
        Motor,
        ESC,
        FC,
        Battery,
        Propeller,
    )

    child_admin_classes = (
        FrameAdmin,
        MotorAdmin,
        ESCAdmin,
        FCAdmin,
        BatteryAdmin,
        PropellerAdmin,
    )

    list_display = (
        "name",
        "current_price",
        "get_type",
        "brand",
        "mpn",
    )

    list_filter = (PolymorphicChildModelFilter,)
    search_fields = ("name", "brand", "mpn")

    def get_type(self, obj):
        return obj.get_real_instance_class().__name__

    get_type.short_description = "Type"