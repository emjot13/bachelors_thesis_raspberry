from django import forms


class ItemForm(forms.Form):
    item_name = forms.CharField(label='Nazwa produktu', max_length=100,
                                error_messages={'required': 'Podaj nazwę produktu'})
    choices = ((1, "Cała nazwa"), (2, "Początek nazwy"), (3, "Osobne słowo"))
    find_by = forms.ChoiceField(label='Sposób szukania', choices=choices,
                                error_messages={'required': 'Wybierz sposób szukania produktu'})
    discount = forms.FloatField(label='Rabat', min_value=0, max_value=100, error_messages={
        'required': 'Podaj rabat',
        'invalid': 'Rabat musi być liczbą',
        'min_value': 'Rabat musi być pomiędzy 0 a 100',
        'max_value': 'Rabat musi być pomiędzy 0 a 100',
    })


class ExcelForm(forms.Form):
    excel_file = forms.FileField(label="Plik excelowy z produktami", required=True, widget=forms.FileInput(attrs={'value': "Wybierz plik"}))

