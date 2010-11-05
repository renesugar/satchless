from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext as _
from satchless.product.models import Variant, ProductAbstract
from . import models

class QuantityForm(object):
    def clean_quantity(self):
        val = self.cleaned_data['quantity']
        if val < 0:
            raise forms.ValidationError("Quantity cannot be negative")
        return val


class AddToCartForm(forms.Form, QuantityForm):
    """Form that adds a Variant quantity to a Cart.
    It may be replaced by more advanced one, performing some checks, e.g.
    verifying the number of items in stock."""
    quantity = forms.DecimalField()
    typ = forms.CharField(max_length=100, widget=forms.HiddenInput())

    def __init__(self, data=None, *args, **kwargs):
        typ = kwargs.pop('typ')
        if data and data.get('typ') != typ:
            data = None
        super(AddToCartForm, self).__init__(data=data, *args, **kwargs)
        self.fields['typ'].initial = typ

    def get_variant(self):
        raise Exception("AddToCart should be subclassed and return Variant subclass " \
                "for given product and form data.")

    def save(self, cart):
        cart.add_quantity(self.get_variant(), self.cleaned_data['quantity'])

def addtocart_factory(klass):
    class AddVariantToForm(klass, AddToCartForm):
        pass
    return AddVariantToForm

class EditCartItemForm(forms.ModelForm, QuantityForm):
    model = models.CartItem
    fields = ('quantity',)

    def save(self, commit=True):
        """Do not call the original save() method, but use cart.set_quantity() instead."""
        self.instance.cart.set_quantity(self.instance.variant, self.cleaned_data['quantity'])

CartItemFormSet = inlineformset_factory(models.Cart, models.CartItem, form=EditCartItemForm, fields=('quantity',), extra=0)
