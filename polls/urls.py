from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views
from . import views
from .views import CustomLoginView
from .views import ChangePasswordView

# Define 404 page for handling unexpected errors
#handler404 = 'polls.views.custom_page_not_found_view'

# Define all paths in our application and link the to the views
urlpatterns = [
    path('', views.index_new, name='index1'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('offers/<str:curr1>/<str:curr2>/', views.offers, name='offers'),
    path('<int:offer_id>/', views.detail, name='detail'),
    path('register/', views.register, name='register'),
    path('login/', CustomLoginView.as_view(template_name='polls/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='polls/logout.html'), name='logout'),
    path('add_offer/', views.add_offer, name='add_offer'),
    path('add_offer/payment/<int:meth1>/<int:meth2>/<int:offer_id>/', views.payment, name='payment'),
    path('payment_buy/<int:offer_id>/payment_transact/<int:meth1>/<int:meth2>/', views.payment_transact, name='payment_transact'),
    path('payment_buy/<int:offer_id>/', views.payment_buy, name='payment_buy'),
    path('profile/', views.profile, name='profile'),
    path('delete/<int:offer_id>/', views.delete, name='delete'),
    path('logout_view/', views.logout_view, name='logout_view'),
    path('profile/update_user/', views.update_user, name='update_user'),

    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('update_offer/<int:offer_id>/', views.update_offer, name='update_offer'),
    path('err_page_balance/', views.err_page_balance, name='err_page_balance'),
    path('err_page_offer/', views.err_page_offer, name='err_page_offer'),
    path('err_page_payment/', views.err_page_payment, name='err_page_payment'),

]

urlpatterns += staticfiles_urlpatterns()
