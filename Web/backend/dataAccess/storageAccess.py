# from datetime import timedelta
from backend.coremodels.article import Article
from backend.coremodels.transaction import Transaction
# from backend.coremodels.Compartment import Compartment
# from backend.coremodels.Storage import Storage
# from backend.coremodels.transaction import Transaction
# from backend.coremodels.article import Article
# from backend.coremodels.qr_code import QRCode
from backend.coremodels.compartment import Compartment
from backend.coremodels.storage import Storage
# from backend.coremodels.transaction import Transaction
# from ..coremodels.order import Order
from ..__init__ import dataAccessInjector as di


@di.register(name="StorageAccess")
class StorageAccess():
    '''Storage acces.'''

    def get_storage(self, id: str) -> Storage:
        '''Returns storage from id.'''
        try:
            storage = Storage.objects.get(id=id)
            return storage
        except Exception:
            return None

    def get_compartments_containing_article(self, lio_id):
        '''Get compartmens containing an article id.'''
        compartments = Compartment.objects.filter(article=lio_id)
        return compartments

    # TODO: This does not seem to do what it is supposed to do. Please review
    def set_compartment_amount(self, compartment_id: str, amount: int) -> int:
        '''Sets amount in compartment.'''
        try:
            Compartment.objects.filter(id=compartment_id).update(amount=amount)
            compartment = Compartment.objects.get(id=compartment_id)
            return compartment
        except Exception:
            return None

    # TODO: This does not seem to do what it is supposed to do. Please review
    def get_compartment_stock(self,
                              compartment_id: str, article_id: str) -> int:
        '''Returns stock of compartment using article id.'''
        try:
            stock = int(Compartment.objects.get(
                id=compartment_id, article=article_id).amount)
            return stock
        except Exception:
            return None

    def get_storage_stock(self, storage_id: str) -> dict:
        '''Returns storage stock using storage id.'''
        try:
            return "article: {} amount: {}".format(
                Compartment.objects.get(id=storage_id).article,
                Compartment.objects.get(id=storage_id).amount)
        except Exception:
            return None

    def get_all_storages(self) -> dict:
        '''Returns every storage unit.'''
        try:
            return Storage.objects.prefetch_related('compartment_set')
        except Exception:
            return None

    def get_article_in_compartment(self, compartment_id: str) -> Article:
        '''Return article in storage space using storage space id.'''
        try:
            compartment = Compartment.objects.get(id=compartment_id)
            article = Article.objects.get(lio_id=compartment.article.lio_id)
            return article
        except Exception:
            return None

    def search_article_in_storage(self, storage_id: str,
                                  article_id: str) -> int:
        '''Search for article in storage using storage unit id
        and article id.'''
        try:
            storage = Storage.objects.get(id=storage_id)
            article = Article.objects.get(lio_id=article_id)
            compartment = Compartment.objects.get(storage=storage,
                                                  article=article)
            return compartment.amount
        except Exception:
            return None

    def get_compartments_by_storage(self, storage_id: str) -> int:
        '''Return compartments from storage id.'''
        try:
            return Compartment.objects.filter(storage=storage_id)
        except Exception:
            return None

    def get_all_transactions(self, fromDate, toDate, limit) -> dict:
        '''Return every transaction. If optional querying parameters are passed, filter by these'''
        try:
            if fromDate and toDate and limit:
                all_transactions = Transaction.objects.filter(time_of_transaction__range=(
                    fromDate, toDate)).order_by('-time_of_transaction')[:int(limit)]
            else:
                all_transactions = Transaction.objects.all()
            return all_transactions
        except Exception:
            return None

    def get_transaction_by_id(self, transaction_id: str) -> Transaction:
        '''Return transaction from transaction id.'''
        try:
            transaction = Transaction.objects.get(id=transaction_id)
            return transaction
        except Exception:
            return None

    def edit_transaction_by_id(self, transaction_id: str, new_time_of_transaction: str) -> Transaction:
        '''Changes a date of a transaction.'''
        try:
            Transaction.objects.filter(id=transaction_id).update(
                time_of_transaction=new_time_of_transaction)
            transaction = Transaction.objects.get(id=transaction_id)
            return transaction
        except Exception:
            return None

    def get_transaction_by_storage(self, storage_id: str) -> int:
        '''Return transaction from storage id.'''
        try:
            return Transaction.objects.filter(storage=storage_id)
        except Exception:
            return None

    def get_transaction_by_cost_date(self, attribute_cost_to: str, start: str, end: str) -> dict:
        '''Return transaction from storage id.'''
        try:
            return Transaction.objects.filter(attribute_cost_to=attribute_cost_to, time_of_transaction__range=(start, end))

        except Exception:
            return None

    def get_storage_by_costcenter(self, cost_center: str) -> Storage:
        '''Return storage using cost-center.'''
        try:
            storage = Storage.objects.get(cost_center=cost_center)
            return storage
        except Exception:
            return None

# FR 9.4.1 och FR 9.4.2 ##
    def create_compartment(self, storage_id: str, placement: str,
                           qr_code) -> Compartment:
        '''Create new compartment.'''
        storage = Storage.objects.filter(id=storage_id).first()
        # article = Article.objects.get(lio_id='123')
        try:
            compartment = Compartment(
                id=qr_code,
                storage=storage,
                placement=placement, maximal_capacity=999)
            compartment.save()
            return compartment
        except Exception:
            return None

    def get_compartment_by_qr(self, qr_code: str) -> Compartment:
        '''Get compartment using qr code.'''
        try:
            compartment = Compartment.objects.get(id=qr_code)
            return compartment
        except Exception:
            return None

    def get_max_capacity(self, current_compartment: Compartment) -> int:
        '''Get maximal_capacity.'''
        try:
            return current_compartment.maximal_capacity
        except Exception:
            return None

# #  FR 9.4.1 och FR 9.4.2

 # TODO: This does not seem to do what it is supposed to do. Please review
    def set_storage_amount(self, compartment_id: str, amount: int) -> int:
        '''Sets amount in compartment.'''
        try:
            new_amount = amount
            return Compartment.objects.update(**{amount: new_amount})
        except Exception:
            return None

    def set_storage(self, current_compartment: Compartment, new_storage: Storage):
        '''Sets article in compartment.'''
        current_compartment.storage = new_storage
        current_compartment.save()

    def set_article(self, current_compartment: Compartment, new_article: Article):
        '''Sets article in compartment.'''
        current_compartment.article = new_article
        current_compartment.save()

    def set_amount(self, current_compartment: Compartment, new_amount: int):
        '''Sets amount in compartment.'''
        current_compartment.amount = new_amount
        current_compartment.save()

    def set_standard_order_amount(self, current_compartment: Compartment, new_std_order_amount: int):
        '''Sets standard_order_amount in compartment.'''
        current_compartment.standard_order_amount = new_std_order_amount
        current_compartment.save()

    def set_order_point(self, current_compartment: Compartment, new_order_point: int):
        '''Sets order_point in compartment.'''
        current_compartment.order_point = new_order_point
        current_compartment.save()

    def set_placement(self, current_compartment: Compartment, new_placement: int):
        '''Sets placement in compartment.'''
        current_compartment.placement = new_placement
        current_compartment.save()
