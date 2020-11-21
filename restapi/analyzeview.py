from rest_framework.decorators import api_view, permission_classes
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from django.http.response import HttpResponse
from django.utils import timezone
from django.http import JsonResponse
from xlsxwriter.workbook import Workbook
from django.db.models import Sum
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN,
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from .serializers import *
import threading, io
from datetime import datetime

# get model
from django.contrib.auth.models import User
from nakhll_market.models import Profile, Product, Shop, BankAccount, AttrProduct, ShopViews, Alert, Field, ShopComment, Review, Comment
from Payment.models import Factor, FactorPost

# -------------------------------------------------------------------------------------------------------------------------------------

# get shop alert
def get_shop_alert(this_shop):
    # result
    result = []
    # search in alert
    for item in Alert.objects.filter(Part__in = ['2', '3']):
        if Shop.objects.filter(ID = item.Slug, Slug = this_shop.Slug).exists():
            result.append(item)
    return result


# get time interval create until first alert
def time_interval_create_until_first_alert(this_shop, this_shop_alerts):
    try:
        # call get_shop_alert
        first_alert_date = this_shop_alerts[1].DateCreate.date()
        # shop create date
        shop_create_date = this_shop.DateCreate.date()
        # time interval
        date_format = "%Y-%m-%d"
        shop_create_date = datetime.strptime(str(shop_create_date), date_format)
        first_alert_date = datetime.strptime(str(first_alert_date), date_format)
        time_interval = first_alert_date - shop_create_date
        return time_interval.days
    except:
        return 'تغییر نداشته'


# get time interval create until last alert
def time_interval_create_until_last_alert(this_shop, this_shop_alerts, this_shop_alerts_count):
    try:
        if this_shop_alerts_count != 1:
            # call get_shop_alert
            last_alert_date = this_shop_alerts[this_shop_alerts_count - 1].DateCreate.date()
            # shop create date
            shop_create_date = this_shop.DateCreate.date()
            # time interval
            date_format = "%Y-%m-%d"
            shop_create_date = datetime.strptime(str(shop_create_date), date_format)
            last_alert_date = datetime.strptime(str(last_alert_date), date_format)
            time_interval = last_alert_date - shop_create_date
            return time_interval.days
        else:
            return 'تغییر نداشته'
    except:
        return 'تغییر نداشته'


# get accepted alert count
def get_accepted_alert_count(this_shop_alerts):
    # count
    count = 0
    # call get_shop_alert
    for item in this_shop_alerts:
        if item.Status == True:
            count += 1
    return count


# get shop factor
class get_shop_factor(threading.Thread):
    def run(self, this_shop):
        # result
        result = []
        # search in factor
        for item in Factor.objects.filter(PaymentStatus = True, Publish = True, Checkout = False):
            for factor_item in item.FK_FactorPost.all():
                if factor_item.FK_Product.FK_Shop == this_shop:
                    result.append(item)
        return result


# get shop factor
def get_shop_factor_cansel(this_shop_factors):
    # count
    count = 0
    # call get_shop_factor
    for item in this_shop_factors:
        if item.FK_FactorPost.filter(ProductStatus = '0').exists():
            count += 1
    return count


# get shop bank account status
def get_shop_bank_account_status(this_shop):
    if Profile.objects.get(FK_User = this_shop.FK_ShopManager).chack_user_bank_account() == False:
        return 'دارد'
    else:
        return 'ندارد'


# get average time interval of alerts
def get_average_time_interval_of_alerts(this_shop_alerts, this_shop_alerts_count):
    # sum time interval
    sum_time = 0
    if (this_shop_alerts_count != 1) and (this_shop_alerts_count != 0):
        # call get_shop_alert
        for i in range(this_shop_alerts_count - 1):
            # first
            first = this_shop_alerts[i].DateCreate.date()
            # second
            second = this_shop_alerts[i + 1].DateCreate.date()
            # time interval
            date_format = "%Y-%m-%d"
            first = datetime.strptime(str(first), date_format)
            second = datetime.strptime(str(second), date_format)
            sum_time = (second - first).days
        return round((sum_time / this_shop_alerts_count), 2)
    else:
        return 0


