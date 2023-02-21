from django.contrib import admin

from .models import Offer, Transaction, PaymentDetails, BankAccount, DebitCard

# Register your models here.

admin.site.register(Offer)
admin.site.register(Transaction)
admin.site.register(PaymentDetails)
admin.site.register(BankAccount)
admin.site.register(DebitCard)

