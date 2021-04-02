from django.shortcuts import render

from django.shortcuts import render
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User
from braces.views import LoginRequiredMixin


class ProfileAlert(LoginRequiredMixin , UpdateView):
    model = User
    fields = ['username' , 'first_name' , 'last_name' , 'password']
    redirect_field_name = 'auth:login'
    template_name = "nakhll_market/profile/pages/alert.html"

    def get_context_data(self, **kwargs):
        request = self.request
        context = super().get_context_data(**kwargs)
        this_profile = Profile.objects.get(FK_User=request.user)
        this_inverntory = request.user.WalletManager.Inverntory
        # Get Menu Item
        options = Option_Meta.objects.filter(Title = 'index_page_menu_items')
        # Get Nav Bar Menu Item
        navbar = Option_Meta.objects.filter(Title = 'nav_menu_items')
        # --------------------------------------------------------------------
        # get all new alert
        alert = Alert.objects.filter(Seen = False).order_by('DateCreate')

        context['This_User_Profile'] = this_profile
        context['This_User_Inverntory'] =this_inverntory
        context['Options'] = options
        context['MenuList'] = navbar
        context['Alert'] = alert

        return context
        
