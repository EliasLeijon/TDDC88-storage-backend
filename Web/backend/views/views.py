from ..serializers import AlternativeNameSerializer, StorageSerializer
from ..serializers import ArticleSerializer, OrderSerializer
from ..serializers import CompartmentSerializer, TransactionSerializer
from ..serializers import GroupSerializer

from backend.services.articleManagementService import ArticleManagementService
from backend.services.userService import UserService
from backend.services.groupManagementService import GroupManagementService
from backend.services.storageManagementService import StorageManagementService
from backend.services.orderServices import OrderService

from backend.__init__ import serviceInjector as si
from django.views import View
from django.http import Http404, JsonResponse, HttpResponseBadRequest

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from itertools import chain
from operator import itemgetter
from backend.coremodels.compartment import Compartment
from django.http import HttpResponse
from datetime import date
from datetime import datetime
import datetime
from django.utils.timezone import now


class Article(View):
    '''Article view.'''
    # Dependencies are injected, I hope that we will be able to mock
    # (i.e. make stubs of) these for testing
    @si.inject
    def __init__(self, _deps, *args):
        self.article_management_service: ArticleManagementService = (
            _deps['ArticleManagementService']())

    def get(self, request, article_id):
        '''Get.'''
        if request.method == 'GET':
            article = self.article_management_service.get_article_by_lio_id(
                article_id)
            supplier = self.article_management_service.get_supplier(article)
            supplier_article_nr = (
                self.article_management_service.get_supplier_article_nr(
                    article))
            compartments = list(article.compartment_set.all())
            alternative_names = list(article.alternativearticlename_set.all())

            if article is None:
                raise Http404("Could not find article")

            serializer = ArticleSerializer(article)

            compartment_list = []
            unit_list = []
            for i in compartments:
                compartment_serializer = CompartmentSerializer(i)
                unit_serializer = StorageSerializer(i.storage)

                compartment_list.append(compartment_serializer.data)
                unit_list.append(unit_serializer.data.get('name'))

            alt_names_list = []
            for j in alternative_names:
                alternative_names_serializer = AlternativeNameSerializer(j)
                alt_names_list.append(
                    alternative_names_serializer.data.get("name"))

            if serializer.is_valid:
                serializer_data = {}
                serializer_data.update(serializer.data)
                serializer_data["supplier"] = supplier.name
                serializer_data["supplierArticleNr"] = supplier_article_nr
                serializer_data["compartments"] = compartment_list
                serializer_data["units"] = unit_list
                serializer_data["alternative names"] = alt_names_list

                return JsonResponse(serializer_data, safe=False, status=200)
            return HttpResponseBadRequest


class Group(View):
    '''Group.'''
    # Dependencies are injected, I hope that we will be able to mock
    # (i.e. make stubs of) these for testing
    @si.inject
    def __init__(self, _deps, *args):
        self.group_management_service: GroupManagementService = (
            _deps['GroupManagementService']())

    def get(self, request, groupId):
        '''Get.'''
        if request.method == 'GET':
            group = self.group_management_service.get_group_by_id(groupId)
            if group is None:
                raise Http404("Could not find group")
            serializer = GroupSerializer(group)
    # TODO: I assume that there is supposed to be some type of return here.


class Storage(View):
    '''Storage view.'''
    # Dependencies are injected, I hope that we will be able to mock
    # (i.e. make stubs of) these for testing
    @si.inject
    def __init__(self, _deps, *args):
        self.storage_management_service: StorageManagementService = (
            _deps['StorageManagementService']())

    def get(self, request, storage_id):
        '''Return storage unit using id.'''
        if request.method == 'GET':
            storage = (
                self.storage_management_service.get_storage_by_id(
                    storage_id))
            if storage is None:
                raise Http404("Could not find storage")
            serializer = StorageSerializer(storage)
            if serializer.is_valid:
                return JsonResponse(serializer.data, status=200)
            return HttpResponseBadRequest


