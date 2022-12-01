from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from backend.views import views
from backend.views import userView
from django.views.decorators.csrf import csrf_exempt
'''Rearranged according to API documentation'''

urlPatterns = [
    # Authentication
    path('loginWithCredentials', views.LoginWithCredentials.as_view()),
    path('loginWithBarcode', views.LoginWithBarcodeOrNfc.as_view()),
    path('loginWithNFC', views.LoginWithBarcodeOrNfc.as_view()),

    # User
    path('users', userView.User.as_view()),
    path('users/<user_id>', userView.UserId.as_view()),

    # This is not a part of the API
    path('user/<int:user_id>/transactions',
         views.GetUserTransactions.as_view()),

    # Notifications
    #   path('/notifications/<order_id>') part of API, not yet implemented

    # Articles
    path('articles/', views.GetArticles.as_view()),
    path('articles/lio/<str:article_id>', views.Article.as_view()),
    path('articles/qr/<str:qr_code>', views.Article.as_view()),
    path('articles/name/<str:name>', views.Article.as_view()),

    # article URLs below not part of API
    path('alternativearticles/<str:article_id>',
         views.GetArticleAlternatives.as_view()),
    path('alternativearticles/<str:article_id>/<str:storage_id>',
         views.GetArticleAlternatives.as_view()),

    # Storages
    path('storages', views.SeeAllStorages.as_view()),
    path('storages/<int:storage_id>', views.Storage.as_view()),
    path('nearbyStorages/<str:qr_code>', views.NearbyStorages.as_view()),

    # Below storage URLs not part of API
    path('storage/<str:storage_id>/value', views.GetStorageValue.as_view()),
    path('storage/<str:storage_id>/cost', views.GetStorageCost.as_view()),

    # Compartments
    path('compartments', views.Compartments.as_view()),
    path('compartments/<str:qr_code>', views.Compartments.as_view()),
    path('connectArticleToCompartment/<str:qr_code>', (
        views.ArticleToCompartmentByQRcode.as_view())),
    path('moveArticle', views.MoveArticle.as_view()),

    # Transactions
    path('transactions', views.Transactions.as_view()),
    path('transactions/<int:transaction_id>',
         views.TransactionsById.as_view()),

    # Transaction URLs below, not part of API.
    path('transactions/addinputunit/<str:compartment_id>/<int:amount>',
         csrf_exempt(views.AddInputUnit.as_view())),
    path('transactions/addoutputunit/<str:compartment_id>/<int:amount>',
         csrf_exempt(views.AddInputUnit.as_view())),
    path('transactions/returnunit/<str:compartment_id>/<int:amount>',
         views.ReturnUnit.as_view()),

    # Orders
    path('orders', views.Order.as_view()),
    path('orders/<int:id>', views.OrderId.as_view()),

    # Economy (no URLS implemented yet)
    path('economy/<storage_id>', views.getEconomy.as_view()),

    # grup is not part if API? Delete?
    path('group/<str:groupId>', views.Group.as_view()),

]

urlpatterns = format_suffix_patterns(urlPatterns)