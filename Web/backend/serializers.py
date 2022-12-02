from rest_framework import serializers
from django.db.models import Q, Case, When, Value, IntegerField

from backend.coremodels.alternative_article_name import AlternativeArticleName
from backend.coremodels.article import Article
from backend.coremodels.article import GroupInfo
from backend.coremodels.storage import Storage
from backend.coremodels.user_info import UserInfo
from backend.coremodels.compartment import Compartment
from backend.coremodels.order import Order
from backend.coremodels.transaction import Transaction
from backend.coremodels.ordered_article import OrderedArticle


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'


class UserInfoSerializer(serializers.ModelSerializer):
    costCenters = serializers.SerializerMethodField('get_storages')
    userId = serializers.CharField(source='user_id')
    username = serializers.CharField(source='user')
    role = serializers.IntegerField(source='group_id')

    class Meta:
        model = UserInfo
        fields = ('userId', 'username', 'costCenters', 'role')

    # returns storages instead of costcenters
    def get_storages(self, obj):
        centers = obj.cost_center.all()
        storages = Storage.objects.filter(
            cost_center__in=centers).values('id')
        final = []
        for i in range(len(storages)):
            final.append((storages[i]['id']))
        return final


class CompartmentSerializer(serializers.ModelSerializer):
    article = ArticleSerializer(many=False, read_only=True)
    storageId = serializers.CharField(source='storage_id')
    normalOrderQuantity = serializers.CharField(source='standard_order_amount')
    orderQuantityLevel = serializers.CharField(source='order_point')
    qrCode = serializers.CharField(source='id')
    quantity = serializers.CharField(source='amount')

    class Meta:
        model = Compartment
        fields = ('placement', 'storageId',
                  'qrCode', 'quantity', 'normalOrderQuantity',
                  'orderQuantityLevel', 'article')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupInfo
        fields = ('id', 'group_name')


class TransactionSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    userId = serializers.CharField(source='by_user.id', read_only=True)
    timeStamp = serializers.CharField(
        source='time_of_transaction', read_only=True)
    lioNr = serializers.PrimaryKeyRelatedField(
        source='article.lio_id', read_only=True)
    storageId = serializers.PrimaryKeyRelatedField(
        source='storage.id', read_only=True)
    quantity = serializers.IntegerField(source='amount', read_only=True)

    class Meta:
        model = Transaction
        fields = ('id', 'userId', 'timeStamp', 'lioNr',
                  'storageId', 'quantity', 'unit', 'operation')


class AlternativeNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlternativeArticleName
        fields = ('name',)

# class MultiStorageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Storage,Compartment
#         field


class UnitsSerializer(serializers.ModelSerializer):
    outputPerInput = serializers.IntegerField(source='output_per_input')

    class Meta:
        model = Article
        fields = ('output', 'input', 'outputPerInput')


# class SupplierSerializer(serializers.ModelSerializer):
#     supplierName = serializers.CharField(
#         source='article_supplier.name', read_only=True)
#     supplierArticleNr = serializers.CharField(
#         source='supplier_article_nr', read_only=True)

#     class Meta:
#         model = ArticleHasSupplier
#         fields = ('supplierName', 'supplierArticleNr')


class NoArticleCompartmentSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(source='amount', read_only=True)
    qrCode = serializers.CharField(source='id', read_only=True)
    normalOrderQuantity = serializers.IntegerField(
        source='standard_order_amount')
    orderQuantityLevel = serializers.IntegerField(
        source='order_point', read_only=True)
    storageId = serializers.PrimaryKeyRelatedField(
        source='storage.id', read_only=True)

    class Meta:
        model = Compartment
        fields = ('placement', 'storageId', 'qrCode', 'quantity',
                  'normalOrderQuantity', 'orderQuantityLevel')


class ApiArticleSerializer(serializers.ModelSerializer):
    lioNr = serializers.CharField(
        source='lio_id', read_only=True)
    inputUnit = serializers.CharField(
        source='input', read_only=True)
    outputUnit = serializers.CharField(
        source='output', read_only=True)
    outputPerInputUnit = serializers.IntegerField(
        source='output_per_input', read_only=True)
    # The SlugRelatedField references a specific field in a reverse foreign key mapping without creating a nested dictionary
    alternativeNames = serializers.SlugRelatedField(
        read_only=True, many=True, slug_field='name', source='alternativearticlename_set')
    # Here you get the primary key from a foreign key relation
    alternativeProducts = serializers.PrimaryKeyRelatedField(
        source='alternative_articles', read_only=True, many=True)
    # Here we get a nested dictianary with data from a reverse foreign key relation
    compartments = NoArticleCompartmentSerializer(
        source='compartment_set', read_only=True, many=True
    )
    # The name supplier_article_nr is renamed to supplierArticleNr so that it is the same as the API
    supplierArticleNr = serializers.CharField(
        source='supplier_article_nr', read_only=True)
    supplierName = serializers.CharField(
        source='supplier.name', read_only=True)

    class Meta:
        model = Article
        fields = ('compartments', 'inputUnit', 'outputUnit', 'outputPerInputUnit', 'price', 'supplierName', 'supplierArticleNr', 'name', 'alternativeNames', 'lioNr', 'alternativeProducts',
                  'Z41')