# get peoduct alert
def get_product_alert(this_product):
    # result
    result = []
    # search in alert
    for item in Alert.objects.filter(Part__in = ['6', '7']):
        if Product.objects.filter(ID = item.Slug, Slug = this_product.Slug).exists():
            result.append(item)
    return result


# get prodcut alert count
def get_product_alert_count(this_product):
    # call get_product_alert
    result = get_product_alert(this_product)
    return len(result)


# get product time interval create until first alert
def get_product_time_interval_create_until_first_alert(this_product, this_product_alerts):
    try:
        # call get_product_alert
        first_alert_date = this_product_alerts[1].DateCreate.date()
        # product create date
        product_create_date = this_product.DateCreate.date()
        # time interval
        date_format = "%Y-%m-%d"
        product_create_date = datetime.strptime(str(product_create_date), date_format)
        first_alert_date = datetime.strptime(str(first_alert_date), date_format)
        time_interval = first_alert_date - product_create_date
        return time_interval.days
    except:
        return 'تغییر نداشته'


# get product time interval create until last alert
def get_product_time_interval_create_until_last_alert(this_product, this_product_alerts, this_product_alerts_count):
    try:
        if this_product_alerts_count != 1:
            # call get_product_alert
            last_alert_date = this_product_alerts[get_product_alert_count(this_product) - 1].DateCreate.date()
            # product create date
            product_create_date = this_product.DateCreate.date()
            # time interval
            date_format = "%Y-%m-%d"
            product_create_date = datetime.strptime(str(product_create_date), date_format)
            last_alert_date = datetime.strptime(str(last_alert_date), date_format)
            time_interval = last_alert_date - product_create_date
            return time_interval.days
        else:
            return 'تغییر نداشته'
    except:
        return 'تغییر نداشته'


# get product average time interval of alerts
def get_product_average_time_interval_of_alerts(this_product_alerts, this_product_alerts_count):
    # sum time interval
    sum_time = 0
    if (this_product_alerts_count != 1) and (this_product_alerts_count != 0):
        # call get_product_alert
        for i in range(this_product_alerts_count - 1):
            # first
            first = this_product_alerts[i].DateCreate.date()
            # second
            second = this_product_alerts[i + 1].DateCreate.date()
            # time interval
            date_format = "%Y-%m-%d"
            first = datetime.strptime(str(first), date_format)
            second = datetime.strptime(str(second), date_format)
            sum_time = (second - first).days
        return round((sum_time / this_product_alerts_count), 2)
    else:
        return 0


# get product accepted alert count
def get_product_accepted_alert_count(this_product_alerts):
    # count
    count = 0
    # call get_product_alert
    for item in this_product_alerts:
        if item.Status == True:
            count += 1
    return count


# get product status
def get_product_status(this_product):
    if this_product.Publish == True:
        return 'منتشر شده'
    else:
        return 'منتشر نشده'


