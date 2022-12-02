# from requests import request
from math import floor
from backend.dataAccess.orderAccess import OrderAccess
from backend.dataAccess.storageAccess import StorageAccess
from backend.dataAccess.userAccess import UserAccess
from backend.serializers import OrderSerializer, CompartmentSerializer
from backend.coremodels.article import Article
from backend.coremodels.storage import Storage
from backend.coremodels.compartment import Compartment
from backend.coremodels.transaction import Transaction
from backend.coremodels.inputOutput import InputOutput
from django.contrib.auth.models import User
from django.http import Http404, JsonResponse, HttpResponseBadRequest
from django.utils.dateparse import parse_date
from backend.__init__ import serviceInjector as si
from ..__init__ import dataAccessInjector as di


@si.register(name='StorageManagementService')
class StorageManagementService():
    '''Storage management service.'''
    @di.inject
    def __init__(self, _deps, *args):
        self.storage_access: StorageAccess = _deps["StorageAccess"]()
        self.order_access: OrderAccess = _deps["OrderAccess"]()
        self.user_access: UserAccess = _deps["UserAccess"]()

    def get_storage_by_id(self, id: str) -> Storage:
        '''Returns storage unit using id.'''
        return self.storage_access.get_storage(id)

    def get_compartment_by_qr(self, id: str) -> Compartment:
        '''Returns storage space using id.'''
        return self.storage_access.get_compartment_by_qr(id)

    def get_compartment_by_article(self, article: Article) -> Compartment:
        '''Returns storage space using article.'''
        return self.storage_access.get_compartment_by_id(id)

    def get_compartment_by_storage_id(self, id: str) -> int:
        '''Returns compartments with storage_id.'''
        return self.storage_access.get_compartments_by_storage(
            storage_id=id)

    def get_stock(self, id: str, article_id: str) -> int:
        '''Return stock.'''
        return self.storage_access.get_compartment_stock(compartment_id=id,
                                                         article_id=article_id)

    def get_storage_stock(self, id: str) -> dict:
        '''Returns dictionary containing stocks in storage.'''
        return self.storage_access.get_storage_stock(storage_id=id)

    def get_all_storages(self) -> dict:
        '''Return every storage unit.'''
        return self.storage_access.get_all_storages()

    def get_storage_value(self, id: str) -> int:
        '''Return total storage value using id.'''
        compartments = self.storage_access.get_compartments_by_storage(
            storage_id=id)
        value = 0
        for compartment in compartments:
            if compartment.article is not None:
                value += compartment.article.price * compartment.amount
        return value

    def get_all_transactions(self, fromDate=None, toDate=None, limit=None) -> dict:
        '''Returns every transaction. Takes fromDate, toDate and limit as optimal parameters for limiting the return.'''
        return self.storage_access.get_all_transactions(fromDate, toDate, limit)

    def get_transaction_by_id(self, transaction_id: str) -> Transaction:
        '''Returns a transaction by id'''
        return self.storage_access.get_transaction_by_id(transaction_id)

    def edit_transaction_by_id(self, transaction_id: str, new_time_of_transaction: str) -> Transaction:
        '''Edit time of a transaction'''
        return self.storage_access.edit_transaction_by_id(transaction_id, new_time_of_transaction)

    def set_compartment_amount(self, compartment_id: int, storage_id: str, amount: int, username: str, add_output_unit: bool, time_of_transaction: str) -> Transaction:
        '''Set a storage to a specified level. Return a transaction.'''

        storage = self.storage_access.get_storage(id=storage_id)
        article = self.storage_access.get_article_in_compartment(
            compartment_id=compartment_id)
        converter = article.output_per_input
        user = User.objects.get(username=username)
        cost_center = storage_id.cost_center
        if add_output_unit:
            unit = "output"
            converter = 1
        else:
            unit = "input"
        compartment = self.storage_access.set_compartment_amount(
            compartment_id, amount*converter)
        transaction = Transaction.objects.create(
            storage=Compartment.objects.get(
                id=compartment_id).storage, article=article, attribute_cost_to=cost_center, operation="adjust",
            by_user=user, amount=amount,
            time_of_transaction=time_of_transaction, unit=unit)
        return transaction

    # Storage is not connected to a costcenter atm
    # For now this is sum och costs (takeout-return)
    # from transactions for one storage_compartment
    def get_storage_cost(self, storage_id: str, start_date: str,
                         end_date: str) -> int:
        '''Get storage cost.'''
        attribute_cost_to = self.storage_access.get_storage(storage_id).cost_center
        sum_value = 0
        transactions = self.storage_access.get_transaction_by_cost_date(
            attribute_cost_to=attribute_cost_to, start=start_date, end=end_date)
        takeout_value = 0
        return_value = 0
        for transaction in transactions:
            if transaction.operation == "takeout":
                takeout_value = transaction.get_value() + takeout_value
            if transaction.operation == "return":
                return_value = transaction.get_value() + return_value
        sum_value = takeout_value - return_value
        return sum_value

    def get_storage_by_costcenter(self, cost_center: str) -> Storage:
        '''Get storage using cost-center.'''
        return self.storage_access.get_storage_by_costcenter(cost_center)

    def get_storage_turnover_rate(self, storage_id: str, start_date: str, end_date: str) -> int:
        '''Get storage turnover rate. (total cost / average storage value)'''
        cost = self.get_storage_cost(storage_id, start_date, end_date)
        '''Estimation of average value: order point + standard order value / 2'''
        compartments = self.storage_access.get_compartments_by_storage(
            storage_id=storage_id)
        '''average_value is the sum of all average compartment values in a storage'''
        average_values = 0
        n_compartments = 0
        for compartment in compartments:
            if compartment.article is not None:
                article_value = compartment.article.price
                compartment_value = (compartment.order_point + compartment.standard_order_amount/2)*article_value
                if compartment_value == 0:
                    compartment_value = (compartment.maximal_capacity/2)*article_value
                average_values += compartment_value
                n_compartments += 1
        if average_values == 0:
            return None
        else:
            '''Average turnover rate over all compartments'''
            return (cost/average_values) / n_compartments
        
      

