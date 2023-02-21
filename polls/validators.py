import datetime
import pytz


# create a validator class to check payment details and offer details
class validators():

    # validate that the expiry time of and offer/ debit card is after the current time
    def time_validator(self, expiry_time):

        if isinstance(expiry_time, str):
            expiry_time = datetime.datetime.strptime(expiry_time, '%Y-%m-%d %H:%M')

        utc = pytz.UTC
        time_now = datetime.datetime.now().replace(tzinfo=utc)
        expiry_time1 = expiry_time.replace(tzinfo=utc)

        if expiry_time1 < time_now:
            return False
        else:
            return True

    # validate that user has entered valid debit card details
    def card_validator(self, card_number, cvv, expiry_date):
        validator = validators()
        if len(card_number) == 16 and len(cvv) == 3 and validator.time_validator(expiry_date):
            if card_number.isdigit() and cvv.isdigit():
                return True

        return False

    # validate that user has entered valid bank account details
    def bank_account_validator(self, account_number, sort_code):
        if len(account_number) == 8 and len(sort_code) == 6:
            if account_number.isdigit() and sort_code.isdigit():
                return True

        return False
