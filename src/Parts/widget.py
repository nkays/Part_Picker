from import_export.widgets import Widget


class CommaSeparatedListWidget(Widget):
    """
    Converts CSV strings like:
    '16x16, 19x19'

    into Python lists:
    ['16x16', '19x19']
    """

    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return []

        if isinstance(value, list):
            return [v.strip() for v in value if v]

        return [v.strip() for v in value.split(",") if v.strip()]

    def render(self, value, obj=None):
        if not value:
            return ""
        return ",".join(value)