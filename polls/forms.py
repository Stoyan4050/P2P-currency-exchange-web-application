from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import numpy as np
from django.contrib.auth.forms import UsernameField

# Create your forms here.

# define all currencies
CURRENCIES = ((1, "EUR"), (2, "USD"), (3, "GBP"), (4, "AUD"), (5, "PLN"), (6, "JPY"), (7, "BRL"),
              (8, "CAD"), (9, "CHF"), (10, "TRY"), (11, "SGD"), (12, "RUB"), (13, "MXN"), (14, "NOK"),
              (15, "CZK"), (16, "INR"), (17, "RON"), (18, "TWD"))


# create form for adding an offer
class AddOfferForm(forms.Form):
    currency_own = forms.ChoiceField(choices=CURRENCIES)
    currency_req = forms.ChoiceField(choices=CURRENCIES)
    amount_offered = forms.FloatField()
    exchange_rate = forms.FloatField()
    expiry_date = forms.DateTimeField(widget=forms.SelectDateWidget())
    expiry_time = forms.TimeField(widget=forms.TimeInput())
    payment_method_get = forms.ChoiceField(choices=((1, "Debit card"), (2, "Bank transfer")))
    payment_method_receive = forms.ChoiceField(choices=((1, "Debit card"), (2, "Bank transfer")))


# create form for updating an offer
class UpdateOfferForm(forms.Form):
    currency_own = forms.ChoiceField(choices=CURRENCIES, required=True)
    currency_req = forms.ChoiceField(choices=CURRENCIES, required=True)
    amount_offered = forms.FloatField(required=False)
    exchange_rate = forms.FloatField(required=False)
    expiry_date = forms.DateTimeField(widget=forms.SelectDateWidget(), required=False)
    expiry_time = forms.TimeField(widget=forms.TimeInput(), required=False)


# create form for buying an offer (providing payment details)
class BuyOffer(forms.Form):
    payment_method_get = forms.ChoiceField(choices=((1, "Debit card"), (2, "Bank transfer")))
    payment_method_receive = forms.ChoiceField(choices=((1, "Debit card"), (2, "Bank transfer")))


# create form for adding payment details
# Based on the user preferences we ask for bank account/ debit card details
# Here paying: debit card, receiving: debit card
class PaymentForm1(forms.Form):
    full_name = forms.CharField(max_length=160)
    debit_cvv_pay = forms.CharField(max_length=3)
    debit_card_number_pay = forms.CharField(max_length=16)
    debit_expiry_date_pay = forms.DateField(widget=forms.SelectDateWidget())

    debit_cvv_receive = forms.CharField(max_length=3)
    debit_card_number_receive = forms.CharField(max_length=16)
    debit_expiry_date_receive = forms.DateField(widget=forms.SelectDateWidget())


# create form for adding payment details
# Based on the user preferences we ask for bank account/ debit card details
# Here paying: debit card, receiving: bank account
class PaymentForm2(forms.Form):
    full_name = forms.CharField(max_length=160)
    debit_cvv_pay = forms.CharField(max_length=3)
    debit_card_number_pay = forms.CharField(max_length=16)
    debit_expiry_date_pay = forms.DateField(widget=forms.SelectDateWidget())

    bank_sort_code_receive = forms.CharField(max_length=6)
    bank_account_number_receive = forms.CharField(max_length=8)


# create form for adding payment details
# Based on the user preferences we ask for bank account/ debit card details
# Here paying: bank account, receiving: debit card
class PaymentForm3(forms.Form):
    full_name = forms.CharField(max_length=160)
    bank_sort_code_pay = forms.CharField(max_length=6)
    bank_account_number_pay = forms.CharField(max_length=8)

    debit_cvv_receive = forms.CharField(max_length=3)
    debit_card_number_receive = forms.CharField(max_length=16)
    debit_expiry_date_receive = forms.DateField(widget=forms.SelectDateWidget())


# create form for adding payment details
# Based on the user preferences we ask for bank account/ debit card details
# Here paying: bank account, receiving: bank account
class PaymentForm4(forms.Form):
    full_name = forms.CharField(max_length=160)
    bank_sort_code_pay = forms.CharField(max_length=6)
    bank_account_number_pay = forms.CharField(max_length=8)

    bank_sort_code_receive = forms.CharField(max_length=6)
    bank_account_number_receive = forms.CharField(max_length=8)


# create form for updating user details
class UpdateUserForm(forms.ModelForm):
    username = UsernameField(
        label='Email (Username)',
        widget=forms.EmailInput(),
        required=False
    )
    name = forms.CharField(max_length=101, required=False)
    birth_date = forms.DateField(widget=forms.SelectDateWidget(years=np.arange(1900, 2021, 1).tolist()), required=False)

    class Meta:
        model = User
        fields = ["username", "name", "birth_date"]


# create a form for registering a user
class UserRegistrationForm(UserCreationForm):
    username = UsernameField(
        label='Email (Username)',
        widget=forms.EmailInput()
    )
    name = forms.CharField(max_length=101)
    birth_date = forms.DateField(widget=forms.SelectDateWidget(years=np.arange(1900, 2021, 1).tolist()))

    class Meta:
        model = User
        fields = ["username", "name", "birth_date", "password1", "password2"]
