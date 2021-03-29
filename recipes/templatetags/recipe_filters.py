from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context["request"].GET.copy()
    query.pop("page", None)
    query.update(kwargs)
    tags = query.getlist("tags")
    if tags and len(tags) == 3:
        query.pop("tags", None)
    return query.urlencode()


@register.filter
def format_str_by_value(value):
    if value == 1:
        return "%d рецепт..." % value
    elif 2 <= value <= 4:
        return "%d рецепта..." % value
    return "%d рецептов..." % value