class Compartment(View):
    '''Storage-space view.'''

    def __init__(self, _deps, *args):
        self.order_service: OrderService = _deps['OrderService']()
        self.storage_management_service: StorageManagementService = (
            _deps['StorageManagementService']())

    def get(self, request, compartment_id):
        '''Returns compartment content as well as orders.'''
        altered_dict = (
            self.storage_management_service.get_compartment_content_and_orders(
                compartment_id))
        if altered_dict is None:
            return Http404("Could not find storage space")
        return JsonResponse(altered_dict, status=200)


class Compartment(View):
    '''Compartment view.'''
    # Dependencies are injected, I hope that we will be able to mock
    # (i.e. make stubs of) these for testing
    @si.inject
    def __init__(self, _deps, *args):
        self.storage_management_service: StorageManagementService = (
            _deps['StorageManagementService']())

    def get(self, request, qr_code):
        '''Returns compartment using qr code.'''
        if request.method == 'GET':
            compartment = (
                self.storage_management_service.get_compartment_by_qr(
                    qr_code))
            if compartment is None:
                return Http404("Could not find compartment")
            else:
                serializer = CompartmentSerializer(compartment)
                if serializer.is_valid:
                    return JsonResponse(serializer.data, status=200)
                return HttpResponseBadRequest

    def post(self, request):
        '''Post compartment.'''
        if request.method == 'POST':
            json_body = request.POST
            storage_id = json_body['storage_id']
            placement = json_body['placement']
            qr_code = json_body['qr_code']
            compartment = self.storage_management_service.create_compartment(
                storage_id, placement, qr_code
            )

        serializer = CompartmentSerializer(compartment)
        if serializer.is_valid:
            return JsonResponse(serializer.data, status=200)
        return HttpResponseBadRequest


class Order(APIView):
    '''Order view.'''
    @si.inject
    def __init__(self, _deps, *args):
        self.order_service: OrderService = _deps['OrderService']()

    def get(self, request, id):
        '''Return order using id.'''
        if request.method == 'GET':
            order = self.order_service.get_order_by_id(id)
            if order is None:
                raise Http404("Could not find order")
            serializer = OrderSerializer(order)
            if serializer.is_valid:
                return JsonResponse(serializer.data, status=200)
            return HttpResponseBadRequest

    def post(self, request, format=None):
        '''Places an order'''
        if request.method == 'POST':
            json_body = request.data
            storage_id = json_body['storageId']
            ordered_articles = json_body['articles']

            max_wait = 0
            for ordered_article in ordered_articles:
                temp = self.order_service.calculate_expected_wait(
                    article_id=ordered_article['lioNr'], amount=ordered_article['quantity'])
                if (temp > max_wait):
                    max_wait = temp

            estimated_delivery_date = datetime.datetime.now() + \
                datetime.timedelta(days=max_wait)

            print(ordered_articles)
            order = self.order_service.place_order(
                storage_id=storage_id, estimated_delivery_date=estimated_delivery_date, ordered_articles=ordered_articles)

            if order is None:
                return HttpResponseBadRequest

            for ordered_article in ordered_articles:
                article_in_order = OrderService.create_ordered_article(
                    ordered_article['lioNr'], ordered_article['quantity'], ordered_article['unit'], order)
                print(article_in_order)
                if article_in_order is None:
                    return HttpResponseBadRequest

            serializer = OrderSerializer(order)
            if serializer.is_valid:
                return JsonResponse(serializer.data, status=200)
            return HttpResponseBadRequest


