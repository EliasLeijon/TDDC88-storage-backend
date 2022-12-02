from ..serializers import *

from backend.services.articleManagementService import ArticleManagementService
from backend.services.userService import UserService
from backend.services.groupManagementService import GroupManagementService
from backend.services.storageManagementService import StorageManagementService
from backend.services.orderServices import OrderService

from backend.__init__ import serviceInjector as si
from django.http import Http404, JsonResponse, HttpResponseBadRequest
from django.core.exceptions import PermissionDenied

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny

from knox.models import AuthToken
from rdxSolutionsBackendProject.settings import SALT

from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.http import HttpResponse
from itertools import chain
from operator import itemgetter
from backend.coremodels.compartment import Compartment
from datetime import date
from datetime import datetime
import datetime
from django.utils.timezone import now


# from Web.backend import serializers


class Article(APIView):
    '''Article view.'''
    # Dependencies are injected, I hope that we will be able to mock
    # (i.e. make stubs of) these for testing

    @si.inject
    def __init__(self, _deps, *args):
        self.article_management_service: ArticleManagementService = (
            _deps['ArticleManagementService']())
        self.storage_management_service: StorageManagementService = (
            _deps['StorageManagementService']())

    def get(self, request, article_id=None, qr_code=None, name=None):
        '''Get.'''
        if request.method == 'GET':
           # A user can get articles if they have permission
            if not request.user.has_perm('backend.view_article_perm'):
                raise PermissionDenied
            
            if article_id != None:
                article = self.article_management_service.get_article_by_lio_id(
                    article_id)
            elif qr_code != None:
                article = self.storage_management_service.get_article_in_compartment(
                    qr_code)
            elif name != None:
                article = self.article_management_service.get_article_by_name(
                    name)
            
            if article is None:
                raise Http404("Could not find article")
            serialized_article = ApiArticleSerializer(article).data
            storage_id = request.GET.get('storageId', None)
            if (storage_id is not None):
                storage = self.storage_management_service.get_storage_by_id(
                    storage_id)
                if storage is None:
                    return Response({'Storage {} does not exist'.format(storage_id)}, status=status.HTTP_400_BAD_REQUEST)
                serialized_article['compartments'] = (
                    ArticleCompartmentProximitySerializer(
                        article=article, storage=storage)).data
            return JsonResponse(serialized_article, status=200)


class Group(APIView):
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
            # A user can see a group if they have permission
            if not request.user.has_perm('backend.view_group_perm'):
                raise PermissionDenied
            group = self.group_management_service.get_group_by_id(groupId)
            if group is None:
                raise Http404("Could not find group")
            serializer = GroupSerializer(group)
    # TODO: I assume that there is supposed to be some type of return here.


class Storage(APIView):
    '''Storage view.'''
    # Dependencies are injected, I hope that we will be able to mock
    # (i.e. make stubs of) these for testing

    @si.inject
    def __init__(self, _deps, *args):
        self.storage_management_service: StorageManagementService = (
            _deps['StorageManagementService']())

    def get(self, request, storage_id):
        '''Return storage unit using id.'''
            # A user can see a storage if they have permission
        if not request.user.has_perm('backend.view_storage_perm'):
            raise PermissionDenied
        storage = (self.storage_management_service.get_storage_by_id(
            storage_id))
        if storage is None:
            raise Http404("Could not find storage")

        serializer = StorageSerializer(storage)
        if serializer.is_valid:
            return Response(serializer.data, status=200)
        return Response('serialization failed', status=status.HTTP_400_BAD_REQUEST)


class NearbyStorages(APIView):
    '''Get nearby storages.'''

    @si.inject
    def __init__(self, _deps, *args):
        self.storage_management_service: StorageManagementService = (
            _deps['StorageManagementService']())

    def get(self, request, qr_code):
        '''Return nearby storages of the storage which
        contains the qr_code with a
        specific qr_code'''
        if request.method == 'GET':
            # A user can see nearby storages if they have permission
            if not request.user.has_perm('backend.view_storage_perm'):
                raise PermissionDenied
            nearby_compartments = list((
                self.storage_management_service.get_nearby_storages(
                    qr_code)).values())
            if nearby_compartments is None:
                raise Http404("Could not find any nearby storages")
            serializer = NearbyStoragesSerializer(nearby_compartments,
                                                  read_only=True,
                                                  many=True)
            if serializer.is_valid:
                return JsonResponse(serializer.data, status=200, safe=False)
            return HttpResponseBadRequest


