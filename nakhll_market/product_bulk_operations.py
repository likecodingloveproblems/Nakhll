"""Bulk operations on products

This module has some classes and fuctions that help you to perform bulk operations on products using a file.
"""
import os
import zipfile
import random
import shutil
import pandas as pd
from itertools import chain
from django.db.models import Q
from django.utils.text import slugify
from django.core.files import File
from simple_history.utils import bulk_update_with_history, bulk_create_with_history
from nakhll_market.models import Product, ProductBanner, HistoricalProduct


HISTORY_TYPE_CREATE = '+'
HISTORY_TYPE_UPDATE = '~'
HISTORY_TYPE_DELETE = '-'


class BulkException(Exception):
    """Exception raised when general error related to bulk operation occured"""


class BulkProductHandler:
    """Class for handling bulk operations on products.

    This class takes a csv file with products information which is required, and an optional images zip file, which
    contains images for products. To relate products with images, the products must have a image_1 field with the
    name of the image file in the images zip file.

    We have two types of bulk operations:
        * :attr:`BULK_TYPE_CREATE` - create new products
        * :attr:`BULK_TYPE_UPDATE` - update existing products
    We use :attr:`nakhll_market.models.Product.barcode` as a unique field for products to indentify them among others.
    You can't do both BULK_TYPE_CREATE and BULK_TYPE_UPDATE at the same time. This means if you use BULK_TYPE_CREATE
    and pass a csv file with barcodes that already exist in the database, those products will be ignored. And if you
    use BULK_TYPE_UPDATE and pass a csv file with barcodes that don't exist in the database, those products will be
    ignored as well.

    There are some validations on the csv file to validate the data that user wants to import. In case of any violation
    in the data, no exception will be raised, but the row will be ignored.

    Also we save each product's history in the :attr:`nakhll_market.models.HistoricalProduct` model. Using this
    history, we can preform undo operations on products. Currenlty we allow shop owners to undo only one operation at a
    time.

    The csv file can have the following columns:
        * Title: the title of the product which you want to insert or update. This field is required by default.
        * barcode: the barcode of the product. This is the unique identifier of the product. This field is required by
            default. When creating a new product, we save this barcode for future reference. When updating a product,
            we use this barcode to find the product in the database.
        * Price: the price of the product. This field is required by default.
        * OldPrice: the old price of the product. This field is required by default. Use 0 if you don't have OldPrice.
        * Inventory: the inventory of the product. This field is required by default.
        * image_1: the name of the image of the product. This field is required by default for :attr:`BULK_TYPE_CREATE`.
            This image is the main image of the product, while other images are secondary images.
        * image_2: the name of the secondary image of the product. This field is optional by default.
        * image_3: the name of the secondary image of the product. This field is optional by default.
        * Net_Weight: the net weight of the product. This field is optional by default.
        * Weight_With_Packing: the weight with packing of the product. This field is optional by default.
        * category_id: the id of the category of the product. This field is optional by default.
            Images are only required for creating new products. In case of updating products, you shouldn't use this
            column.

    Attributes:
        * shop: the shop which all products belong to
        * image_zip_file: path of the zip file that contains all images. This field only works for BULK_TYPE_CREATE.
        * product_barcode_field: this indicates which field is going to use as the unique identifiers among all user's
            products. by default this is set to 'barcode'.
        * required_fields_with_types: indicates which fields are required and the type of each field (for validation)
        * optional_fields_with_type: indicates which fields are optional and the type of each field (for validation)
        * update_fields: fields that you want to be affedted in update process. if you don't pass a field in this list
            and pass it in the csv file, it will be ignored.
        * image_fields: indicates which fields of the csv file are for images.
        * bulk_type: indicates the type of bulk operation that you want to perform. bulk_types can be:
            * :attr:`BULK_TYPE_CREATE` - create new products
            * :attr:`BULK_TYPE_UPDATE` - update existing products
        * is_undo_operation: indicates if this is an undo operation or not.

    """
    BULK_TYPE_CREATE = 'create'
    BULK_TYPE_UPDATE = 'update'

    def __init__(self, *, shop, images_zip_file=None, product_barcode_field='barcode',
                 required_fields_with_types={
                     'Title': object,
                     'barcode': object,
                     'Price': 'Int64',
                     'OldPrice': 'Int64',
                     'Inventory': 'Int64',
                     'image_1': object,
                 },
                 optional_fields_with_types={
                     'Net_Weight': 'Int64',
                     'Weight_With_Packing': 'Int64',
                     'category_id': 'Int64',
                 },
                 update_fields=['Title', 'Price', 'OldPrice', 'Inventory', 'Net_Weight',
                                'Weight_With_Packing', 'category_id'],
                 image_fields={'image_1': object, 'image_2': object, 'image_3': object},
                 bulk_type=None, is_undo_operation=False):
        self.df = None
        self.shop = shop
        self.shop_key = f'tag:{shop.ID}'
        self.old_shop_key = f'old_tag:{shop.ID}'
        self.na_rows = []
        self.product_barcode_field = product_barcode_field
        self.images_path = self.parse_images_zip(images_zip_file)
        self.slug_duplicate_rows = []
        self.required_fields_with_types = required_fields_with_types
        self.optional_fields_with_types = optional_fields_with_types
        self.update_fields = update_fields
        self.image_fields = image_fields
        if not is_undo_operation and bulk_type not in [self.BULK_TYPE_CREATE, self.BULK_TYPE_UPDATE]:
            raise BulkException('Bulk type must be either create or update')
        self.bulk_type = bulk_type

    def parse_csv(self, csv_file):
        """Get a csv file and parse it to a pandas dataframe."""
        dtypes = {**self.required_fields_with_types, **self.optional_fields_with_types}
        df = pd.read_csv(csv_file, dtype=dtypes)
        self.df = df
        self.total_rows = df.shape[0]
        return self.dataframe_parser()

    def dataframe_parser(self):
        """Parse the dataframe to a list of products."""
        df = self.df
        df = self.validate_df(df)
        if self.bulk_type == self.BULK_TYPE_CREATE:
            df = self.__drop_na_rows(df)
            df = self.__add_slug_to_df(df)
            df = self.__drop_df_duplicate_slugs(df)
            self.__validate_slugs(df)
        result = self.save_to_db(df)
        self.__delete_image_files()
        return result

    def save_to_db(self, df):
        """Save all cleaned dataframe's data in the database.

        It first remove the old history of products and then save newly added or edited products seperately with new 
        history.
        """
        self.__delete_previous_product_history()
        new_products_df, old_products_df = self.__seperate_new_old_products(df)
        new_products, old_products = [], []
        if self.bulk_type == self.BULK_TYPE_UPDATE:
            old_products = self.__update_old_products_instance(old_products_df)
        elif self.bulk_type == self.BULK_TYPE_CREATE:
            new_products = self.__create_new_products_instance(new_products_df)

        return {
            'old_products': len(old_products),
            'new': len(new_products),
            'total_rows': self.total_rows,
            'na_rows': len(self.na_rows),
            'slug_duplicate_rows': len(self.slug_duplicate_rows),
        }

    def parse_images_zip(self, images_zip_file):
        """If there is a zip file with all images, extract it and return the path of the directory."""
        rand_num = random.randint(1, 100000)
        path = f'/tmp/bulk_product_images/{rand_num}/'
        if images_zip_file:
            with zipfile.ZipFile(images_zip_file, 'r') as zip_ref:
                zip_ref.extractall(path)
            return path
        return None

    def validate_df(self, df):
        """Validate all fields in the dataframe.

        Validations are:
            * Check if unique field exists in df
            * Check if required fields exist in df
            * Check each row's data type
            * drop extra fields
            * drop rows with that doesn't have image (only for :attr:`BULK_TYPE_CREATE`)
        """
        df = self.__validate_unique_field(df)
        self._validate_required_fields(df)
        self._validate_fields_dtype(df)
        self.__drop_extra_fields(df)
        self.__drop_non_exists_image_rows(df)
        return df

    def __update_old_products_instance(self, df):
        products = Product.objects.filter(
            FK_Shop=self.shop, barcode__in=df[self.product_barcode_field].to_list())
        update_list = []
        for product in products:
            for field in self.update_fields:
                if field in df.columns:
                    self.__set_product_attribute(product, field, df)
            update_list.append(product)
        bulk_update_with_history(update_list, Product, self.update_fields, batch_size=500,
                                 default_user=self.shop.FK_ShopManager,
                                 default_change_reason=f'tag:{self.shop.ID}')
        return update_list

    def __set_product_attribute(self, product, field, df):
        setattr(product, field, df[field][df[self.product_barcode_field] == product.barcode].values[0])

    def __create_new_products_instance(self, df):
        product_images_dictioanry = self.__pop_images_dictioanry(df)
        new_products = [Product(FK_Shop=self.shop, Publish=True, Status='1', **row)
                        for row in df.T.to_dict().values()]
        objs = bulk_create_with_history(new_products, Product, batch_size=500,
                                        default_user=self.shop.FK_ShopManager,
                                        default_change_reason=f'tag:{self.shop.ID}')
        self.__append_images_to_products(df, product_images_dictioanry)
        return new_products

    def __append_images_to_products(self, new_products_df, product_images_dictioanry):
        if not product_images_dictioanry:
            return
        bulk_product_list = []
        bulk_product_banner_list = []
        new_products_sorted = Product.objects.filter(
            FK_Shop=self.shop, barcode__in=new_products_df[
                self.product_barcode_field].to_list()).order_by(self.product_barcode_field)
        for product, product_image_item in zip(new_products_sorted, product_images_dictioanry):
            images = product_image_item[1]
            if images:
                image_file = File(open(images[0], 'rb'))
                product.Image.save(images[0], image_file)
                bulk_product_list.append(product)
                for img in images:
                    image_file = File(open(img, 'rb'))
                    product_banner = ProductBanner(
                        FK_Product=product, Image=image_file, Publish=True)
                    bulk_product_banner_list.append(product_banner)
        Product.objects.bulk_update(bulk_product_list, ['Image'])
        ProductBanner.objects.bulk_create(bulk_product_banner_list)

    def __validate_unique_field(self, df):
        if self.product_barcode_field not in df.columns:
            raise BulkException(f'{self.product_barcode_field} is required field')
        return df.astype({self.product_barcode_field: str})

    def _validate_required_fields(self, df):
        if self.bulk_type == self.BULK_TYPE_CREATE:
            for field in self.required_fields_with_types:
                if field not in df.columns:
                    raise BulkException(f'{field} is required field')

    def _validate_fields_dtype(self, df):
        fields_with_types = chain(self.required_fields_with_types.items(),
                                  self.optional_fields_with_types.items())
        for field, field_type in fields_with_types:
            if field not in df.columns:
                continue
            if df[field].dtype != field_type:
                raise BulkException(f'{field} must be {field_type}')

    def __drop_extra_fields(self, df):
        extra_fields = list(set(df.columns) - set(self.required_fields_with_types.keys())
                                            - set(self.optional_fields_with_types.keys())
                                            - set(self.image_fields.keys()))
        df.drop(extra_fields, axis=1, inplace=True)

    def __add_slug_to_df(self, df):
        df['Slug'] = list(map(lambda title: slugify(title, allow_unicode=True), df['Title']))
        df['Slug'] = self.shop.Slug + '-' + df['barcode'] + '-' + df['Slug']
        return df

    def __drop_na_rows(self, df):
        na_free = df.dropna(subset=self.required_fields_with_types.keys())
        self.na_rows = df[~df.index.isin(na_free.index)]
        return na_free

    def __drop_non_exists_image_rows(self, df):
        if self.bulk_type == self.BULK_TYPE_UPDATE:
            return
        exists_image_names = os.listdir(self.images_path)
        indexes = df[~df['image_1'].isin(exists_image_names)].index
        df.drop(indexes, inplace=True)

    def __drop_df_duplicate_slugs(self, df):
        duplicate_free = df.drop_duplicates(subset='Slug', keep='first')
        self.slug_duplicate_rows = df[~df.index.isin(duplicate_free.index)]
        return duplicate_free

    def __delete_previous_product_history(self):
        old_shop_key = f'old_tag:{self.shop.ID}'
        Product.history.filter(history_change_reason=old_shop_key).delete()
        product_histories = Product.history.filter(history_change_reason=self.shop_key)
        bulk_update_list = []
        for product_history in product_histories:
            product_history.history_change_reason = old_shop_key
            bulk_update_list.append(product_history)
        HistoricalProduct.objects.bulk_update(bulk_update_list, ['history_change_reason'])

    def __validate_slugs(self, df):
        all_products_slug = set(Product.objects.filter(~Q(FK_Shop=self.shop)).values_list('Slug', flat=True))
        df_slug = set(df['Slug'].to_list())
        duplicated_slugs = all_products_slug.intersection(df_slug)
        if duplicated_slugs:
            raise BulkException(f'Duplicated slugs: {duplicated_slugs}')

    def __seperate_new_old_products(self, df):
        new_products = df.query(
            f'{self.product_barcode_field} not in @Product.objects.filter(FK_Shop=@self.shop)\
                                    .values_list(@self.product_barcode_field, flat=True)')
        old_products = df.query(
            f'{self.product_barcode_field} in @Product.objects.filter(FK_Shop=@self.shop).\
                                    values_list(@self.product_barcode_field, flat=True)')
        return new_products, old_products

    def __pop_images_dictioanry(self, df):
        if not self.images_path:
            self.__drop_image_fields(df)
            return None
        images_dictioanry = {}
        for index, row in df.iterrows():
            barcode = row[self.product_barcode_field]
            images = []
            for image_field in self.image_fields:
                image_name = row.get(image_field, '')
                image_path = self.images_path + str(image_name)
                if image_path and os.path.isfile(image_path):
                    images.append(image_path)
            images_dictioanry[barcode] = images
        self.__drop_image_fields(df)
        return sorted(images_dictioanry.items())

    def __drop_image_fields(self, df):
        image_fields = [image_field for image_field in self.image_fields if image_field in df.columns]
        df.drop(image_fields, axis=1, inplace=True)

    def __delete_image_files(self):
        if self.images_path:
            shutil.rmtree(self.images_path)

    def undo_last_changes(self):
        deleted_products = self.__delete_newly_created_products()
        reverted_products = self.__revert_updated_products()
        self.__revert_undo_shop_tag()
        return {'deleted_products': deleted_products, 'reverted_products': reverted_products}

    def __delete_newly_created_products(self):
        newly_added_historical = Product.history.filter(
            history_change_reason=self.shop_key,
            history_type=HISTORY_TYPE_CREATE)
        newly_added_historical_ids = newly_added_historical.values_list('ID', flat=True)
        newly_added_products = Product.objects.filter(ID__in=newly_added_historical_ids)
        deleted_products, _ = newly_added_products.delete()
        newly_added_historical.delete()
        return deleted_products

    def __revert_updated_products(self):
        updated_historical_products = Product.history.filter(
            history_change_reason=self.shop_key, history_type=HISTORY_TYPE_UPDATE)
        bulk_update_list = []
        for hist in updated_historical_products:
            product = hist.instance
            if hist.prev_record:
                for field in self.update_fields:
                    setattr(product, field, getattr(hist.prev_record.instance, field))
                bulk_update_list.append(product)
        Product.objects.bulk_update(bulk_update_list, self.update_fields)
        return len(bulk_update_list)

    def __revert_undo_shop_tag(self):
        old_product_histories = Product.history.filter(history_change_reason=self.old_shop_key)
        bulk_update_list = []
        for product_history in old_product_histories:
            product_history.history_change_reason = self.shop_key
            bulk_update_list.append(product_history)
        HistoricalProduct.objects.bulk_update(bulk_update_list, ['history_change_reason'])