# FR 10.1.3 #
# alltid takeout/takein
# TODO: This is a lot of work to refactor since barely any of the
# methods work. Leaving this
# TODO to the original author

    def add_to_storage(self, id: str, storage_id: str, amount: int, username: str,
                       add_output_unit: bool, time_of_transaction: str) -> Transaction:
        '''Add to storage.'''
        compartment = self.storage_access.get_compartment_by_qr(id)
        storage_id = storage_id
        cost_center = storage_id.cost_center
        article = Article.objects.get(lio_id=compartment.article.lio_id)
        converter = article.output_per_input
        user = User.objects.get(username=username)
        if (add_output_unit):
            amount_in_storage = Compartment.objects.get(
                id=id).amount + amount
            new_amount = amount
            unit = "output"
        else:
            amount_in_storage = Compartment.objects.get(
                id=id).amount + amount*converter
            new_amount = amount*converter
            unit = "input"

        if (amount_in_storage < 0 or Compartment.objects.get(id=id).maximal_capacity < amount_in_storage):
            return None
        else:
            self.storage_access.set_compartment_amount(id, amount_in_storage)
            new_transaction = Transaction.objects.create(
                storage=compartment.storage, article=article, attribute_cost_to=cost_center, operation="replenish",
                by_user=user, amount=amount,
                time_of_transaction=time_of_transaction, unit=unit)
            new_transaction.save()
            return new_transaction
            # except:
            # return None

# TODO: This is a lot of work to refactor since barely any of the methods work.
# Leaving this
# TODO to the original author

    def add_to_return_storage(self, id: str, storage_id: str, amount: int,
                              username: str, add_output_unit: bool,
                              time_of_transaction) -> Transaction:
        '''Add return to storage.'''
        compartment = Compartment.objects.get(id=id)
        storage_id = storage_id
        cost_center = storage_id.cost_center
        amount = amount
        article = Article.objects.get(lio_id=compartment.article.lio_id)
        user = User.objects.get(username=username)
        medical_employee = User.objects.get(username=username).groups.filter(
            name='medical employee').exists()

        converter = article.output_per_input

        if (medical_employee and article.Z41):
            return None

        if (add_output_unit):
            amount_in_storage = Compartment.objects.get(
                id=id).amount + amount
            new_return_amount = amount
            unit = "output"
        else:
            amount_in_storage = Compartment.objects.get(
                id=id).amount + amount*converter
            new_return_amount = amount*converter
            unit = "input"
        if (amount_in_storage < 0 or Compartment.objects.get(id=id).maximal_capacity < amount_in_storage):
            return None
        else:

            Compartment.objects.filter(id=id).update(amount=amount_in_storage)
            new_transaction = Transaction.objects.create(
                storage=compartment.storage, article=article, attribute_cost_to=cost_center, operation="return",
                by_user=user, amount=amount,
                time_of_transaction=time_of_transaction, unit=unit)
            new_transaction.save()
            return new_transaction

    def take_from_Compartment(self, id: str, storage_id: str, amount: int, username: str,
                              add_output_unit: bool, time_of_transaction: str):
        '''Take from compartment. Return transaction.'''
        compartment = self.storage_access.get_compartment_by_qr(id)
        article = Article.objects.get(lio_id=compartment.article.lio_id)
