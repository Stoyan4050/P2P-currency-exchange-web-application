# mock_api
# will act as a bank payment service

CARD_BALANCE = 100
BANK_ACCOUNT_BALANCE = 200


class MOCK_API():

    def pay_by_card(self, name, card_number, cvv, expiry_date, amount_requested):
        if name == "admin":
            return True
        else:
            if CARD_BALANCE > amount_requested:
                return True
        return False

    def pay_by_transfer(self, name, account_number, sort_code, amount_requested):
        if name == "admin":
            return True
        else:
            if BANK_ACCOUNT_BALANCE > amount_requested:
                return True

        return False
