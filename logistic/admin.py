from django.contrib import admin
from logistic.models import (LogisticUnitGeneralSetting, ShopLogisticUnit,
                             ShopLogisticUnitCalculationMetric,
                             ShopLogisticUnitConstraint)

# Register your models here.

admin.site.register(LogisticUnitGeneralSetting)
admin.site.register(ShopLogisticUnit)
admin.site.register(ShopLogisticUnitConstraint)
admin.site.register(ShopLogisticUnitCalculationMetric)