# check the seller interaction
def check_the_seller_interaction(request):
    try:
        # chack user access level
        if request.user.is_superuser:
            # create io file
            output = io.BytesIO()
            # create xlsx
            workbook = Workbook(output, {'in_memory': True})
            # get shop order by view
            shop_view_list = list(ShopViews.objects.all())
            # get shop view
            def getview(item):
                return int(item.Total_View)
            shop_view_list.sort(reverse = True, key = getview)
            for item in shop_view_list:
                try:
                    if item.FK_Shop.Slug in ['taemirkhodro', 'kadbanoo_99', 'Somayeh-HosseinShahi', 'asale-vahshie-naaab', 'sport_accesories', 'Dehghani-Rice', 'unique_jewellry_mhd', 'grocery-store-Aali', 'ganjinehhomeandorganicproductsspecializedstore', 'fogholade', 'kilim-darestan', 'kosarane', 'ninninaz', 'Atari-namjoo', 'oil-1', 'test_shop', '1369', 'samareh', 'bagh', 'kolbesefid', 'havigh', 'delbaft', 'royastore', 'mobleghalikarmania', 'store', 'kilim-darestan-2', 'celid', 'najma-gallery', 'empt', 'ahonor-gallery', 'hoorfarbadspareparts', 'oil-2', '-asalrabor1', 'nomadic-organic-products', 'howzeh_book_kerman', 'b_u_t', 'galorisoheyl', 'forooshgah-ghods', 'hakim-arab', 'atregilan', 'cellid84', 'mm1363mm', 'reza9876', 'shahrzad', '-asalrabor', 'sismounimahnini-', 'abfaraz', 'fanni_team', '13990414', 'hajghasem', 'cofeeshop']:
                        print('item id ------------>' + str(item.id))
                        print(item.FK_Shop.Slug)
                        worksheet = workbook.add_worksheet(item.FK_Shop.Title)
                        # set row
                        row = 0
                        # get shop data
                        this_shop_products = item.FK_Shop.get_all_products()
                        this_shop_products_count = this_shop_products.count()
                        this_shop_alerts = get_shop_alert(item.FK_Shop)
                        this_shop_factors = get_shop_factor().run(item.FK_Shop)
                        # set shop filed
                        worksheet.write(row, 0, 'نام حجره')
                        worksheet.write(row, 1, 'نام حجره دار')
                        worksheet.write(row, 2, 'تاریخ ساخت حجره')
                        worksheet.write(row, 3, 'تاریخ آخرین بروزرسانی حجره')
                        worksheet.write(row, 4, 'تعداد محصولات')
                        worksheet.write(row, 5, 'تعداد محصولات منتشر شده')
                        worksheet.write(row, 6, 'تعداد تغییرات حجره')
                        worksheet.write(row, 7, 'فاصله زمانی ساخت حجره تا اولین تغییر')
                        worksheet.write(row, 8, 'فاصله زمانی ساخت حجره تا آخرین تغییر')
                        worksheet.write(row, 9, 'میانگین زمانی تغییرات')
                        worksheet.write(row, 10, 'تعداد تغییرات پذیرفته شده')
                        worksheet.write(row, 11, 'میزان بازدید حجره')
                        worksheet.write(row, 12, 'تعداد نظرات حجره')
                        worksheet.write(row, 13, 'تعداد فاکتور ها')
                        worksheet.write(row, 14, 'تعداد فاکتور ها لغو شده')
                        # worksheet.write(row, 15, 'میانگین زمانی پاسخ به فاکتور ها')
                        worksheet.write(row, 16, 'وضعیت اطلاعات حساب بانکی')
                        worksheet.write(row, 17, 'آخر ورود کاربر به سایت')
                        # set shop data
                        row += 1
                        worksheet.write(row, 0, item.FK_Shop.Title)
                        worksheet.write(row, 1, item.FK_Shop.FK_ShopManager.first_name + ' ' + item.FK_Shop.FK_ShopManager.last_name)
                        worksheet.write(row, 2, str(item.FK_Shop.DateCreate.date()))
                        worksheet.write(row, 3, str(item.FK_Shop.DateUpdate.date()))
                        worksheet.write(row, 4, this_shop_products_count)
                        worksheet.write(row, 5, this_shop_products.filter(Available = True, Publish = True).count())
                        worksheet.write(row, 6, len(this_shop_alerts))
                        worksheet.write(row, 7, time_interval_create_until_first_alert(item.FK_Shop, this_shop_alerts))
                        worksheet.write(row, 8, time_interval_create_until_last_alert(item.FK_Shop, this_shop_alerts, len(this_shop_alerts)))
                        worksheet.write(row, 9, get_average_time_interval_of_alerts(this_shop_alerts, len(this_shop_alerts)))
                        worksheet.write(row, 10, get_accepted_alert_count(this_shop_alerts))
                        worksheet.write(row, 11, int(item.Total_View))
                        worksheet.write(row, 12, ShopComment.objects.filter(FK_Shop = item.FK_Shop).count())
                        worksheet.write(row, 13, len(this_shop_factors))
                        worksheet.write(row, 14, get_shop_factor_cansel(this_shop_factors))
                        # worksheet.write(row, 15, 'میانگین زمانی پاسخ به فاکتور ها')
                        worksheet.write(row, 16, get_shop_bank_account_status(item.FK_Shop))
                        worksheet.write(row, 17, str(item.FK_Shop.FK_ShopManager.last_login.date()))
                        # set product field
                        row += 5
                        worksheet.write(row, 0, 'نام محصول')
                        worksheet.write(row, 1, 'تاریخ ساخت محصول')
                        worksheet.write(row, 2, 'تاریخ آخرین بروزرسانی محصول')
                        worksheet.write(row, 3, 'تعداد تغییرات')
                        worksheet.write(row, 4, 'فاصله زمانی ساخت حجره تا اولین تغییر')
                        worksheet.write(row, 5, 'فاصله زمانی ساخت حجره تا آخرین تغییر')
                        worksheet.write(row, 6, 'میانگین زمانی تغییرات')
                        worksheet.write(row, 7, 'تعداد تغییرات پذیرفته شده')
                        worksheet.write(row, 8, 'تعداد نظرات محصول')
                        worksheet.write(row, 9, 'تعداد نقد و بررسی محصول')
                        worksheet.write(row, 10, 'وضعیت انتشار محصول')
                        # set product data
                        for product_item in this_shop_products:
                            # set product data
                            this_product_alerts = get_product_alert(product_item)
                            print(this_shop_products_count)
                            row += 1
                            worksheet.write(row, 0, product_item.Title)
                            worksheet.write(row, 1, str(product_item.DateCreate.date()))
                            worksheet.write(row, 2, str(product_item.DateUpdate.date()))
                            worksheet.write(row, 3, len(this_product_alerts))
                            worksheet.write(row, 4, get_product_time_interval_create_until_first_alert(product_item, this_product_alerts))
                            worksheet.write(row, 5, get_product_time_interval_create_until_last_alert(product_item, this_product_alerts, len(this_product_alerts)))
                            worksheet.write(row, 6, get_product_average_time_interval_of_alerts(this_product_alerts, len(this_product_alerts)))
                            worksheet.write(row, 7, get_product_accepted_alert_count(this_product_alerts))
                            worksheet.write(row, 8, Comment.objects.filter(FK_Product = product_item).count())
                            worksheet.write(row, 9, Review.objects.filter(FK_Product = product_item).count())
                            worksheet.write(row, 10, get_product_status(product_item))
                            this_shop_products_count -= 1
                except:
                    continue      

            # get output
            workbook.close()
            output.seek(0)
            response = HttpResponse(output.read(), content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition'] = "attachment; filename = " + 'test' + ".xlsx"
            output.close()

            return response
        else:
            return JsonResponse({'status' : False}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'status' : False, 'message' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)


# get factor analyze
def get_factor_analyze(request):
    try:
        # chack user access level
        if request.user.is_superuser:
            # create io file
            output = io.BytesIO()
            # create xlsx
            workbook = Workbook(output, {'in_memory': True})
            # date list
            date_list = ['2019-12-01|2019-12-31', '2020-01-01|2020-01-31', '2020-02-01|2020-02-29', '2020-03-01|2020-03-31', '2020-04-01|2020-04-30', '2020-05-01|2020-05-31', '2020-06-01|2020-06-30', '2020-07-01|2020-07-31', '2020-08-01|2020-08-31', '2020-09-01|2020-09-30', '2020-10-01|2020-10-13']

            for date_item in date_list:
                this_date = date_item.split('|')
                start = this_date[0]
                end = this_date[1]
                this_date_factors = Factor.objects.filter(PaymentStatus = True, OrderDate__range = [start, end])
                this_date_sum = 0
                i = 0
                worksheet = workbook.add_worksheet(start + ' to ' + end)
                # set row
                row = i
                # set factor filed
                worksheet.write(row, 0, 'شماره سریال')
                worksheet.write(row, 1, 'تاریخ خرید')
                worksheet.write(row, 2, 'کل هزینه')
                worksheet.write(row, 3, 'هزینه پست')
                worksheet.write(row, 4, 'میزان تخفیف')
                worksheet.write(row, 5, 'نوع تخفیف')
                worksheet.write(row, 6, 'وضعیت فاکتور')
                worksheet.write(row, 7, 'نوع پرداخت')
                worksheet.write(row, 8, 'توضیحات')
                worksheet.write(row, 9, 'نام خریدار')

                for this_factor in this_date_factors:
                    try:
                        print('date ------------>' + str(date_item))
                        # set factor data
                        row += 1
                        worksheet.write(row, 0, this_factor.FactorNumber)
                        worksheet.write(row, 1, str(this_factor.OrderDate.date()))
                        worksheet.write(row, 2, int(this_factor.TotalPrice))
                        worksheet.write(row, 3, int(this_factor.PostPrice))
                        worksheet.write(row, 4, this_factor.DiscountRate)
                        worksheet.write(row, 5, this_factor.get_coupon_status())
                        worksheet.write(row, 6, this_factor.get_factor_status())
                        worksheet.write(row, 7, this_factor.get_factor_payment_type())
                        worksheet.write(row, 8, this_factor.Description)
                        worksheet.write(row, 9, this_factor.FK_User.first_name + ' ' + this_factor.FK_User.last_name)
                        # set sum
                        this_date_sum += int(this_factor.TotalPrice)
                    except:
                        continue
                row += 3
                worksheet.write(row, 0, 'تعداد فاکتور ها ')
                worksheet.write(row, 1, 'مجموع فروش')
                # set sum
                row += 1
                worksheet.write(row, 0, this_date_factors.count())
                worksheet.write(row, 1, this_date_sum)

            # get output
            workbook.close()
            output.seek(0)
            response = HttpResponse(output.read(), content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition'] = "attachment; filename = " + 'nakhll-factors' + ".xlsx"
            output.close()

            return response
        else:
            return JsonResponse({'status' : False}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'status' : False, 'message' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)



# get top products
def get_top_products(request):
    try:
        # chack user access level
        if request.user.is_superuser:
            # Build Class
            class Top:
                def __init__(self, this_item, this_count):
                    self.item = this_item
                    self.count = this_count

            this_list = []
            # get all sell products
            sell_products_list = []
            # set data
            for item in Factor.objects.filter(PaymentStatus = True):
                for sub_item in item.FK_FactorPost.filter(ProductStatus__in = ['1', '2', '3']):
                    sell_products_list.append(sub_item.FK_Product)
            # clean list
            sell_products_list = list(dict.fromkeys(sell_products_list))

            for item in sell_products_list:
                sum_count = FactorPost.objects.filter(FK_Product = item, ProductStatus__in = ['1', '2', '3']).aggregate(Sum('ProductCount'))['ProductCount__sum']
                this_list.append(Top(item, sum_count))

            # sort count
            def sortcount(item):
                return item.count
            this_list.sort(reverse = True, key = sortcount)

            # create io file
            output = io.BytesIO()
            # create xlsx
            workbook = Workbook(output, {'in_memory': True})
            row = 0
            worksheet = workbook.add_worksheet('top product')

            worksheet.write(row, 0, 'نام محصول')
            worksheet.write(row, 1, 'تعداد فروش')
  
            for item in this_list:
                # set factor data
                row += 1
                worksheet.write(row, 0, item.item.Title)
                worksheet.write(row, 1, item.count)
            # get output
            workbook.close()
            output.seek(0)
            response = HttpResponse(output.read(), content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition'] = "attachment; filename = " + 'nakhll-products' + ".xlsx"
            output.close()

            return response
        else:
            return JsonResponse({'status' : False}, status = HTTP_403_FORBIDDEN)
    except Exception as e:
        return JsonResponse({'status' : False, 'message' : str(e)}, status = HTTP_500_INTERNAL_SERVER_ERROR)