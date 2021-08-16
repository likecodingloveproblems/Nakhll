from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from rest_framework import status, mixins, generics, permissions, response
from rest_framework.decorators import action
from nakhll.authentications import CsrfExemptSessionAuthentication
from .models import Invoice
from .serializers import InvoiceSerializer
from .permissions import IsInvoiceOwner


class InvoiceViewSet(generics.GenericAPIView, mixins.CreateModelMixin, 
                    mixins.UpdateModelMixin, mixins.RetrieveModelMixin):
    serializer_class = InvoiceSerializer
    permission_classes = [IsInvoiceOwner, permissions.IsAuthenticated, ]
    authentication_classes = [CsrfExemptSessionAuthentication, ]
    queryset = Invoice.objects.all()

    @action(methods=['POST'], detail=True)
    def check_coupon(self, request, pk,):
        # coupon_code --> get from post data
        pass
    
    @action(methods=['POST'], detail=True)
    def check_logistic(self, request, pk):
        # logistic --> get from post data
        # should be ignored if no compeleting factor is available
        pass