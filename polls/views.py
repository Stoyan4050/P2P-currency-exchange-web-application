from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Offer, PaymentDetails, DebitCard, BankAccount, Transaction
from django.template import loader
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.views import LoginView
import datetime
from .forms import AddOfferForm, PaymentForm1, PaymentForm2, PaymentForm3, PaymentForm4, BuyOffer, UpdateUserForm
from .forms import UserRegistrationForm, UpdateOfferForm
from django.db.models import ProtectedError
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from .validators import validators
from .mock_api import MOCK_API


# create custom Login view that uses the Django framework for Log In of a user
class CustomLoginView(LoginView):
    form = UserRegistrationForm


# define global variables used when filtering based on pair of currencies
# used to show only offer for a particular pair of currencies
global curr_chosen1, curr_chosen2

# global variable used to keep track of the current offer
global current_offer

# define all supported currencies
all_currencies = ["EUR", "USD", "GBP", "AUD", "PLN", "JPY", "BRL",
                  "CAD", "CHF", "TRY", "SGD", "RUB", "MXN", "NOK", "CZK", "INR", "RON", "TWD"]
# set a flat fee
FEE = 0.2


# renders the home page, shows the home view to the user
def index_new(request):
    req = request.POST
    return render(request, "polls/index1.html")


# renders the log out page, shows the home view to the user
def logout_view(request):
    return render(logout(request), "polls/index1.html")


# renders the custom error page, shows the error page to the user
def custom_page_not_found_view(request, exception=None):
    print("Exception 404: ", exception)

    return redirect('/')


# renders the profile page, shows the profile page to the user
def profile(request):
    # get the currently logged in user instance
    user = request.user

    # get all offers
    offers = Offer.objects.order_by('-publish_date')

    # get all transactions
    all_transactions = Transaction.objects.all()

    offers_for_user = []
    trans_for_user = []

    # filter the offers so that we get only the offers related to the logged in user
    for offer in offers:
        if offer.user_id == request.user.id:
            offers_for_user.append(offer)

    # filter the transaction so that we get only the transaction related to the logged in user
    for trans in all_transactions:
        if trans.user_id_rec == request.user.id:
            trans_for_user.append(trans)

    template = loader.get_template('polls/profile.html')

    selected_offers_final = []

    # filter the offers that are already executed
    for offer in offers_for_user:
        flag = 0
        for trans in all_transactions:
            if trans.offer.id == offer.id:
                flag = 1

        if flag != 1:
            selected_offers_final.append(offer)

    # render the page
    context = {
        'latest_offer_list': selected_offers_final,
        'transaction_list': trans_for_user,
        'user': user,
    }

    return HttpResponse(template.render(context, request))


# renders the log in page, shows the log in form to the user
def log_in(request):
    req = request.POST
    return render(request, "polls/log_in.html")


# renders the register page, shows the register form to the user
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(request, f'Your account has been created. You can log in now!')
            return redirect('index1')
    else:
        form = UserRegistrationForm()

    context = {'form': form}
    return render(request, 'polls/register2.html', context)


# renders the update profile page, shows the update profile form to the user
def update_user(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST)

        if user_form.is_valid():
            # user_form.save()
            request.user.username = user_form.cleaned_data["username"]
            request.user.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='profile')
    else:
        user_form = UpdateUserForm(instance=request.user)

    return render(request, 'polls/update_user.html', {'form': user_form})


# renders the change password page, shows the change password form to the user
class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'polls/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('profile')


# renders the about page, shows the about page to the user
def about(request):
    req = request.POST
    return render(request, "polls/about.html")


# renders the error page when user has insufficient balance, shows the error page to the user
def err_page_balance(request):
    req = request.POST
    return render(request, "polls/err_page_balance.html")


# renders the error page when user enter invalid offer details, shows the error page to the user
def err_page_offer(request):
    req = request.POST
    return render(request, "polls/err_page_offer.html")


# renders the error page when user enter invalid payment details, shows the error page to the user
def err_page_payment(request):
    req = request.POST
    return render(request, "polls/err_page_payment.html")