class ApiArticleSerializerNoCompartment(serializers.ModelSerializer):
    lioNr = serializers.CharField(
        source='lio_id', read_only=True)
    inputUnit = serializers.CharField(
        source='input', read_only=True)
    outputUnit = serializers.CharField(
        source='output', read_only=True)
    outputPerInputUnit = serializers.IntegerField(
        source='output_per_input', read_only=True)
    # The SlugRelatedField references a specific field in a reverse foreign key mapping without creating a nested dictionary
    alternativeNames = serializers.SlugRelatedField(
        read_only=True, many=True, slug_field='name', source='alternativearticlename_set')
    # Here you get the primary key from a foreign key relation
    alternativeProducts = serializers.PrimaryKeyRelatedField(
        source='alternative_articles', read_only=True, many=True)
    # The name supplier_article_nr is renamed to supplierArticleNr so that it is the same as the API
    supplierArticleNr = serializers.CharField(
        source='supplier_article_nr', read_only=True)
    supplierName = serializers.CharField(
        source='supplier.name', read_only=True)

    class Meta:
        model = Article
        fields = ('inputUnit', 'outputUnit', 'outputPerInputUnit', 'price', 'supplierName', 'supplierArticleNr', 'name', 'alternativeNames', 'lioNr', 'alternativeProducts',
                  'Z41')


class OrderedArticleSerializer(serializers.ModelSerializer):
    orderedQuantity = serializers.CharField(source='quantity')
    articleInfo = ApiArticleSerializer(
        source='article', read_only=True, many=False)

    class Meta:
        model = OrderedArticle
        fields = ('articleInfo', 'orderedQuantity', 'unit')


class OrderSerializer(serializers.ModelSerializer):
    articles = OrderedArticleSerializer(
        source='orderedarticle_set', read_only=True, many=True)
    storageId = serializers.PrimaryKeyRelatedField(
        source='to_storage', read_only=True)
    orderDate = serializers.CharField(source='order_date')
    estimatedDeliveryDate = serializers.CharField(
        source='estimated_delivery_date')
    deliveryDate = serializers.CharField(
        source='delivery_date')
    state = serializers.CharField(source='order_state')

    class Meta:
        model = Order
        fields = ['id', 'storageId', 'orderDate',
                  'estimatedDeliveryDate', 'deliveryDate', 'state', 'articles']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = ('building', 'floor')


class ApiCompartmentSerializer(serializers.ModelSerializer):
    article = ApiArticleSerializerNoCompartment(read_only=True)
    quantity = serializers.IntegerField(source='amount', read_only=True)
    qrCode = serializers.CharField(source='id', read_only=True)
    normalOrderQuantity = serializers.IntegerField(
        source='standard_order_amount')
    orderQuantityLevel = serializers.IntegerField(
        source='order_point', read_only=True)
    storageId = serializers.PrimaryKeyRelatedField(
        source='storage.id', read_only=True)

    class Meta:
        model = Compartment
        fields = ('placement', 'storageId', 'qrCode', 'quantity',
                  'normalOrderQuantity', 'orderQuantityLevel', 'article')


class StorageSerializer(serializers.ModelSerializer):
    #id = serializers.CharField(source='name', read_only=True)
    location = LocationSerializer(source='*')
    compartments = ApiCompartmentSerializer(
        source='compartment_set', many=True, read_only=True)

    class Meta:
        model = Storage
        fields = ('id', 'location', 'compartments')


class NearbyStoragesSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='storage.id', read_only=True)
    location = LocationSerializer(source='storage', read_only=True)
    # Calls the later defined function get_self_reference below
    compartment = serializers.SerializerMethodField('get_self_reference')

    class Meta:
        model = Compartment
        fields = ('id', 'location', 'compartment')

    # A function to get a nested dictionary with data from the current object that is being serialized
    def get_self_reference(self, object):
        return ApiCompartmentSerializer(object).data


class ArticleCompartmentProximitySerializer():
    '''Self made serializer, contains properties
        article: Article, storage: Storage, is_valid(): Bool
        and data: [ApiCompartmentModel]'''

    def __init__(self, article: Article, storage: Storage):
        self.article = article
        self.storage = storage
        self.valid = True
        self.data = []
        same_floor = Q(storage__floor__iexact=storage.floor)
        same_building = Q(storage__building__iexact=storage.building)

        if (storage.floor is None):
            self.valid = False
        if (storage.building is None):
            self.valid = False
        if (not self.valid):
            return

        nearest_comps = article.compartment_set.all().annotate(
            proximity_ordering=Case(
                When(same_building & same_floor, then=Value(2)),
                When(same_building & ~same_floor, then=Value(1)),
                When(same_floor & ~same_building, then=Value(0)),
                When(~same_floor & ~same_building, then=Value(-1)),
                output_field=IntegerField(),
            )
        ).order_by('-proximity_ordering')
        if (not nearest_comps):
            self.valid = False

        self.data = NoArticleCompartmentSerializer(
            nearest_comps, many=True, read_only=True).data

    def is_valid(self):
        return self.valid
