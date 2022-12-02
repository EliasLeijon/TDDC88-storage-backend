from django.contrib import admin
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from backend.coremodels.alternative_article_name import AlternativeArticleName
from backend.coremodels.article import Article
from backend.coremodels.centralStorageSpace import CentralStorageSpace
from backend.coremodels.storage import Storage
from backend.coremodels.cost_center import CostCenter
from backend.coremodels.compartment import Compartment
from backend.coremodels.supplier import Supplier
from backend.coremodels.transaction import Transaction
from backend.coremodels.order import Order
from backend.coremodels.user_info import UserInfo
from backend.coremodels.article import GroupInfo


# Register your models here.
# admin.site.register(storage)
admin.site.register(CostCenter)


# Displays cost center as an option in the user class


class UserInfoInLine(admin.StackedInline):
    model = UserInfo


class UserGroupInLine(admin.StackedInline):
    model = Group


class UserAdmin(BaseUserAdmin):
    inlines = (UserInfoInLine, )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
#######################################################

# Register your models here.
# admin.site.register(Article)

admin.site.register(Compartment)


# Displays all articles in the group
class ArticleAdminInline(admin.TabularInline):
    model = Article.article_group.through


class GroupAdmin(admin.ModelAdmin):
    inlines = (ArticleAdminInline, )


admin.site.register(GroupInfo, GroupAdmin)
#######################################################


admin.site.register(Supplier)

# Displays which storage components that the articles are in,
# the supplier that the article has and its alternative names


class CompartmentInline(admin.TabularInline):
    model = Compartment


class AlternativeNameInLine(admin.TabularInline):
    model = AlternativeArticleName


class ArticleAdmin(admin.ModelAdmin):
    inlines = (CompartmentInline,
               AlternativeNameInLine, )


admin.site.register(Article, ArticleAdmin)
########################################################


class StorageAdmin(admin.ModelAdmin):
    inlines = (CompartmentInline, )


# Display QRCode in Backend
admin.site.register(Storage, StorageAdmin)

admin.site.register(Order)
admin.site.register(CentralStorageSpace)


########################################################


# Display Transaction in Backend
class TransactioInline(admin.TabularInline):
    model = Transaction


admin.site.register(Transaction)
