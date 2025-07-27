from django.test import TestCase
from django import forms
from sams.widgets import *
from django.utils.html import escape

class WidgetTestCase(TestCase):
    """Test case for custom form widgets"""
    
    def test_custom_checkbox_select_multiple(self):
        """Test the CustomCheckboxSelectMultiple widget"""
        choices = [('1', 'Option 1'), ('2', 'Option 2'), ('3', 'Option 3')]
        widget = CustomCheckboxSelectMultiple(choices=choices)
        
        # Test with no value selected
        html = widget.render('test', None)
        self.assertIn('checkbox-group', html)
        self.assertIn('form-check', html)
        self.assertIn('test_0', html)
        self.assertIn('Option 1', html)
        self.assertIn('Option 2', html)
        self.assertIn('Option 3', html)
        
        # Test with values selected
        html = widget.render('test', ['1', '3'])
        self.assertIn('checked', html)
        self.assertIn('value="1"', html)
        self.assertIn('value="3"', html)
        
        # Test with custom attributes
        widget = CustomCheckboxSelectMultiple(attrs={'data-test': 'value'}, choices=choices)
        html = widget.render('test', None)
        self.assertIn('data-test="value"', html)
    
    def test_custom_radio_select(self):
        """Test the CustomRadioSelect widget"""
        choices = [('1', 'Option 1'), ('2', 'Option 2')]
        widget = CustomRadioSelect(choices=choices)
        
        # Test default attributes
        self.assertEqual(widget.attrs['class'], 'form-check-input')
        
        # Test with custom attributes
        widget = CustomRadioSelect(attrs={'data-test': 'value'})
        self.assertEqual(widget.attrs['class'], 'form-check-input')
        self.assertEqual(widget.attrs['data-test'], 'value')
    
    def test_styled_select(self):
        """Test the StyledSelect widget"""
        widget = StyledSelect()
        
        # Test default attributes
        self.assertEqual(widget.attrs['class'], 'form-select')
        self.assertIn('border-radius', widget.attrs['style'])
        
        # Test with custom attributes
        widget = StyledSelect(attrs={'data-test': 'value'})
        self.assertEqual(widget.attrs['class'], 'form-select')
        self.assertEqual(widget.attrs['data-test'], 'value')
    
    def test_searchable_select(self):
        """Test the SearchableSelect widget"""
        widget = SearchableSelect()
        
        # Test default attributes
        self.assertIn('searchable-select', widget.attrs['class'])
        self.assertIn('border-radius', widget.attrs['style'])
        
        # Test with custom attributes
        widget = SearchableSelect(attrs={'data-test': 'value'})
        self.assertIn('searchable-select', widget.attrs['class'])
        self.assertEqual(widget.attrs['data-test'], 'value')
    
    def test_styled_text_input(self):
        """Test the StyledTextInput widget"""
        widget = StyledTextInput()
        
        # Test default attributes
        self.assertEqual(widget.attrs['class'], 'form-control')
        self.assertIn('border-radius', widget.attrs['style'])
        
        # Test with custom attributes
        widget = StyledTextInput(attrs={'data-test': 'value'})
        self.assertEqual(widget.attrs['class'], 'form-control')
        self.assertEqual(widget.attrs['data-test'], 'value')
    
    def test_styled_email_input(self):
        """Test the StyledEmailInput widget"""
        widget = StyledEmailInput()
        
        # Test default attributes
        self.assertEqual(widget.attrs['class'], 'form-control')
        self.assertIn('border-radius', widget.attrs['style'])
        
        # Test with custom attributes
        widget = StyledEmailInput(attrs={'data-test': 'value'})
        self.assertEqual(widget.attrs['class'], 'form-control')
        self.assertEqual(widget.attrs['data-test'], 'value')
    
    def test_styled_number_input(self):
        """Test the StyledNumberInput widget"""
        widget = StyledNumberInput()
        
        # Test default attributes
        self.assertEqual(widget.attrs['class'], 'form-control')
        self.assertIn('border-radius', widget.attrs['style'])
        
        # Test with custom attributes
        widget = StyledNumberInput(attrs={'data-test': 'value'})
        self.assertEqual(widget.attrs['class'], 'form-control')
        self.assertEqual(widget.attrs['data-test'], 'value')
    
    def test_styled_textarea(self):
        """Test the StyledTextarea widget"""
        widget = StyledTextarea()
        
        # Test default attributes
        self.assertEqual(widget.attrs['class'], 'form-control')
        self.assertIn('border-radius', widget.attrs['style'])
        self.assertEqual(widget.attrs['rows'], 4)
        
        # Test with custom attributes
        widget = StyledTextarea(attrs={'rows': 10, 'data-test': 'value'})
        self.assertEqual(widget.attrs['class'], 'form-control')
        self.assertEqual(widget.attrs['rows'], 10)
        self.assertEqual(widget.attrs['data-test'], 'value')

class WidgetIntegrationTestCase(TestCase):
    """Test widgets integrated with forms"""
    
    def test_widget_in_form(self):
        """Test widgets when used in a form"""
        
        class TestForm(forms.Form):
            name = forms.CharField(widget=StyledTextInput())
            email = forms.EmailField(widget=StyledEmailInput())
            age = forms.IntegerField(widget=StyledNumberInput())
            notes = forms.CharField(widget=StyledTextarea())
            category = forms.ChoiceField(
                choices=[('1', 'Category 1'), ('2', 'Category 2')],
                widget=StyledSelect()
            )
            options = forms.MultipleChoiceField(
                choices=[('1', 'Option 1'), ('2', 'Option 2'), ('3', 'Option 3')],
                widget=CustomCheckboxSelectMultiple()
            )
        
        form = TestForm()
        html = form.as_p()
        
        # Check that widgets are rendered correctly
        self.assertIn('form-control', html)
        self.assertIn('form-select', html)
        self.assertIn('checkbox-group', html)
        
        # Test form with data
        form = TestForm({
            'name': 'Test User',
            'email': 'test@example.com',
            'age': '25',
            'notes': 'Test notes',
            'category': '1',
            'options': ['1', '3']
        })
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['name'], 'Test User')
        self.assertEqual(form.cleaned_data['options'], ['1', '3'])