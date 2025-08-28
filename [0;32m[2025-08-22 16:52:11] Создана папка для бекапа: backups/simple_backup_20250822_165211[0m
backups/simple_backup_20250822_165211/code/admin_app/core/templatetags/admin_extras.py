from django import template

register = template.Library()

@register.filter
def get_range(value):
    """
    Filter - returns a list containing range made from given value
    Usage (in template):
    <ul>{% for i in 3|get_range %}
      <li>{{ i }}. Do something</li>
    {% endfor %}</ul>
    """
    return range(1, int(value) + 1)
