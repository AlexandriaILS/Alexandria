from django import forms

from alexandria.records.models import BibliographicLevel, ItemType


class LoCSearchForm(forms.Form):
    search_term = forms.CharField(max_length=200)
    store = forms.BooleanField(required=False)


class CombinedRecordItemEditForm(forms.Form):
    # record-related stuff
    title = forms.CharField(max_length=26021)
    authors = forms.CharField(max_length=500)
    subtitle = forms.CharField(max_length=26021, required=False)
    uniform_title = forms.CharField(max_length=26021, required=False)
    notes = forms.CharField(widget=forms.Textarea, required=False)
    series = forms.CharField(widget=forms.Textarea, required=False)
    record_type = forms.ModelChoiceField(queryset=ItemType.objects.all())
    record_bibliographic_level = forms.ModelChoiceField(
        queryset=BibliographicLevel.objects.all()
    )
    summary = forms.CharField(widget=forms.Textarea, required=False)

    # item-related stuff
    barcode = forms.CharField(max_length=50)
    price = forms.DecimalField(max_digits=7, decimal_places=2, required=False)
    publisher = forms.CharField(max_length=500)
    is_active = forms.BooleanField(required=False)
    pubyear = forms.IntegerField(required=False)
    item_bibliographic_level = forms.ModelChoiceField(
        queryset=BibliographicLevel.objects.all()
    )
    item_type = forms.ModelChoiceField(queryset=ItemType.objects.all())


class RecordEditForm(forms.Form):
    # record-related stuff
    title = forms.CharField(max_length=26021)
    authors = forms.CharField(max_length=500)
    subtitle = forms.CharField(max_length=26021, required=False)
    uniform_title = forms.CharField(max_length=26021, required=False)
    notes = forms.CharField(widget=forms.Textarea, required=False)
    series = forms.CharField(widget=forms.Textarea, required=False)
    record_type = forms.ModelChoiceField(queryset=ItemType.objects.all())
    record_bibliographic_level = forms.ModelChoiceField(
        queryset=BibliographicLevel.objects.all()
    )
    summary = forms.CharField(widget=forms.Textarea, required=False)
