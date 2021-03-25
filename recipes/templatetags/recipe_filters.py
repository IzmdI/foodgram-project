from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context["request"].GET.copy()
    query.pop("page", None)
    query.update(kwargs)
    return query.urlencode()


@register.filter
def format_str_by_value(value):
    if value == 4:
        return f"{value-3} рецепт..."
    elif 5 <= value <= 7:
        return f"{value-3} рецепта..."
    else:
        return f"{value-3} рецептов..."
