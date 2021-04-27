from django import forms
from django.core.validators import (
    validate_email,
    RegexValidator
)
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import (
    Newsletters,
    Shop,
    SubMarket
)

# Login Form
class Login (forms.Form):
    username=forms.CharField()
    password=forms.CharField()

    def clean_password (self):
        data=self.cleaned_data['password']

        if len(data) < 8:
           raise ValidationError(_('طول عبارت ورودی کوتاه می باشد.'))

        return data

# Add Email Form
class CheckEmail (forms.Form):

    email=forms.EmailField()

    def clean_email(self):

        email = self.cleaned_data.get('email')

        if validate_email(email):
            return email

class CustomMultipleModelChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj


# Shop Form - Store ModelForm:
class StoreForm(forms.ModelForm):

    Title = forms.CharField(
        label="عنوان حجره",
        widget=forms.TextInput(attrs={
            "placeholder": "لطفا نام حجره خود را وارد کنید",
            "class": "form-control",
            "type": "text",
            "minlength":"20",
            "maxlength":"70",
        })
    )

    Slug = forms.CharField(
        label="شناسه حجره",
        widget=forms.TextInput(attrs={
            "placeholder": "لطفا لینک حجره خود را به انگلیسی وارد کنید",
            "class": "form-control",
            "type": "text",
        }),
        validators=[RegexValidator(r"^[a-z0-9\-_]{2,}")]
    )

    Description = forms.CharField(
        label="درباره حجره",
        widget=forms.Textarea(attrs={
            "placeholder": "لطفا اطلاعات حجره خود را وارد نمایید",
            "class": "form-control",
            "type": "text",
            "rows":"2"
        })
    )

    State = forms.CharField(
        label="استان",
        widget=forms.TextInput(attrs={
            "placeholder": "استان",
            "class": "form-control",
            "type": "text",
        })
    )

    BigCity = forms.CharField(
        label="شهرستان",
        widget=forms.TextInput(attrs={
            "placeholder": "شهرستان",
            "class": "form-control",
            "type": "text",
        })
    )

    City = forms.CharField(
        label="شهر",
        widget=forms.TextInput(attrs={
            "placeholder": "شهر",
            "class": "form-control",
            "type": "text",
        })
    )

    # راسته حجره
    FK_SubMarket = CustomMultipleModelChoiceField(
        # label="راسته حجره",
        queryset=SubMarket.objects.all(),
        # widget=forms.CheckboxSelectMultiple,
    )

    Bio = forms.CharField(
        label="معرفی حجره دار",
        widget=forms.TextInput(attrs={
            "placeholder": "خلاصه توضیحی در مورد خودتان...",
            "class": "form-control",
            "type": "text",
            "maxlength":"200",
            "rows":"2",
        })
    )  

    # close days 
    is_sat_closed = forms.BooleanField(
        label="شنبه",
        required = False,
    )

    is_sun_closed = forms.BooleanField(
        required=False,
        label="یک‌شنبه",
    )

    is_mon_closed = forms.BooleanField(
        required=False,
        label="دوشنبه",
    )

    is_tue_closed = forms.BooleanField(
        required=False,
        label="سه‌شنبه",
    )

    is_wed_closed = forms.BooleanField(
        required=False,
        label="چهارشنبه",
    )

    is_thu_closed = forms.BooleanField(
        required=False,
        label="پنج‌شنبه",
    )

    is_fri_closed = forms.BooleanField(
        required=False,
        label="جمعه",
    )


    class Meta:
        model = Shop
        fields = [
            "Title",
            "Slug",
            "Description",
            "State",
            "BigCity",
            "City",
            "FK_SubMarket",
            "Bio",
            "is_sat_closed",
            "is_sun_closed",
            "is_mon_closed",
            "is_tue_closed",
            "is_wed_closed",
            "is_thu_closed",
            "is_fri_closed",
        ]