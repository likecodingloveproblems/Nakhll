import os
import zipfile
import random
import pandas as pd
from django.utils.text import slugify
from django.conf import settings
from nakhll_market.models import Product, ProductBanner


class BulkProductHandler:
    def __init__(self, *, shop, images_zip_file=None,
                 required_fields_with_types={'Title': object, 'barcode': object,
                                             'Price': 'Int64', 'OldPrice': 'Int64', 'Inventory': 'Int64'},
                 optional_fields_with_types={
                     'Description': object, 'Image': object},
                 update_fields=['Price', 'OldPrice', 'Inventory'],
                 image_fields={'image_1': object, 'image_2': object, 'image_3': object}):
        self.df = None
        self.shop = shop
        self.na_rows = None
        self.images_path = self.parse_images_zip(images_zip_file)
        self.slug_duplicate_rows = None
        self.required_fields_with_types = required_fields_with_types
        self.optional_fields_with_types = optional_fields_with_types
        self.update_fields = update_fields
        self.image_fields = image_fields

    def parse_csv(self, csv_file):
        df = pd.read_csv(csv_file, dtype=self.required_fields_with_types)
        self.df = df
        return self.dataframe_parser()

    def dataframe_parser(self):
        df = self.df
        self.validate_df(df)
        df = self.__drop_na_rows(df)
        df = self.__add_slug_to_df(df)
        df = self.__drop_duplicate_slugs(df)
        result = self.save_to_db(df)
        return result

    def save_to_db(self, df):
        new_products_df, old_products_df = self.__seperate_new_and_old_products(
            df)
        old_products = self.__create_old_products_instance(old_products_df)
        new_products = self.__create_new_products_instance(new_products_df)
        return {
            'old_products': len(old_products),
            'new': len(new_products),
            'total_rows': df.shape[0],
            'na_rows': self.na_rows,
            'slug_duplicate_rows': self.slug_duplicate_rows,
        }

    def __create_old_products_instance(self, df):
        self.__drop_nonupdate_fields(df)
        old_products = [Product(FK_Shop=self.shop, **row)
                        for row in df.T.to_dict().values()]
        Product.objects.bulk_update(old_products, self.update_fields)
        return old_products

    def __create_new_products_instance(self, df):
        product_images_dictioanry = self.__pop_images_dictioanry(df)
        new_products = [Product(FK_Shop=self.shop, **row)
                        for row in df.T.to_dict().values()]
        Product.objects.bulk_create(new_products)
        self.__append_images_to_products(df, product_images_dictioanry)
        return new_products

    def __append_images_to_products(self, new_products_df, product_images_dictioanry):
        bulk_product_list = []
        bulk_product_banner_list = []
        new_products_sorted = Product.objects.filter(FK_Shop=self.shop,
                                                     barcode__in=new_products_df['barcode'].to_list()).order_by('barcode')
        for product, product_image_item in zip(new_products_sorted, product_images_dictioanry):
            images = product_image_item[1]
            if images:
                product.Image = images[0]
                bulk_product_list.append(product)
                for img in images:
                    product_banner = ProductBanner(
                        FK_Product=product, Image=img)
                    bulk_product_banner_list.append(product_banner)
        Product.objects.bulk_update(bulk_product_list, ['Image'])
        ProductBanner.objects.bulk_create(bulk_product_banner_list)

    def validate_df(self, df):
        self._validate_required_fields(df)
        self._validate_optional_fields(df)
        self.__drop_extra_fields(df)

    def __drop_extra_fields(self, df):
        extra_fields = list(set(df.columns) - set(self.required_fields_with_types.keys())
                                            - set(self.optional_fields_with_types.keys())
                                            - set(self.image_fields.keys()))
        df.drop(extra_fields, axis=1, inplace=True)

    def __drop_nonupdate_fields(self, df):
        nonupdate_fields = list(set(df.columns) - set(self.update_fields))
        df.drop(nonupdate_fields, axis=1, inplace=True)

    def _validate_required_fields(self, df):
        for field, field_type in self.required_fields_with_types.items():
            if field not in df.columns:
                raise Exception(f'{field} is required field')
            if df[field].dtype != field_type:
                raise Exception(f'{field} must be {field_type}')

    def _validate_optional_fields(self, df):
        for field, field_type in self.optional_fields_with_types.items():
            if field not in df.columns:
                continue
            if df[field].dtype != field_type:
                raise Exception(f'{field} must be {field_type}')

    def __add_slug_to_df(self, df):
        df['Slug'] = list(map(lambda title: self.shop.Slug +
                          '-' + slugify(title, allow_unicode=True), df['Title']))
        return df

    def __drop_na_rows(self, df):
        na_free = df.dropna(subset=self.required_fields_with_types.keys())
        self.na_rows = df[~df.index.isin(na_free.index)]
        return na_free

    def __drop_duplicate_slugs(self, df):
        duplicate_free = df.drop_duplicates(subset='Slug', keep='first')
        self.slug_duplicate_rows = df[~df.index.isin(duplicate_free.index)]
        return duplicate_free

    def __seperate_new_and_old_products(self, df):
        new_products = df.query(
            'barcode not in @Product.objects.filter(FK_Shop=@self.shop).values_list("barcode", flat=True)')
        old_products = df.query(
            'barcode in @Product.objects.filter(FK_Shop=@self.shop).values_list("barcode", flat=True)')
        return new_products, old_products

    def parse_images_zip(self, images_zip_file):
        rand_num = random.randint(1, 100000)
        path = f'/tmp/bulk_product_images/{rand_num}'
        if images_zip_file:
            with zipfile.ZipFile(images_zip_file, 'r') as zip_ref:
                zip_ref.extractall(path)
        return path

    def __pop_images_dictioanry(self, df):
        images_dictioanry = {}
        for index, row in df.iterrows():
            barcode = row['barcode']
            images = []
            for image_field in self.image_fields:
                image_path = row.get(image_field)
                if image_path and type(image_path) == str:
                    images.append(image_path)
            images_dictioanry[barcode] = [
                image for image in images if os.path.isfile(f'{self.images_path}/{image}')]
        self.__drop_image_fields(df)
        return sorted(images_dictioanry.items())

    def __drop_image_fields(self, df):
        for image_field in self.image_fields:
            df.drop(image_field, axis=1, inplace=True)
