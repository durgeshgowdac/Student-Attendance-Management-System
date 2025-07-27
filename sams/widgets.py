from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class CustomCheckboxSelectMultiple(CheckboxSelectMultiple):
    """Custom checkbox widget with better styling"""
    
    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-check-input'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = []
        
        output = []
        output.append('<div class="checkbox-group">')
        
        for i, (option_value, option_label) in enumerate(self.choices):
            checkbox_attrs = self.build_attrs(attrs, {'type': 'checkbox', 'name': name, 'value': option_value})
            if option_value in value:
                checkbox_attrs['checked'] = True
            
            checkbox_id = f"{name}_{i}"
            checkbox_attrs['id'] = checkbox_id
            
            output.append(format_html(
                '<div class="form-check mb-2">'
                '<input{} />'
                '<label class="form-check-label" for="{}">{}</label>'
                '</div>',
                forms.widgets.flatatt(checkbox_attrs),
                checkbox_id,
                option_label
            ))
        
        output.append('</div>')
        return mark_safe('\n'.join(output))


class CustomRadioSelect(forms.RadioSelect):
    """Custom radio button widget with better styling"""
    
    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-check-input'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class StyledSelect(forms.Select):
    """Custom select widget with better styling"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-select',
            'style': 'border-radius: 8px; border: 2px solid #e9ecef; padding: 10px 15px;'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class SearchableSelect(forms.Select):
    """Select widget with search functionality"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-select searchable-select',
            'style': 'border-radius: 8px; border: 2px solid #e9ecef; padding: 10px 15px;'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class StyledTextInput(forms.TextInput):
    """Custom text input widget with better styling"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control',
            'style': 'border-radius: 8px; border: 2px solid #e9ecef; padding: 10px 15px;'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class StyledEmailInput(forms.EmailInput):
    """Custom email input widget with better styling"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control',
            'style': 'border-radius: 8px; border: 2px solid #e9ecef; padding: 10px 15px;'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class StyledNumberInput(forms.NumberInput):
    """Custom number input widget with better styling"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control',
            'style': 'border-radius: 8px; border: 2px solid #e9ecef; padding: 10px 15px;'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class StyledTextarea(forms.Textarea):
    """Custom textarea widget with better styling"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control',
            'style': 'border-radius: 8px; border: 2px solid #e9ecef; padding: 10px 15px;',
            'rows': 4
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class SearchableSelect(forms.Select):
    """Select widget with search functionality (same as StyledSelect for now)"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-select',
            'style': 'border-radius: 8px; border: 2px solid #e9ecef; padding: 10px 15px;'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)