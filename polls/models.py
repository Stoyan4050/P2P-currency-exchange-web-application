from django.db import models


# Create models following the UML diagram and the Database design

# Create Debit card model
class DebitCard(models.Model):
    cvv = models.IntegerField()
    card_number = models.CharField(max_length=16)
    expiry_date = models.DateTimeField('date expiry')

    def __str__(self):
        return str(self.id)

    def getCardNumber(self):
        return self.card_number

    def getCVV(self):
        return self.cvv

    def getExpiryDate(self):
        return self.expiry_date

# Create Bank account model
class BankAccount(models.Model):
    sort_code = models.CharField(max_length=6)
    account_number = models.CharField(max_length=8)

    def __str__(self):
        return str(self.id)

    def getSortCode(self):
        return self.sort_code

    def getAccountNo(self):
        return self.account_number

# Create Payments details model
class PaymentDetails(models.Model):
    name = models.CharField(max_length=160)

    debit_card_get = models.ForeignKey(DebitCard, on_delete=models.CASCADE, default=None,
                                       related_name="%(app_label)s_%(class)s_related_get")
    debit_card_rec = models.ForeignKey(DebitCard, on_delete=models.CASCADE, default=None,
                                       related_name="%(app_label)s_%(class)s_related_rec")
    bank_account_get = models.ForeignKey(BankAccount, on_delete=models.CASCADE, default=None,
                                         related_name="%(app_label)s_%(class)s_related_get")
    bank_account_rec = models.ForeignKey(BankAccount, on_delete=models.CASCADE, default=None,
                                         related_name="%(app_label)s_%(class)s_related_rec")

    def __str__(self):
        return str(self.id)

    def getName(self):
        return self.name


# Create Offer model
class Offer(models.Model):
    user_id = models.IntegerField()
    currency_own = models.CharField(max_length=10)
    currency_req = models.CharField(max_length=10)
    amount_offered = models.FloatField(default=0)
    exchange_rate = models.FloatField()
    publish_date = models.DateTimeField('date published')
    expiry_date = models.DateTimeField('date expiry')
    payment_method = models.ForeignKey(PaymentDetails, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.id)

    def updateExpiryTime(self, expiry_date):
        self.expiry_date = expiry_date

    def updateAmount(self, amount):
        self.amount_offered = amount

    def updateExchangeRate(self, rate):
        self.exchange_rate = rate

    def addPaymentMethodGet(self, payment_method_get):
        self.payment_method_get = payment_method_get

    def addPaymentMethodReceive(self, payment_method_rec):
        self.payment_method_rec = payment_method_rec

    def getPaymentMethodGet(self):
        return self.payment_method_get

    def getPaymentMethodReceive(self):
        return self.payment_method_rec

# Create Transaction model
class Transaction(models.Model):
    payment_method_get = models.ForeignKey(PaymentDetails, on_delete=models.PROTECT,
                                           related_name="related_get")
    user_id_rec = models.IntegerField()
    execution_time = models.DateTimeField('execution time')
    payment_method_rec = models.ForeignKey(PaymentDetails, on_delete=models.PROTECT,
                                           related_name="related_rec")

    offer = models.ForeignKey(Offer, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.id)

    def getUserReceive(self):
        return self.user_id_rec

    def getExecutionTime(self):
        return self.execution_time

    def addPaymentMethodGet(self, payment_method_get):
        self.payment_method_get = payment_method_get

    def addPaymentMethodReceive(self, payment_method_rec):
        self.payment_method_rec = payment_method_rec

    def getPaymentMethodGet(self):
        return self.payment_method_get

    def getPaymentMethodReceive(self):
        return self.payment_method_rec