# renders the offers page, shows the all offers to the user
def offers(request, curr1, curr2):
    # get the global variables when filtering
    # By default show all offers
    global curr_chosen1, curr_chosen2

    # initialise validator instance
    validator = validators()

    # get the latest offers
    latest_offer_list = Offer.objects.order_by('-publish_date')
    # get all transactions
    all_transactions = Transaction.objects.all()

    template = loader.get_template('polls/offers.html')
    selected_offers = []

    # check for sorting
    if curr1 == "all" and curr2 == "all":
        curr_chosen2 = "all"
        curr_chosen1 = "all"

        selected_offers_final = []

        # Filter already executed offers
        for offer in latest_offer_list:
            flag = 0
            for trans in all_transactions:
                if trans.offer.id == offer.id:
                    flag = 1

            # Filter already executed offers
            if flag != 1:
                if validator.time_validator(offer.expiry_date):
                    selected_offers_final.append(offer)

        context = {
            'latest_offer_list': selected_offers_final,
        }
        return HttpResponse(template.render(context, request))

    # check for sorting
    if curr1 == "all" and curr2 != "all":
        curr_chosen2 = curr2

    # check for sorting
    if curr1 != "all" and curr2 == "all":
        curr_chosen1 = curr1

    # check for sorting
    if curr1 == "all" and curr2 == "all":

        selected_offers_final = []

        # Filter already executed offers
        for offer in latest_offer_list:
            flag = 0
            for trans in all_transactions:
                if trans.offer.id == offer.id:
                    flag = 1

            # Filter already executed offers
            if flag != 1:
                if validator.time_validator(offer.expiry_date):
                    selected_offers_final.append(offer)

        context = {
            'latest_offer_list': selected_offers_final,
        }
        return HttpResponse(template.render(context, request))

    # Filter for chosen currency
    elif curr_chosen1 != "all" and curr_chosen2 == "all":
        for offer in latest_offer_list:
            if offer.currency_own == curr_chosen1:
                selected_offers.append(offer)

    # Filter for chosen currency
    elif curr_chosen1 == "all" and curr_chosen2 != "all":
        for offer in latest_offer_list:
            if offer.currency_req == curr_chosen2:
                selected_offers.append(offer)

    # Filter for chosen currency
    else:
        for offer in latest_offer_list:
            if offer.currency_own == curr_chosen1 and offer.currency_req == curr_chosen2:
                selected_offers.append(offer)

    selected_offers_final = []

    for offer in selected_offers:
        flag = 0
        # Filter already executed offers
        for trans in all_transactions:
            if trans.offer.id == offer.id:
                flag = 1

        # Filter already executed offers
        if flag != 1:
            if validator.time_validator(offer.expiry_date):
                selected_offers_final.append(offer)

    # return the selected offers
    context = {
        'latest_offer_list': selected_offers_final,
    }

    return HttpResponse(template.render(context, request))


# renders the contact page, shows the contact page to the user
def contact(request):
    req = request.POST
    return render(request, "polls/contact.html")


# renders the offer detail page, shows the details of selected offer to the user
def detail(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id)
    total = offer.amount_offered * offer.exchange_rate
    total = total - (total * FEE) / 100
    return render(request, 'polls/detail.html', {'offer': offer, 'total': round(total, 2)})


# deletes an offer the user is not redirected, stays on the profile page
def delete(request, offer_id):
    try:
        offer = Offer.objects.get(pk=offer_id)
        offer.delete()

    # stay on this page
    except ProtectedError:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    return render(request, 'polls/index1.html')


