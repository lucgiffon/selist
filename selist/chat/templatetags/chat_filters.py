from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using the key"""
    if dictionary and hasattr(dictionary, 'get'):
        return dictionary.get(key)
    return None