# inputOutput = InputOutput.objects.get(article=article)
        converter = article.output_per_input
        user = User.objects.get(username=username)

        cost_center = storage_id.cost_center
        if (add_output_unit):
            amount_in_storage = Compartment.objects.get(
                id=id).amount - amount
            new_amount = amount
            unit = "output"
        else:
            amount_in_storage = Compartment.objects.get(
                id=id).amount - amount*converter
            new_amount = amount*converter
            unit = "input"
        if (amount_in_storage < 0 or Compartment.objects.get(id=id).maximal_capacity < amount_in_storage):
            return None
        else:
            Compartment.objects.filter(id=id).update(amount=amount_in_storage)
            new_transaction = Transaction.objects.create(
                storage=compartment.storage, article=article, attribute_cost_to=cost_center,
                operation="takeout", by_user=user, amount=amount,
                time_of_transaction=time_of_transaction, unit=unit)
            new_transaction.save()
            return new_transaction

    def get_article_in_compartment(self, compartment_id: str) -> Article:
        '''Get article in storage space.'''
        return self.storage_access.get_article_in_compartment(
            compartment_id=compartment_id)

    def search_article_in_storage(self, storage_id: str,
                                  article_id: str) -> int:
        '''Search for article in storage.'''
        return self.storage_access.search_article_in_storage(
            storage_id=storage_id, article_id=article_id)
# FR 10.1.3 #

    def get_compartment_content_and_orders(self, compartment_id):
        '''Get content of compartment as well as orders using 
            compartment id.'''
        compartment = self.storage_access.get_compartment_by_id(
            id=compartment_id)
        altered_dict = {}

        if compartment is None:
            return None

        compartment_serializer = CompartmentSerializer(compartment)
        if not compartment_serializer.is_valid:
            return None
        altered_dict.update(compartment_serializer.data)

        order = self.order_access.get_order_by_article_and_storage(
            compartment.storage.id, compartment.article.lio_id)
        if order is not None:
            order_serializer = OrderSerializer(order)
            eta = self.order_access.get_eta(order.id)
            order_dictionary = {"ETA": eta}
            if order_serializer.is_valid:
                order_dictionary.update(order_serializer.data)
            altered_dict['Order'] = order_dictionary
            return altered_dict

    # FR 9.4.1 och FR 9.4.2 ##
    def create_compartment(self, storage_id: str, placement: str,
                           qr_code: str) -> Compartment:
        '''Create new compartment.'''

        compartment = self.storage_access.create_compartment(
            storage_id=storage_id, placement=placement, qr_code=qr_code
        )
        return compartment

    def get_compartment_by_qr(self, qr_code: str) -> Compartment:
        '''Return compartment using qr code.'''
        compartment = self.storage_access.get_compartment_by_qr(
            qr_code=qr_code)
        return compartment

    # FR 9.4.1 och FR 9.4.2 ##

    def update_compartment_by_qr(self, current_compartment: Compartment, new_placement: str, new_storage_id: str, new_amount: int, new_std_order_amount: int, new_order_point: int) -> Compartment:
        '''Edit compartment using qr code.'''

        new_storage = self.storage_access.get_storage(new_storage_id)

        #Update compartments attributes
        self.storage_access.set_placement(current_compartment, new_placement)
        self.storage_access.set_storage(current_compartment, new_storage)
        self.storage_access.set_amount(current_compartment, new_amount)
        self.storage_access.set_standard_order_amount(current_compartment, new_std_order_amount)
        self.storage_access.set_order_point(current_compartment, new_order_point)

    # 25.2.1
    def get_nearby_storages(self, qr_code: str) -> Compartment:
        '''Returns nearby storages containing the
        article which is contained in the compartment which 
        the qr_code points to. If there are no nearby storages on
        the same floor, nearby storages in the building is
        returned. If there are none in the building, other 
        storages are returned. If there are no other storages
        containing the article, None is returned.'''
        subject_compartment = self.get_compartment_by_qr(qr_code)
        if subject_compartment is None:
            return None
        subject_storage = subject_compartment.storage
        subject_article_id = subject_compartment.article.lio_id

        subject_floor = subject_storage.floor
        subject_building = subject_storage.building

        compartments = (
            self.storage_access.get_compartments_containing_article(
                subject_article_id))
        if compartments is None:
            return None
        else:
            floor_neigh = False
            building_neigh = False
            storages_on_floor = {}
            storages_in_building = {}
            storages_elsewhere = {}
            for compartment in compartments:
                if (compartment.storage.floor == subject_floor):
                    storages_on_floor[compartment.storage] = compartment
                    floor_neigh = True
                elif (compartment.storage.building == subject_building):
                    storages_in_building[compartment.storage] = compartment
                    building_neigh = True
                else:
                    storages_elsewhere[compartment.storage] = compartment
            if floor_neigh:
                return storages_on_floor
            elif building_neigh:
                return storages_in_building
            else:
                return storages_elsewhere

    def update_compartment(self, current_compartment: Compartment, new_article: Article, new_amount: int, new_std_order_amount: int, new_order_point: int):
        '''Updates attributes in compartment.'''

        self.storage_access.set_article(current_compartment, new_article)
        self.storage_access.set_amount(current_compartment, new_amount)
        self.storage_access.set_standard_order_amount(
            current_compartment, new_std_order_amount)
        self.storage_access.set_order_point(
            current_compartment, new_order_point)

    def is_compartment_large_enough(self, current_compartment: Compartment, new_amount: int) -> bool:
        '''Return boolean if new amount can fit compartment or not.'''
        max_capacity = self.storage_access.get_max_capacity(current_compartment)

        if new_amount <= max_capacity:
            return True
        return False
