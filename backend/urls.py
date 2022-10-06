from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from backend.views import views

urlPatterns = [
    path('article/<str:articleId>/', views.article.as_view()),
    path('group/<str:groupId>/', views.group.as_view()),
    path('storage/<int:storageId>/', views.storage.as_view()),
    path('order/<int:id>/', views.order.as_view()),
    path('login/', views.Login.as_view()),
    path('loginwithid/', views.LoginWithId.as_view()),
]

urlpatterns = format_suffix_patterns(urlPatterns)