# renders the payment method page when executing offer
# shows the payment method form to the user
def payment_buy(request, offer_id):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = BuyOffer(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # get payment details
            payment_meth1 = form.cleaned_data["payment_method_get"]
            payment_meth2 = form.cleaned_data["payment_method_receive"]
            print("Offer details entered, go to payment")

            # w
            return redirect('payment_transact/' + str(payment_meth1) + "/" + str(payment_meth2) + "/")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = BuyOffer()

    context = {
        'form': form,
    }
    return render(request, 'polls/payment_buy.html', context)


# renders the update offer page, shows the update offer form to the user
def update_offer(request, offer_id):
    # get the offer to be updated
    offer = get_object_or_404(Offer, pk=offer_id)

    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        form = UpdateOfferForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # collect all of the information from the user
            # update offer details
            if form.cleaned_data['exchange_rate'] is not None:
                offer.exchange_rate = form.cleaned_data['exchange_rate']

            if form.cleaned_data['amount_offered'] is not None:
                offer.amount_offered = form.cleaned_data['amount_offered']

            new_time = offer.expiry_date.time()

            if form.cleaned_data['expiry_time'] is not None:
                new_time = form.cleaned_data['expiry_time']

            new_date = offer.expiry_date.date()
            if form.cleaned_data['expiry_date'] is not None:
                new_date = form.cleaned_data['expiry_date']

            # Update offer details
            offer.expiry_date = datetime.datetime.combine(new_date, new_time)

            offer.currency_own = all_currencies[int(form.cleaned_data['currency_own']) - 1]
            offer.currency_req = all_currencies[int(form.cleaned_data['currency_req']) - 1]

            offer.save()

            print("Offer details entered, go to payment")

            return redirect('profile')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = UpdateOfferForm()

    context = {
        'form': form,
        'offer_id': offer_id,
    }
    return render(request, 'polls/update_offer.html', context)


# renders the add offer page, shows the add offer form to the user
def add_offer(request):
    # create new offer instance
    offer = Offer()
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        form = AddOfferForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # collect the offer details from the user
            offer.currency_own = all_currencies[int(form.cleaned_data['currency_own']) - 1]
            offer.currency_req = all_currencies[int(form.cleaned_data['currency_req']) - 1]
            offer.amount_offered = form.cleaned_data['amount_offered']
            offer.exchange_rate = form.cleaned_data['exchange_rate']

            # Create fake payment method to create offer instance
            # If a user does not enter payment details, offer is discarded
            offer.payment_method = get_object_or_404(PaymentDetails, pk=1)

            offer.publish_date = datetime.datetime.now()
            offer.user_id = request.user.id

            # get the desired payment method
            payment_meth1 = form.cleaned_data["payment_method_get"]
            payment_meth2 = form.cleaned_data["payment_method_receive"]

            # get the expiry date and time of the offer
            time = form.cleaned_data['expiry_time']
            date = form.cleaned_data['expiry_date']

            # validate the offer expiry time
            offer.expiry_date = datetime.datetime.combine(date, time)
            validator = validators()

            if not validator.time_validator(expiry_time=offer.expiry_date):
                return redirect('err_page_offer')

            # save offer for now
            offer.save()

            print("Offer details entered, go to payment")

            # redirect to payment details page
            return redirect('payment/' + str(payment_meth1) + "/" + str(payment_meth2) + "/" + str(offer.id) + "/")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = AddOfferForm()

    context = {
        'form': form,
    }
    return render(request, 'polls/add_offer.html', context)


# renders a payment details page, shows the user payment details form based on the selected payment method
def payment(request, meth1, meth2, offer_id):
    # get the current offer (containing the fake payment method)
    global current_offer
    # create a validator instance
    validator = validators()

    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        # based on the payment method selected by the user get the matching form
        if meth1 == 2 and meth2 == 2:
            form = PaymentForm4(request.POST)

        elif meth1 == 2 and meth2 == 1:
            form = PaymentForm3(request.POST)

        elif meth1 == 1 and meth2 == 2:
            form = PaymentForm2(request.POST)

        else:
            form = PaymentForm1(request.POST)

        # check whether it's valid:
        if form.is_valid():

            # get details for paying, receiving with bank account
            if meth1 == 2 and meth2 == 2:
                bank_acc1 = BankAccount()
                bank_acc1.sort_code = form.cleaned_data['bank_sort_code_pay']
                bank_acc1.account_number = form.cleaned_data['bank_account_number_pay']

                bank_acc2 = BankAccount()
                bank_acc2.sort_code = form.cleaned_data['bank_sort_code_receive']
                bank_acc2.account_number = form.cleaned_data['bank_account_number_receive']

                # validate bank account information
                if not validator.bank_account_validator(bank_acc1.account_number, bank_acc1.sort_code):
                    return redirect('err_page_payment')

                if not validator.bank_account_validator(bank_acc2.account_number, bank_acc2.sort_code):
                    return redirect('err_page_payment')

                bank_acc1.save()
                bank_acc2.save()

                # in the payments detail object save fake debit card
                # the fake debit card has id=7
                debit1 = get_object_or_404(DebitCard, pk=7)
                debit2 = get_object_or_404(DebitCard, pk=7)

            # get details for paying with bank account, receiving with debit card
            elif meth1 == 2 and meth2 == 1:
                bank_acc1 = BankAccount()
                bank_acc1.sort_code = form.cleaned_data['bank_sort_code_pay']
                bank_acc1.account_number = form.cleaned_data['bank_account_number_pay']

                debit2 = DebitCard()
                time = " 00:00"
                debit2.cvv = form.cleaned_data['debit_cvv_receive']

                debit2.card_number = form.cleaned_data['debit_card_number_receive']
                debit2.expiry_date = str(form.cleaned_data['debit_expiry_date_receive']) + time

                # validate bank account/ debit card information
                if not validator.bank_account_validator(bank_acc1.account_number, bank_acc1.sort_code):
                    return redirect('err_page_payment')

                if not validator.card_validator(debit2.card_number, debit2.cvv, debit2.expiry_date):
                    return redirect('err_page_payment')

                bank_acc1.save()
                debit2.save()

                # in the payments detail object save fake debit card/ bank account
                # the fake debit card has id=7
                # the fake bank account has id=14
                bank_acc2 = get_object_or_404(BankAccount, pk=14)
                debit1 = get_object_or_404(DebitCard, pk=7)

            # get details for paying with debit card, receiving with bank account
            elif meth1 == 1 and meth2 == 2:
                debit1 = DebitCard()
                time = " 00:00"
                debit1.cvv = form.cleaned_data['debit_cvv_pay']

                debit1.card_number = form.cleaned_data['debit_card_number_pay']
                debit1.expiry_date = str(form.cleaned_data['debit_expiry_date_pay']) + time

                bank_acc2 = BankAccount()
                bank_acc2.sort_code = form.cleaned_data['bank_sort_code_receive']
                bank_acc2.account_number = form.cleaned_data['bank_account_number_receive']

                # validate bank account/ debit card information
                if not validator.bank_account_validator(bank_acc2.account_number, bank_acc2.sort_code):
                    return redirect('err_page_payment')

                if not validator.card_validator(debit1.card_number, debit1.cvv, debit1.expiry_date):
                    return redirect('err_page_payment')

                bank_acc2.save()
                debit1.save()

                # in the payments detail object save fake debit card/ bank account
                # the fake debit card has id=7
                # the fake bank account has id=14

                bank_acc1 = get_object_or_404(BankAccount, pk=14)
                debit2 = get_object_or_404(DebitCard, pk=7)

            # get details for paying/ receiving with debit card
            else:
                debit1 = DebitCard()
                time = " 00:00"
                debit1.cvv = form.cleaned_data['debit_cvv_pay']
                debit1.card_number = form.cleaned_data['debit_card_number_pay']
                debit1.expiry_date = str(form.cleaned_data['debit_expiry_date_pay']) + time

                debit2 = DebitCard()
                debit2.cvv = form.cleaned_data['debit_cvv_receive']
                debit2.card_number = form.cleaned_data['debit_card_number_receive']
                debit2.expiry_date = str(form.cleaned_data['debit_expiry_date_receive']) + time

                # validate debit card information
                if not validator.card_validator(debit1.card_number, debit1.cvv, debit1.expiry_date):
                    return redirect('err_page_payment')

                if not validator.card_validator(debit2.card_number, debit2.cvv, debit2.expiry_date):
                    return redirect('err_page_payment')

                debit1.save()
                debit2.save()

                # in the payments detail object save fake bank account
                # the fake bank account has id=14
                bank_acc1 = get_object_or_404(BankAccount, pk=14)
                bank_acc2 = get_object_or_404(BankAccount, pk=14)

            # create the payment details instance with the information proved by the user
            payment_meth = PaymentDetails()
            payment_meth.bank_account_get = bank_acc1
            payment_meth.bank_account_rec = bank_acc2
            payment_meth.debit_card_get = debit1
            payment_meth.debit_card_rec = debit2
            payment_meth.name = form.cleaned_data['full_name']
            payment_meth.save()

            # change the fake payment method in the offer to the actual one
            current_offer.payment_method = payment_meth
            # save the offer
            current_offer.save()

        # redirect to home page
        return redirect('index1')

    # if a GET (or any other method) we'll create a blank form
    else:

        # show the user the correct form, based on the chosen payment method
        if meth1 == 2 and meth2 == 2:
            form = PaymentForm4(request.POST)

        elif meth1 == 2 and meth2 == 1:
            form = PaymentForm3(request.POST)

        elif meth1 == 1 and meth2 == 2:
            form = PaymentForm2(request.POST)
        else:
            form = PaymentForm1(request.POST)

        offer = get_object_or_404(Offer, pk=offer_id)

        # save the offer as current offer
        # if no payment details are entered, the offer will be deleted

        full_offer = Offer()
        full_offer.currency_own = offer.currency_own
        full_offer.currency_req = offer.currency_req
        full_offer.amount_offered = offer.amount_offered
        full_offer.expiry_date = offer.expiry_date
        full_offer.exchange_rate = offer.exchange_rate

        full_offer.publish_date = offer.publish_date
        full_offer.user_id = offer.user_id

        offer.delete()

        current_offer = full_offer

    context = {
        'form': form,
        'meth1': meth1,
        'meth2': meth2,
    }
    return render(request, 'polls/payment.html', context)


# renders a payment transaction page when buying offer
# shows the user payment details form based on the selected payment method
def payment_transact(request, meth1, meth2, offer_id):
    # create validator instance
    validator = validators()
    # invoke the mock api for money transactions
    payment_api = MOCK_API()

    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        # based on the payment method selected by the user get the matching form
        if meth1 == 2 and meth2 == 2:
            form = PaymentForm4(request.POST)

        elif meth1 == 2 and meth2 == 1:
            form = PaymentForm3(request.POST)

        elif meth1 == 1 and meth2 == 2:
            form = PaymentForm2(request.POST)

        else:
            form = PaymentForm1(request.POST)

        # check whether it's valid:
        if form.is_valid():

            offer = get_object_or_404(Offer, pk=offer_id)
            total = offer.amount_offered * offer.exchange_rate
            total = total - (total * FEE) / 100

            # get details for paying, receiving with bank account
            if meth1 == 2 and meth2 == 2:
                bank_acc1 = BankAccount()
                bank_acc1.sort_code = form.cleaned_data['bank_sort_code_pay']
                bank_acc1.account_number = form.cleaned_data['bank_account_number_pay']

                bank_acc2 = BankAccount()
                bank_acc2.sort_code = form.cleaned_data['bank_sort_code_receive']
                bank_acc2.account_number = form.cleaned_data['bank_account_number_receive']

                # validate bank account information
                if not validator.bank_account_validator(bank_acc1.account_number, bank_acc1.sort_code):
                    return redirect('err_page_payment')

                if not validator.bank_account_validator(bank_acc2.account_number, bank_acc2.sort_code):
                    return redirect('err_page_payment')

                if not payment_api.pay_by_transfer(form.cleaned_data['full_name'],
                                                   bank_acc1.account_number,
                                                   bank_acc1.sort_code, total):
                    return redirect('err_page_balance')

                bank_acc1.save()
                bank_acc2.save()

                # in the payments detail object save fake debit card
                # the fake debit card has id=7
                debit1 = get_object_or_404(DebitCard, pk=7)
                debit2 = get_object_or_404(DebitCard, pk=7)

            # get details for paying with bank account, receiving with debit card
            elif meth1 == 2 and meth2 == 1:
                bank_acc1 = BankAccount()
                bank_acc1.sort_code = form.cleaned_data['bank_sort_code_pay']
                bank_acc1.account_number = form.cleaned_data['bank_account_number_pay']

                debit2 = DebitCard()
                time = " 00:00"
                debit2.cvv = form.cleaned_data['debit_cvv_receive']

                debit2.card_number = form.cleaned_data['debit_card_number_receive']
                debit2.expiry_date = str(form.cleaned_data['debit_expiry_date_receive']) + time

                # validate bank account/ debit card information
                if not validator.bank_account_validator(bank_acc1.account_number, bank_acc1.sort_code):
                    return redirect('err_page_payment')

                if not validator.card_validator(debit2.card_number, debit2.cvv, debit2.expiry_date):
                    return redirect('err_page_payment')

                if not payment_api.pay_by_transfer(form.cleaned_data['full_name'],
                                                   bank_acc1.account_number,
                                                   bank_acc1.sort_code, total):
                    return redirect('err_page_balance')

                bank_acc1.save()
                debit2.save()

                # in the payments detail object save fake debit card/ bank account
                # the fake debit card has id=7
                # the fake bank account has id=14
                bank_acc2 = get_object_or_404(BankAccount, pk=14)
                debit1 = get_object_or_404(DebitCard, pk=7)

            # get details for paying with debit card, receiving with bank account
            elif meth1 == 1 and meth2 == 2:
                debit1 = DebitCard()
                time = " 00:00"
                debit1.cvv = form.cleaned_data['debit_cvv_pay']

                debit1.card_number = form.cleaned_data['debit_card_number_pay']
                debit1.expiry_date = str(form.cleaned_data['debit_expiry_date_pay']) + time

                bank_acc2 = BankAccount()
                bank_acc2.sort_code = form.cleaned_data['bank_sort_code_receive']
                bank_acc2.account_number = form.cleaned_data['bank_account_number_receive']

                # validate bank account/ debit card information
                if not validator.bank_account_validator(bank_acc2.account_number, bank_acc2.sort_code):
                    return redirect('err_page_payment')

                if not validator.card_validator(debit1.card_number, debit1.cvv, debit1.expiry_date):
                    return redirect('err_page_payment')

                if not payment_api.pay_by_card(form.cleaned_data['full_name'],
                                               debit1.card_number,
                                               debit1.cvv,
                                               debit1.expiry_date, total):
                    return redirect('err_page_balance')

                bank_acc2.save()
                debit1.save()

                # in the payments detail object save fake debit card/ bank account
                # the fake debit card has id=7
                # the fake bank account has id=14

                bank_acc1 = get_object_or_404(BankAccount, pk=14)
                debit2 = get_object_or_404(DebitCard, pk=7)

            # get details for paying/ receiving with debit card
            else:
                debit1 = DebitCard()
                time = " 00:00"
                debit1.cvv = form.cleaned_data['debit_cvv_pay']
                debit1.card_number = form.cleaned_data['debit_card_number_pay']
                debit1.expiry_date = str(form.cleaned_data['debit_expiry_date_pay']) + time

                debit2 = DebitCard()
                debit2.cvv = form.cleaned_data['debit_cvv_receive']
                debit2.card_number = form.cleaned_data['debit_card_number_receive']
                debit2.expiry_date = str(form.cleaned_data['debit_expiry_date_receive']) + time

                # validate debit card information
                if not validator.card_validator(debit1.card_number, debit1.cvv, debit1.expiry_date):
                    return redirect('err_page_payment')

                if not validator.card_validator(debit2.card_number, debit2.cvv, debit2.expiry_date):
                    return redirect('err_page_payment')

                if not payment_api.pay_by_card(form.cleaned_data['full_name'],
                                               debit1.card_number,
                                               debit1.cvv,
                                               debit1.expiry_date, total):
                    return redirect('err_page_balance')

                debit1.save()
                debit2.save()

                # in the payments detail object save fake bank account
                # the fake bank account has id=14

                bank_acc1 = get_object_or_404(BankAccount, pk=14)
                bank_acc2 = get_object_or_404(BankAccount, pk=14)

            # create the payment details instance with the information proved by the user
            payment_meth = PaymentDetails()
            payment_meth.bank_account_get = bank_acc1
            payment_meth.bank_account_rec = bank_acc2
            payment_meth.debit_card_get = debit1
            payment_meth.debit_card_rec = debit2
            payment_meth.name = form.cleaned_data['full_name']
            payment_meth.save()

            # create a transaction instance with the payment methods provided
            transaction = Transaction()
            transaction.offer = offer
            transaction.payment_method_get = offer.payment_method
            transaction.payment_method_rec = payment_meth
            transaction.execution_time = datetime.datetime.now()
            transaction.user_id_rec = request.user.id

            offer_payment = offer.payment_method

            # get the bank account/ debit card by checking for the fake ids
            if offer_payment.debit_card_get.id == 7 and offer_payment.bank_account_get != 14:
                # try transacting the requested amount
                if not payment_api.pay_by_transfer(form.cleaned_data['full_name'],
                                                   bank_acc1.account_number,
                                                   bank_acc1.sort_code, offer.amount_offered):
                    # redirect to error page in case of insufficient balance
                    return redirect('err_page_balance')

            elif offer_payment.bank_account_get.id == 14 and offer_payment.debit_card_get.id != 7:
                # try transacting the requested amount
                if not payment_api.pay_by_card(form.cleaned_data['full_name'],
                                               offer_payment.debit_card_get.card_number,
                                               offer_payment.debit_card_get.cvv,
                                               offer_payment.debit_card_get.expiry_date, offer.amount_offered):
                    # redirect to error page in case of insufficient balance
                    return redirect('err_page_balance')
            else:
                # redirect to error page in case of error in the payment details
                return redirect('err_page_offer')

            # save the transaction
            transaction.save()

        return redirect('index1')

    # if a GET (or any other method) we'll create a blank form
    else:

        # show the user the correct form, based on the chosen payment method
        if meth1 == 2 and meth2 == 2:
            form = PaymentForm4(request.POST)

        elif meth1 == 2 and meth2 == 1:
            form = PaymentForm3(request.POST)

        elif meth1 == 1 and meth2 == 2:
            form = PaymentForm2(request.POST)
        else:
            form = PaymentForm1(request.POST)

    context = {
        'form': form,
        'meth1': meth1,
        'meth2': meth2,
    }
    return render(request, 'polls/payment_transact.html', context)
