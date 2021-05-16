from io import BytesIO

from django.db.models.query import QuerySet
from nakhll_market.models import Profile, Shop, Product
from django.http import HttpResponse
from xlsxwriter.workbook import Workbook
from django.views import View
from braces.views import GroupRequiredMixin
from excel_response import ExcelResponse
from django.db.models import Count, Sum


class ShopManagersInformation(GroupRequiredMixin, View):
    group_required = u"accounting"

    def get(self, request):
        filename = 'shop_managers_info.xlsx'
        shops = Shop.objects.all()
        with BytesIO() as output:
            workbook = Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet(filename)
            # set factor filed
            worksheet.write_row(0, 0,
                            ['نام حجره دار',
                            'نام خانوادگی حجره دار',
                            'کدملی حجره دار',
                            'استان حجره دار',
                            'شهرستان حجره دار',
                            'شهر حجره دار',
                            'نشانی حجره دار',
                            'استان حجره',
                            'شهرستان حجره',
                            'شهر حجره',
                            'نشانی حجره',
                            ]
                )
            for row, shop in enumerate(shops):
                user = shop.FK_ShopManager
                if user:
                    first_name = user.first_name
                    last_name = user.last_name
                else:
                    first_name = None
                    last_name = None
                try:
                    profile = Profile.objects.get(FK_User=user)
                    national_code = profile.NationalCode
                    profile_state = profile.State
                    profile_big_city = profile.BigCity
                    profile_city = profile.City
                    profile_location = profile.Location
                except:
                    national_code = None
                    profile_state = None
                    profile_big_city = None
                    profile_city = None
                    profile_location = None
                
                worksheet.write_row(row+1, 0,
                [
                    first_name,
                    last_name,
                    national_code,
                    profile_state,
                    profile_big_city,
                    profile_city,
                    profile_location,
                    shop.State,
                    shop.BigCity,
                    shop.City,
                    shop.Location,
                ])

            workbook.close()

            output.seek(0)

            response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition'] = "attachment; filename = " + filename

            output.close()

        return response
        

class ShopManagersInformationV2(GroupRequiredMixin, View):
    group_required = u"accounting"

    def get(self, request, *args, **kwargs):
        filename = 'shop_managers_info'
        field_header_map = {
            'FK_ShopManager__first_name':'نام',
            'FK_ShopManager__last_name':'نام خانوادگی',
            'FK_ShopManager__User_Profile__NationalCode':'کد ملی',
            'State':'استان',
            'BigCity':'شهرستان',
            'City':'شهر',
            'Location':'نشانی',
        }
        queryset = Shop.objects.shop_managers_info()
        return ExcelResponse(
            data=queryset,
            output_filename=filename,
            )

class UserMobile(View):
    # group_required = u"marketing"

    def get(self, request, *args, **kwargs):
        queryset = Shop.objects.shop_managers_info_marketing()
        return ExcelResponse(
            data=queryset,
            )

class ProductStats(View):

    def get(self, request):
        queryset = Product.objects\
            .annotate(sell_count = Count('Factor_Product'))\
            .annotate(sell_product_count=Sum('Factor_Product__ProductCount'))\
            .values(
                'Title', 'Slug', 'FK_SubMarket__Title', 'FK_Shop__Title', 
                'FK_Shop__Slug', 'FK_Shop__State', 'FK_Shop__BigCity', 'FK_Shop__City',
                'FK_Shop__Location', 'FK_Shop__Available', 'FK_Shop__Publish', 
                'FK_Shop__CanselCount','FK_Shop__FK_ShopManager__username', 'sell_count',
                'sell_product_count', 'Price', 'OldPrice',
                )
        
        return ExcelResponse(
            data=queryset
        )

class UserState(View):

    def get (self , request):
        queryset =  Profile.objects\
            .annotate(shop_count=Count('FK_User__ShopManager'))\
            .values(
                'MobileNumber', 'NationalCode', 'FK_User__first_name', 'FK_User__last_name' 
                , 'shop_count'
                )


        return ExcelResponse(
            data=queryset
        )