class Compartments(APIView):
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
            # A user can see compartments if they have permission
            if not request.user.has_perm('backend.view_compartment_perm'):
                raise PermissionDenied
            compartment = (
                self.storage_management_service.get_compartment_by_qr(
                    qr_code))
            if compartment is None:
                raise Http404("Could not find compartment")
            else:
                serializer = ApiCompartmentSerializer(compartment)
                if serializer.is_valid:
                    return JsonResponse(serializer.data, status=200)
                return HttpResponseBadRequest

    def post(self, request):
        '''Post compartment.'''
        if request.method == 'POST':
            # A user can add a compartment if they have permission
            if not request.user.has_perm('backend.add_compartment'):
                raise PermissionDenied
            try:
                json_body = request.data
                storage_id = json_body['storageId']
                placement = json_body['placement']
                qr_code = json_body['qrCode']
            except:
                return Response({'JSON payload not correctly formatted'}, status=status.HTTP_400_BAD_REQUEST)

        compartment = self.storage_management_service.create_compartment(
            storage_id, placement, qr_code)

        if compartment is None:
            return Response({'Compartment could not be created'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ApiCompartmentSerializer(compartment)
        if serializer.is_valid:
            return JsonResponse(serializer.data, status=200)
        return Response({'Serialization failed'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, qr_code):
        '''Edit compartment by QR code.'''

        current_compartment = (
            self.storage_management_service.get_compartment_by_qr(qr_code))

        if current_compartment is not None:

            # Get values from payload
            new_placement = request.data.get("placement")
            new_storage_id = request.data.get("storageId")
            new_amount = request.data.get('quantity')
            new_standard_order_amount = request.data.get('normalOrderQuantity')
            new_order_point = request.data.get('orderQuantityLevel')

            self.storage_management_service.update_compartment_by_qr(
                current_compartment, new_placement, new_storage_id, new_amount, new_standard_order_amount, new_order_point)

            return JsonResponse(ApiCompartmentSerializer(current_compartment).data, status=200)

        else:
            return Response({'error': 'Could not find compartment'},
                            status=status.HTTP_400_BAD_REQUEST)


class Order(APIView):
    '''Order endpoint handling all request from /orders'''

    @si.inject
    def __init__(self, _deps, *args):
        self.order_service: OrderService = _deps['OrderService']()
        self.article_management_service: ArticleManagementService = _deps['ArticleManagementService'](
        )

    def get(self, request):
        '''Returns all orders)'''
        # A user can view orders if they have permission
        if not request.user.has_perm('backend.view_order_perm'):
            raise PermissionDenied

        orders = self.order_service.get_orders()
        if orders is None:
            return Response({'No orders found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(orders, many=True)

        if serializer.is_valid:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'Serialization failed'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        '''Places an order'''
        if request.method == 'POST':
            # A user can add an order if they have permission for it
            if not request.user.has_perm('backend.add_order_perm'):
                raise PermissionDenied
            json_body = request.data
            try:
                storage_id = json_body['storageId']
                ordered_articles = json_body['articles']
            except:
                return Response({'JSON payload not correctly formatted'}, status=status.HTTP_400_BAD_REQUEST)

            max_wait = 0
            for ordered_article in ordered_articles:
                temp = self.order_service.calculate_expected_wait(
                    article_id=ordered_article['lioNr'], amount=ordered_article['quantity'])
                if temp is None:
                    return Response({'Article not in central storage'}, status=status.HTTP_400_BAD_REQUEST)
                if (temp > max_wait):
                    max_wait = temp

            estimated_delivery_date = datetime.datetime.now() + \
                datetime.timedelta(days=max_wait)

            order = self.order_service.place_order(
                storage_id=storage_id, estimated_delivery_date=estimated_delivery_date, ordered_articles=ordered_articles)

            if order is None:
                return Response({'Order could not be placed'}, status=status.HTTP_400_BAD_REQUEST)

            for ordered_article in ordered_articles:
                ord_art = OrderService.create_ordered_article(
                    ordered_article['lioNr'], ordered_article['quantity'], ordered_article['unit'], order)
                if ord_art is None:
                    return Response({'Article does not exist'}, status=status.HTTP_404_NOT_FOUND)
            serialized_order = OrderSerializer(order)
            if serialized_order.is_valid:
                return Response(serialized_order.data, status=200)
            return Response({'Serialization failed'}, status=status.HTTP_400_BAD_REQUEST)


class OrderId(APIView):
    '''Order Endpoint which handles all request coming from /orders/id'''

    @si.inject
    def __init__(self, _deps, *args):
        self.order_service: OrderService = _deps['OrderService']()
        self.article_management_service: ArticleManagementService = _deps['ArticleManagementService'](
        )

    def get(self, request, id):
        order = self.order_service.get_order_by_id(id)
        if order is None:
            return Response({'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        serialized_order = OrderSerializer(order)
        if serialized_order.is_valid:
            return Response(serialized_order.data, status=200)
        return Response({'Serialization failed'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        '''Alters the state of an order to delivered and updates the amount in the correct compartments.'''
        json_body = request.data
        try:
            order_state = json_body['state']
        except:
            return Response({'JSON payload not correctly formatted'}, status=status.HTTP_400_BAD_REQUEST)

        order = self.order_service.get_order_by_id(id)
        if order is None:
            return Response({'Order does not exist'}, status=status.HTTP_404_NOT_FOUND)
        current_state = order.order_state

        if current_state == 'delivered' and order_state == 'delivered' or current_state == 'order placed' and order_state == 'order placed':
            return Response({'This order has already been handled'}, status=status.HTTP_400_BAD_REQUEST)

        elif current_state == 'delivered' and order_state == 'order placed':
            return Response({'You are not allowed to alter an order in this way'}, status=status.HTTP_400_BAD_REQUEST)

        elif current_state == 'order placed' and order_state == 'delivered':
            updated_order = self.order_service.order_arrived(id)

        else:
            return Response({'Somthing went wrong'}, status=status.HTTP_400_BAD_REQUEST)

        if updated_order is None:
            return Response({'Order could not be updated'}, status=status.HTTP_400_BAD_REQUEST)

        serialized_order = OrderSerializer(updated_order)
        if serialized_order.is_valid:
            return Response(serialized_order.data, status=200)
        return Response({'Serialization failed'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        '''Delete order func'''
        order = self.order_service.get_order_by_id(id)
        if order is None:
            return Response({'Order does not exist. Cannot be deleted'}, status=status.HTTP_404_NOT_FOUND)

        deleted_order = self.order_service.delete_order(id, order.order_state)
        if deleted_order is None:
            return Response({'Order deletion failed'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginWithCredentials(APIView):
    '''Login a user using credentials username and password and returns
    the user along with bearer auth token'''
    permission_classes = [AllowAny]

    @si.inject
    def __init__(self, _deps, *args):
        self.user_service: UserService = _deps['UserService']()

    def post(self, request):
        '''Login a user using credentials username and password. 
        returns User along with auth token'''
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            raise AuthenticationFailed

        auth = authenticate(username=username, password=password)
        if auth is None:
            raise AuthenticationFailed

        login(request, auth)

        user = self.user_service.get_user_info(request.user)
        serialized_user = UserInfoSerializer(user)
        data = {
            "user": serialized_user.data,
            "token": AuthToken.objects.create(auth)[1]
        }
        return JsonResponse(data, status=status.HTTP_200_OK)


class LoginWithBarcodeOrNfc(APIView):
    '''Login a user using either barcode or NFC to authenticate user.
    Returns the user along with bearer auth token'''
    permission_classes = [AllowAny]

    @si.inject
    def __init__(self, _deps, *args):
        self.user_service: UserService = _deps['UserService']()

    def post(self, request):
        '''Login a user using either barcode or NFC.
        returns User along with auth token'''
        # body = request.data
        barcode_id = request.data.get('barcodeId')
        nfc_id = request.data.get('nfcId')
        if barcode_id is None and nfc_id is None:
            raise AuthenticationFailed

        if barcode_id is not None:
            check_barcode = make_password(barcode_id, SALT)
            user = self.user_service.get_user_with_barcode(
                barcode_id=check_barcode)
        elif nfc_id is not None:
            check_nfc = make_password(nfc_id, SALT)
            user = self.user_service.get_user_with_nfc(nfc_id=check_nfc)

        if user is None:
            raise AuthenticationFailed

        auth = user.user

        login(request, auth)
        serialized_user = UserInfoSerializer(user)
        data = {
            "user": serialized_user.data,
            "token": AuthToken.objects.create(auth)[1]
        }
        return JsonResponse(data, status=status.HTTP_200_OK)


class SeeAllStorages(APIView):
    '''See all storages view.'''

    @si.inject
    def __init__(self, _deps, *args):
        storage_management_service = _deps['StorageManagementService']
        # Instance of dependency is created in constructor
        self.storage_management_service: StorageManagementService = (
            storage_management_service())

    def get(self, request):
        '''Returns all storages.'''
        # A user can see all storages if they have permission
        if not request.user.has_perm('backend.view_storage_perm'):
            raise PermissionDenied

        all_storages = self.storage_management_service.get_all_storages()
        if all_storages is None:
            raise Http404("Could not find any storage units")

        serializer = StorageSerializer(all_storages, many=True)
        if serializer.is_valid:
            return Response(serializer.data, status=200)
        return Response('serialization failed', status=status.HTTP_400_BAD_REQUEST)

        # return JsonResponse(list(all_storages), safe=False, status=200)


class AddInputUnit(APIView):
    '''Add input unit view.'''

    @si.inject
    def __init__(self, _deps):
        self.storage_management_service = _deps['StorageManagementService']
        self.user_service: UserService = _deps['UserService']()

    def post(self, request, compartment_id, amount, time_of_transaction):
        '''Post addition to storage.'''
        # Custom permission to be able to add a input unit. Can be found in the coremodel storage.py
        if not request.user.has_perm('backend.add_input_unit'):
            raise PermissionDenied
        compartment = StorageManagementService.get_compartment_by_id(
            self=self, id=compartment_id)
        user = request.user
        if request.method == 'POST':
            if compartment is None:
                raise Http404("Could not find storage space")
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


class GetUserTransactions(APIView):
    '''Get user transactions view.'''

    @si.inject
    def __init__(self, _deps):
        self.user_service: UserService = _deps['UserService']()

    def get(self, request, user_id):
        '''Returns all transactions made by user.'''
        # Custom permission to be able to see a users transactions. Can be found in the coremodel transaction.py
        if not request.user.has_perm('backend.get_user_transactions'):
            raise PermissionDenied
        current_user = User.objects.filter(id=user_id)

        if current_user is not None:
            all_transactions_by_user = (
                self.user_service.get_all_transactions_by_user(
                    current_user=current_user))

            if all_transactions_by_user is not None:
                return JsonResponse(list(all_transactions_by_user),
                                    safe=False, status=200)
            else:  # Exception
                return Response({'error': 'Could not find any transactions'},
                                status=status.HTTP_404_NOT_FOUND)
        else:  # Exception
            return Response({'error': 'Could not find user'},
                            status=status.HTTP_404_NOT_FOUND)


class ReturnUnit(APIView):
    '''Return unit view.'''

    @si.inject
    def __init__(self, _deps):
        self.storage_management_service = _deps['StorageManagementService']
        self.user_service: UserService = _deps['UserService']()

    def post(self, request, compartment_id, amount, time_of_transaction=now):
        '''Post return to storage.'''
        # A user can return to storage if they have permission
        if not request.user.has_perm('backend.return_to_storage'):
            raise PermissionDenied
        compartment = StorageManagementService.get_compartment_by_id(
            self=self, id=compartment_id)
        user = request.user
        if request.method == 'POST':
            if compartment is None:
                raise Http404("Could not find storage space")
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
        self.storage_management_service: StorageManagementService = (
            _deps['StorageManagementService']())

    def get(self, request):
        '''Get all transactions.'''
        if request.method == 'GET':
            # Custom permission to be able to see all transactions. Can be found in the coremodel transaction.py
            if not request.user.has_perm('backend.get_all_transaction'):
                raise PermissionDenied
            fromDate = request.query_params.get('fromDate', None)
            toDate = request.query_params.get('toDate', None)
            limit = request.query_params.get('limit', None)
            all_transactions = (
                self.storage_management_service.get_all_transactions(fromDate=fromDate, toDate=toDate, limit=limit))
        if all_transactions is None:
            raise Http404("Could not find any transactions")
        else:
            serializer = TransactionSerializer(all_transactions, many=True)

            return JsonResponse(serializer.data, safe=False, status=200)

    def post(self, request):
        '''Create new Transaction.'''
        if not request.user.has_perm('backend.add_transaction_perm'):
            raise PermissionDenied
        compartment = self.storage_management_service.get_compartment_by_qr(
            qr_code=request.data.get("qrCode"))
        storage = self.storage_management_service.get_storage_by_id(
            request.data.get('storageId'))
        if compartment is None:
            return Response({'error': 'Could not find compartment'},
                            status=status.HTTP_400_BAD_REQUEST)
        elif storage is None:
            return Response({'error': 'Could not find storage'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:

            amount = request.data.get("quantity")
            unit = request.data.get("unit")
            user = request.user
            operation = request.data.get("operation")
            time_of_transaction = request.data.get("time_of_transaction")

            if time_of_transaction == "" or time_of_transaction is None:
                time_of_transaction = date.today()

            if unit == "input":
                add_output_unit = False
            else:
                add_output_unit = True

            if operation == "replenish":
                if not request.user.has_perm('backend.replenish'):
                    raise PermissionDenied
                if (compartment.maximal_capacity - compartment.amount - amount) < 0 and add_output_unit:
                    return Response({'error': 'Not enough space in the compartment.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                elif (compartment.maximal_capacity - amount*compartment.article.output_per_input - compartment.amount) < 0 and add_output_unit == False:
                    return Response({'error': 'Not enough space in the compartment.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    transaction = self.storage_management_service.add_to_storage(
                        id=compartment.id, storage_id=storage, amount=amount,
                        username=user.username, add_output_unit=add_output_unit,
                        time_of_transaction=time_of_transaction)
                    return JsonResponse(TransactionSerializer(transaction).data,
                                        status=200)
            elif operation == "return":
                if (compartment.maximal_capacity - compartment.amount - amount) < 0 and add_output_unit:
                    return Response({'error': 'Not enough space in the compartment.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                elif (compartment.maximal_capacity - amount*compartment.article.output_per_input - compartment.amount) < 0 and add_output_unit == False:
                    return Response({'error': 'Not enough space in the compartment.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    transaction = (
                        self.storage_management_service.add_to_return_storage(
                            id=compartment.id, storage_id=storage, amount=amount,
                            username=user.username,
                            add_output_unit=add_output_unit,
                            time_of_transaction=time_of_transaction))
                    return JsonResponse(TransactionSerializer(transaction).data,
                                        status=200)
            elif operation == "takeout":
                if (compartment.amount - amount) < 0 and add_output_unit:
                    return Response({'error': 'Not enough articles in the compartment.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                elif (compartment.amount - amount*compartment.article.output_per_input) < 0 and add_output_unit == False:
                    return Response({'error': 'Not enough articles in the compartment.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    transaction = (
                        self.storage_management_service.take_from_Compartment(
                            id=compartment.id, storage_id=storage, amount=amount,
                            username=user.username,
                            add_output_unit=add_output_unit,
                            time_of_transaction=time_of_transaction))
                    return JsonResponse(TransactionSerializer(transaction).data,
                                        status=200)
            elif operation == "adjust":
                if (compartment.maximal_capacity - amount) < 0 and add_output_unit:
                    return Response({'error': 'Not enough space in the compartment.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                elif (compartment.maximal_capacity - amount*compartment.article.output_per_input) < 0 and add_output_unit == False:
                    return Response({'error': 'Not enough space in the compartment.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    transaction = (
                        self.storage_management_service.set_compartment_amount(
                            compartment_id=compartment.id, storage_id=storage, amount=amount,
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
            # Custom permission to be able to get transactiopns by id. Can be found in the coremodel transaction.py
            if not request.user.has_perm('backend.get_transaction_by_id'):
                raise PermissionDenied
            transaction = (
                self.storage_management_service.get_transaction_by_id(transaction_id))
        if transaction is None:
            raise Http404("Could not find the transaction")
        else:
            return JsonResponse(TransactionSerializer(transaction).data, safe=False, status=200)

    def put(self, request, transaction_id):
        '''Put transaction.'''
        if request.method == 'PUT':
            # Can only change a transaction if they have the permission
            if not request.user.has_perm('backend.change_transaction_perm'):
                raise PermissionDenied
            new_time_of_transaction = request.data.get("timeStamp")
            transaction = (
                self.storage_management_service.edit_transaction_by_id(transaction_id, new_time_of_transaction))

        if transaction is None:
            raise Http404("Could not find the transaction")
        else:
            return JsonResponse(TransactionSerializer(transaction).data, safe=False, status=200)


class GetStorageValue(APIView):
    '''Get storage value view.'''
   # authentication_classes = (TokenAuthentication,)

    @si.inject
    def __init__(self, _deps):
        storage_management_service = _deps['StorageManagementService']
        self.storage_management_service: StorageManagementService = (
            storage_management_service())

    def get(self, request, storage_id):
        '''Get storage unit value using id.'''
        if request.method == 'GET':
            # Custom permission to be able to see storage value. Can be found in the coremodel storage.py
            if not request.user.has_perm('backend.get_storage_value'):
                raise PermissionDenied
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
        start_date = "2010-11-16T15:09:57.028Z"
        end_date = "2023-11-16T15:09:57.028Z"
        if request.method == 'GET':
            # Custom permission to be able to see storage cost. Can be found in the coremodel storage.py
            if not request.user.has_perm('backend.get_storage_cost'):
                raise PermissionDenied
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


class GetArticleAlternatives(APIView):
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
            # If a user can view articles, then they can get their alternative articles
            if not request.user.has_perm('backend.view_article_perm'):
                raise PermissionDenied
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
class SearchForArticleInStorages(APIView):
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
            # If a user has permission to view articles, then they can search for them
            if not request.user.has_perm('backend.view_article_perm'):
                raise PermissionDenied
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


class ArticleToCompartmentByQRcode(APIView):
    '''Change Article linked to Compartment by using QR code.'''

    @si.inject
    def __init__(self, _deps):
        self.storage_management_service: StorageManagementService = (
            _deps['StorageManagementService']())
        self.article_management_service: ArticleManagementService = (
            _deps['ArticleManagementService']())

    def put(self, request, qr_code):
        '''Sets new article in payload to compartment matching qr_code.'''

        current_compartment = (
            self.storage_management_service.get_compartment_by_qr(
                qr_code=qr_code))

        if current_compartment is not None:
            article_id = request.data.get("lioNr")
            new_article = (
                self.article_management_service.get_article_by_lio_id((
                    article_id)))

            if new_article is not None:
                # Get attributes from payload
                new_amount = request.data.get("quantity")
                new_standard_order_amount = request.data.get(
                    ("normalOrderQuantity"))
                new_order_point = request.data.get("orderQuantityLevel")

                is_compartment_large_enough = self.storage_management_service.is_compartment_large_enough(
                    current_compartment, new_amount)

                if is_compartment_large_enough:
                    # Updates attributes in compartment
                    self.storage_management_service.update_compartment(
                        current_compartment, new_article, new_amount, new_standard_order_amount, new_order_point)

                    return JsonResponse(ApiCompartmentSerializer
                                        (current_compartment).data)
                else:  # Exception
                    return Response({'error': 'Quantity more than maximal capacity'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:  # Exception
                return Response({'error': 'Could not find article'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:  # Exception
            return Response({'error': 'Could not find compartment'},
                            status=status.HTTP_400_BAD_REQUEST)


class getEconomy(APIView):
    '''Returns the total value in storage, and the average turnover rate'''
   # authentication_classes = (TokenAuthentication,)

    @si.inject
    def __init__(self, _deps, *args):
        storage_management_service = _deps['StorageManagementService']
        self.storage_management_service: StorageManagementService = (
            storage_management_service())

    def get(self, request, storage_id):
        '''Takes the storage_id from the url'''
        storage = self.storage_management_service.get_storage_by_id(
            storage_id)
        if storage is None:
            raise Http404("Could not find storage")
        else:
            start_date = datetime.date(datetime.datetime.today(
            ).year-1, datetime.datetime.today().month, datetime.datetime.today().day)
            end_date = datetime.datetime.today()

            value = self.storage_management_service.get_storage_value(
                storage_id)
            turnover_rate = self.storage_management_service.get_storage_turnover_rate(
                storage_id, start_date, end_date)
            data = {}
            data["totalValue"] = value
            data["averageTurnoverRate"] = turnover_rate
            return JsonResponse(data, safe=False, status=200)


class MoveArticle(APIView):
    '''Move an amount of a specific article from one compartment to another one.
        This will create two transactions, one for the withdrawal and one for the deposit.'''

    @si.inject
    def __init__(self, _deps, *args):
        storage_management_service = _deps['StorageManagementService']
        self.storage_management_service: StorageManagementService = (
            storage_management_service())
        self.user_service: UserService = _deps['UserService']()

    def post(self, request):
        data = request.data.get
        from_compartment_qr_code = data('fromCompartmentQrCode')
        to_compartment_qr_code = data('toCompartmentQrCode')
        unit = data('unit')
        quantity = data('quantity')
        user = request.user

        if request.method == 'POST':
            if not request.user.has_perm('backend.move_article'):
                raise PermissionDenied

            from_compartment = self.storage_management_service.get_compartment_by_qr(
                from_compartment_qr_code)
            to_compartment = self.storage_management_service.get_compartment_by_qr(
                to_compartment_qr_code)

            if unit == "output":
                add_output_unit = True
                converter = 1
            elif unit == "input":
                add_output_unit = False
                converter = from_compartment.article.output_per_input

            if from_compartment is None or to_compartment is None:
                return Response({'error': 'Could not find compartment'},
                                status=status.HTTP_400_BAD_REQUEST)

            if (from_compartment.amount-quantity) < 0:
                return Response({'error': 'Not enough articles in compartment'},
                                status=status.HTTP_400_BAD_REQUEST)

            if from_compartment.article.lio_id != to_compartment.article.lio_id:
                return Response({'error': 'Not matching articles'},
                                status=status.HTTP_400_BAD_REQUEST)

            if (from_compartment.amount - quantity*converter) < 0 or (to_compartment.amount + quantity*converter) > to_compartment.maximal_capacity:
                return Response({'error': 'Not allowed quantity, not enough in storage or not enough space in target'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                time_of_transaction = date.today()

                from_transaction = (
                    self.storage_management_service.take_from_Compartment(
                        id=from_compartment_qr_code, storage_id=from_compartment.storage, amount=quantity,
                        username=user.username,
                        add_output_unit=add_output_unit,
                        time_of_transaction=time_of_transaction))

                to_transaction = (
                    self.storage_management_service.add_to_return_storage(
                        id=to_compartment_qr_code, storage_id=to_compartment.storage, amount=quantity,
                        username=user.username,
                        add_output_unit=add_output_unit,
                        time_of_transaction=time_of_transaction))
                '''Prints JsonResponse directly instead of using Serializer'''
                data = {}
                data['userId'] = str(user.id)
                data['timeStamp'] = to_transaction.time_of_transaction
                data['fromCompartmentQrCode'] = from_compartment_qr_code
                data['toCompartmentQrCode'] = to_compartment_qr_code
                data['lioNr'] = from_compartment.article.lio_id
                data['unit'] = unit
                data['quantity'] = quantity

                return JsonResponse(data, safe=False, status=200)


class GetArticles(APIView):
    '''Get articles according to lioNr, name or storageId.'''

    @si.inject
    def __init__(self, _deps, *args):
        self.article_management_service: ArticleManagementService = (
            _deps['ArticleManagementService']())
        self.storage_management_service: StorageManagementService = (
            _deps['StorageManagementService']())
        self.user_service: UserService = (
            _deps['UserService']())

    def get(self, request):
        '''Get articles according to lioNr, name or storageId.'''
        if request.method == 'GET':
            # Gets parameter(s) from query in URL
            query_param_lio_nr = request.GET.get('lioNr', None)
            query_param_name = request.GET.get('name', None)
            query_param_storage_id = request.GET.get('storageId', None)

            # Checks if query parameter is used and then get articles with that lio nr or name. Can also be a storage id, then gets all articles in that storage.
            if query_param_lio_nr is not None:
                articles_in_chosen_storage = self.article_management_service.get_articles_by_search_lio(
                    query_param_lio_nr)

            elif query_param_name is not None:
                articles_in_chosen_storage = self.article_management_service.get_articles_by_search_name(
                    query_param_name)
            else:
                articles_in_chosen_storage = self.article_management_service.get_articles()
                

            if query_param_storage_id is not None:
                # Get a list of all compartments in chosen storage
                serialized_articles = []
                current_storage = self.storage_management_service.get_storage_by_id(
                    query_param_storage_id)
                if current_storage is None:
                    return Response({'Storage does not exist'}, status=status.HTTP_400_BAD_REQUEST)

                # Serializes every article and then appends it to a list to print all articles serilized
                for article in articles_in_chosen_storage:
                    compartments = ArticleCompartmentProximitySerializer(
                        article, current_storage).data
                    serialized_article = ApiArticleSerializer(article).data
                    serialized_article["compartments"] = compartments
                    serialized_articles.append(serialized_article)
                return JsonResponse(serialized_articles, safe=False, status=200)
            else:
                serializer = ApiArticleSerializer(
                    articles_in_chosen_storage, many=True)
                return JsonResponse(serializer.data, safe=False, status=200)