class Login(APIView):
    '''Login view.'''
    # Dependencies are injected, I hope that we will be able to mock (i.e.
    # make stubs of) these for testing
    @si.inject
    def __init__(self, _deps, *args):
        self.user_service: UserService = _deps['UserService']()

    def post(self, request):
        '''Login post. Returns token.'''
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Please fill in all fields'},
                            status=status.HTTP_400_BAD_REQUEST)

        check_user = User.objects.filter(username=username).exists()
        if check_user is False:
            return Response({'error': 'Username does not exist'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user is not None:
            return self.user_service.create_auth_token(request, user)
        else:
            return Response({'error': 'invalid details'}, status=status.HTTP_400_BAD_REQUEST)


class LoginWithId(APIView):
    '''Id login view.'''
    @si.inject
    def __init__(self, _deps, *args):
        self.user_service: UserService = _deps['UserService']()

    def post(self, request):
        '''Login using id. Returns token.'''
        user_id = request.data.get('id')
        check_user = User.objects.filter(id=user_id).exists()
        if check_user is False:
            return Response({'error': 'User ID does not exist'},
                            status=status.HTTP_404_NOT_FOUND)

        user = self.user_service.authenticate_with_id(id=user_id)
        if user is not None:
            return self.user_service.create_auth_token(request, user)
        else:
            return Response({'error': 'invalid details'},
                            status=status.HTTP_400_BAD_REQUEST)


class SeeAllStorages(View):
    '''See all storages view.'''
    @si.inject
    def __init__(self, _deps, *args):
        storage_management_service = _deps['StorageManagementService']
        # Instance of dependency is created in constructor
        self.storage_management_service: StorageManagementService = (
            storage_management_service())

    def get(self, request):
        '''Returns all storages.'''
        if request.method == 'GET':
            all_storages = self.storage_management_service.get_all_storages()
            if all_storages is None:
                raise Http404("Could not find any storage units")
            else:
                return JsonResponse(list(all_storages), safe=False, status=200)


class AddInputUnit(View):
    '''Add input unit view.'''
    @si.inject
    def __init__(self, _deps):
        self.storage_management_service = _deps['StorageManagementService']
        self.user_service: UserService = _deps['UserService']()

    def post(self, request, compartment_id, amount, time_of_transaction):
        '''Post addition to storage.'''
        compartment = StorageManagementService.get_compartment_by_id(
            self=self, id=compartment_id)
        user = request.user
        if request.method == 'POST':
            if compartment is None:
                return Http404("Could not find storage space")
            StorageManagementService.add_to_storage(self=self,
                                                  id=compartment_id,
                                                  amount=amount,
                                                  username=user.username,
                                                  add_output_unit=False,
                                                  time_of_transaction=(
                                                      time_of_transaction))
            return HttpResponse(status=200)

# AddOutputUnit is used to add articles to the storage space in
# the form of single articles, or smaller parts etc.
# For example: One output unit could be one single mask or
# the article -->one meter of paper.
# Creates a transaction


class GetUserTransactions(View):
    '''Get user transactions view.'''
    @si.inject
    def __init__(self, _deps):
        self.user_service: UserService = _deps['UserService']()

    def get(self, request, user_id):
        '''Returns all transactions made by user.'''
        current_user = User.objects.filter(id=user_id)

        if current_user.exists() == False:
            return Response({'error': 'User ID does not exist'}, status=status.HTTP_404_NOT_FOUND)

        all_transactions_by_user = (
            self.user_service.get_all_transactions_by_user(
                current_user=current_user))

        if all_transactions_by_user is None:
            raise Http404("Could not find any transactions")
        else:
            return JsonResponse(list(all_transactions_by_user), safe=False, status=200)


class ReturnUnit(View):
    '''Return unit view.'''
    @si.inject
    def __init__(self, _deps):
        self.storage_management_service = _deps['StorageManagementService']
        self.user_service: UserService = _deps['UserService']()

    def post(self, request, compartment_id, amount, time_of_transaction=now):
        '''Post return to storage.'''
        compartment = StorageManagementService.get_compartment_by_id(
            self=self, id=compartment_id)
        user = request.user
        if request.method == 'POST':
            if compartment is None:
                return Http404("Could not find storage space")
            StorageManagementService.add_to_return_storage(
                                                        self=self,
                                                        id=compartment_id,
                                                        amount=amount,
                                                        username=user.username,
                                                        add_output_unit=True,
                                                        time_of_transaction=(
                                                            time_of_transaction))
            return HttpResponse(status=200)


class Transactions(APIView):
    '''Transactions API view.'''
    @si.inject
    def __init__(self, _deps):
        self.user_service: UserService = _deps['UserService']()
        self.storage_management_service: StorageManagementService = (_deps['StorageManagementService']())

    def get(self, request):
        '''Get all transactions.'''
        if request.method == 'GET':
            all_transactions = (
                self.storage_management_service.get_all_transactions())
        if all_transactions is None:
            raise Http404("Could not find any transactions")
        else:
            return JsonResponse(list(all_transactions), safe=False, status=200)

    def post(self, request):
        '''Description needed.'''
        compartment = self.storage_management_service.get_compartment_by_qr(qr_code=request.data.get("qrCode"))
        if compartment is None:
            return Response({'error': 'Could not find compartment'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            storage = self.storage_management_service.get_storage_by_id(
                id=compartment.id)
            amount = request.data.get("quantity")
            unit = request.data.get("unit")
            user = request.user
            operation = request.data.get("operation")
            time_of_transaction = request.data.get("time_of_transaction")

            if time_of_transaction == "" or time_of_transaction is None:
                time_of_transaction = date.today()

            if unit == "output":
                add_output_unit = False
            else:
                add_output_unit = True

            if operation == "replenish":
                transaction = self.storage_management_service.add_to_storage(
                    id=compartment.id, amount=amount,
                    username=user.username, add_output_unit=add_output_unit,
                    time_of_transaction=time_of_transaction)
                return JsonResponse(TransactionSerializer(transaction).data,
                                    status=200)
            elif operation == "return":
                transaction = (
                    self.storage_management_service.add_to_return_storage(
                        id=compartment.id, amount=amount,
                        username=user.username,
                        add_output_unit=add_output_unit,
                        time_of_transaction=time_of_transaction))
                return JsonResponse(TransactionSerializer(transaction).data,
                                    status=200)
            elif operation == "takeout":
                transaction = (
                    self.storage_management_service.take_from_Compartment(
                        id=compartment.id, amount=amount,
                        username=user.username,
                        add_output_unit=add_output_unit,
                        time_of_transaction=time_of_transaction))
                return JsonResponse(TransactionSerializer(transaction).data,
                                    status=200)
            elif operation == "adjust":
                transaction = (
                    self.storage_management_service.set_compartment_amount(
                        compartment_id=compartment.id, amount=amount,
                        username=user.username,
                        add_output_unit=add_output_unit,
                        time_of_transaction=time_of_transaction))
                return JsonResponse(TransactionSerializer(transaction).data,
                                    status=200)

class TransactionsById(APIView):
    '''Get transaction by ID view.'''
    @si.inject
    def __init__(self, _deps):
        StorageManagementService = _deps['StorageManagementService']
        self.storage_management_service = StorageManagementService()
        self.user_service: UserService = _deps['UserService']()

    def get(self, request, transaction_id):
        '''Get transaction.'''
        if request.method == 'GET':
            transaction = (
                self.storage_management_service.get_transaction_by_id(transaction_id))
        if transaction is None:
            raise Http404("Could not find the transaction")
        else:
            return JsonResponse(TransactionSerializer(transaction).data, safe=False, status=200)

    def put(self, request, transaction_id):
        '''Put transaction.'''
        if request.method == 'PUT':
            new_time_of_transaction = request.data.get("time_of_transaction")
            transaction = (
                self.storage_management_service.edit_transaction_by_id(transaction_id, new_time_of_transaction))

        if transaction is None:
            raise Http404("Could not find the transaction")
        else:
            return JsonResponse(TransactionSerializer(transaction).data, safe=False, status=200)
    

class GetStorageValue(View):
    '''Get storage value view.'''
    @si.inject
    def __init__(self, _deps):
        storage_management_service = _deps['StorageManagementService']
        self.storage_management_service: StorageManagementService = (
            storage_management_service())

    def get(self, request, storage_id):
        '''Get storage unit value using id.'''
        if request.method == 'GET':
            storage = self.storage_management_service.get_storage_by_id(
                storage_id)
            if storage is None:
                raise Http404("Could not find storage")
            else:
                value = self.storage_management_service.get_storage_value(
                    storage_id)
                return JsonResponse(value, safe=False, status=200)


class GetStorageCost(APIView):
    '''Get storage cost API view.'''
    @si.inject
    def __init__(self, _deps, *args):
        storage_management_service = _deps['StorageManagementService']
        self.storage_management_service: StorageManagementService = (
            storage_management_service())

    def get(self, request, storage_id):
        '''Get storage cost.'''
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        if request.method == 'GET':
            storage = self.storage_management_service.get_storage_by_id(
                storage_id)
            if storage is None:
                raise Http404("Could not find storage")
            else:
                value = self.storage_management_service.get_storage_cost(
                    storage_id, start_date, end_date)
            return JsonResponse(value, safe=False, status=200)

# Gets alternative articles for a given article. If only article id
# is entered, the method returns a list of alternative articles and all
# their attributes. If an article id and a storage id is entered, the
# method returns the id for alternative articles and the amount of
# the alternative articles in that storage


class GetArticleAlternatives(View):
    '''Get alternative article view. Gets alternative articles for a
       given article. If only article id
       is entered, the method returns a list of alternative articles and all
       their attributes. If an article id and a storage id is entered, the
       method returns the id for alternative articles and the amount of
       the alternative articles in that storage'''
    @si.inject
    def __init__(self, _deps):
        article_management_service = _deps['ArticleManagementService']
        # Instance of dependency is created in constructor
        self.storage_management_service: StorageManagementService = (
            _deps['StorageManagementService']())
        self.article_management_service: ArticleManagementService = (
            article_management_service())

    def get(self, request, article_id, storage_id=None):
        '''Get.'''
        if request.method == 'GET':

            article = self.article_management_service.get_alternative_articles(
                article_id)

            if storage_id is not None:
                storage_list = []
                dict = {'Article: ': None, 'Amount: ': None}
                for i in article:
                    dict['Article: '] = i.lio_id
                    dict['Amount: '] = (
                        self.storage_management_service.search_article_in_storage(
                            storage_id, i.lio_id))
                    storage_list.append(dict.copy())

            if article is None:
                raise Http404("Could not find article")
            else:
                if storage_id is not None:
                    return JsonResponse(list(storage_list),
                                        safe=False,
                                        status=200)
                else:
                    return JsonResponse(list(article.values()),
                                        safe=False,
                                        status=200)


# FR 8.1 start #
class SearchForArticleInStorages(View):
    '''Search for article in storages view.'''
    @si.inject
    def __init__(self, _deps):
        OrderService = _deps['OrderService']
        UserService = _deps['UserService']
        self._storage_management_service = _deps['StorageManagementService']
        self._user_service = UserService()
        self._order_service = OrderService()

    def get(self, request, search_string, input_storage) -> dict:
        '''Return articles in a given storage which matches
           Search.'''
        if request.method == 'GET':

            # Getting the storage unit which is connected
            # to the users cost center.
            user = request.user
            user_info = self._user_service.get_user_info(user.id)
            user_storage = (
                self._storage_management_service.get_storage_by_costcenter(
                    user_info.cost_center))

            # If not input storage unit is given, we assume the user wants to
            # search from it's own storage unit
            if input_storage is None:
                storage = user_storage.id
            else:
                storage = input_storage

            # NOTE: In order to increase testability and reusability I would
            # like to see already existing functions in
            # the service- / data access layer being used here. Another tip is
            # to query the "articles" variable
            # based on storage_id != storage (then duplicates will not
            # have to be removed)

            # query for the articles which match the input search string
            # and the chosen storage unit.
            articles_in_chosen_storage = Compartment.objects.filter(
                article__name__contains=search_string,
                storage_unit__id=storage).values_list(
                'article__name', 'id', 'amount', 'storage_unit__name',
                'storage_unit__floor', 'storage_unit__building')
            # query for the articles which only matches the input search
            # string in all storage units.
            articles = Compartment.objects.filter(
                article__name__contains=search_string).values_list(
                'article__name', 'id', 'amount', 'storage_unit__name',
                'storage_unit__floor', 'storage_unit__building')

            # sort the articles which does not match with
            # the chosen storage unit.
            sorted_articles = sorted(
                list(articles), key=itemgetter(5, 4))

            # chain the querysets together.
            data = list(chain(articles_in_chosen_storage, sorted_articles))

            # ugly way to remove duplicates from the data. Can't use set()
            # since order has to be preserved
            data2 = []
            for article in data:
                if article not in data2:
                    data2.append(article)

            return JsonResponse(data2, safe=False, status=200)
