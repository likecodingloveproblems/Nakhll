from django.db.models.signals import post_save , post_delete
from django.dispatch import receiver

#----------------------- Create signal ---------------------------------#

@receiver(post_save)
def alert_factor(sender , instance , created , **kwargs):
     if created == True :
           Alert.objects.create(Part = '12', FK_User = request.user, 
                                 Slug = factor.ID)

@receiver(post_save)
def add_new_shop(sender , instance , created ,**kwargs):
     if created == True :
          Alert.objects.create(Part = '2', FK_User = request.user, Slug = shop.ID,
                               Seen = True, Status = True, FK_Staff = request.user)

@receiver(post_save)
def shop_banner(sender , instance , created ,**kwargs):
     if created == True :
          Alert.objects.create(Part = '4', 
                              FK_User = request.user, 
                              Slug = thisbanner.id, 
                              Seen = True, 
                              Status = True, 
                              FK_Staff = request.user)

@receiver(post_save)
def add_new_product(sendre , instance , created , **kwargs):
     if created == True :
          Alert.objects.create(Part = '6', FK_User = request.user, Slug = product.ID, 
                               Seen = True, Status = True, FK_Staff = request.user)

@receiver(post_save)
def new_product_banner(sender , instance , created , **kwargs):
     if created == True :
          Alert.objects.create(Part = '8', FK_User = request.user, Slug = thisbanner.id,
                               Seen = True, Status = True, FK_Staff = request.user)

@receiver(post_save)
def add_new_product_attribut(sender , instance , created , **kwargs):
     if created == True :
          Alert.objects.create(Part = '11', FK_User = request.user, Slug = attrproduct.id,
                               Seen = True, Status = True, FK_Staff = request.user)

@receiver(post_save)
def add_new_product_attrprice(sender , instance , created , **kwargs):
     if created == True :
          Alert.objects.create(Part = '17', FK_User = request.user, Slug = attrprice.id,
                               Seen = True, Status = True, FK_Staff = request.user)

@receiver(post_save)
def add_new_attribute(sender , instance , created , **kwargs):
     if created == True :
         Alert.objects.create(FK_User = request.user, Part = '10', Slug = this_attribute.id)

@receiver(post_save)
def repaly_ticketing(sender , instance , created , **kwargs):
     if created == True :
        Alert.objects.create(Part = '16', FK_User = request.user, Slug = ticket_id)

@receiver(post_save)
def add_new_complaint(sender , instance , created , **kwargs):
     if created == True :
        Alert.objects.create(Part = '18', FK_User = request.user, Slug = msg.id)

@receiver(post_save)
def add_shop_copun(sender , instance , created , **kwargs):
     if created == True :
        Alert.objects.create(Part = '26', FK_User = request.user, Slug = copun.id)

@receiver(post_save)
def add_new_comment_in_product(sender , instance , created , **kwargs):
     if created == True :
        Alert.objects.create(Part = '14', FK_User = request.user, Slug = comment.id)

@receiver(post_save)
def add_new_comment_in_shop(sender , instance , created , **kwargs):
     if created == True :
        Alert.objects.create(Part = '30', FK_User = request.user, Slug = comment.id)

@receiver(post_save)
def add_new_review_in_product(sender , instance , created , **kwargs):
     if created == True :
        Alert.objects.create(Part = '15', FK_User = request.user, Slug = review.id)

@receiver(post_save)
def accept_factor_product(sender , instance , created , **kwargs):
     if created == True :
        Alert.objects.create(Part = '20', FK_User = request.user, Slug = ID)

@receiver(post_save)
def cansel_factor_product(sender , instance , created , **kwargs):
     if created == True :
        Alert.objects.create(Part = '13', FK_User = request.user, Slug = this_factor.ID)

@receiver(post_save)
def send_factor(sender , instance , created , **kwargs):
     if created == True :
        Alert.objects.create(Part = '21', FK_User = request.user, Slug = barcode.id)

@receiver(post_save)
def add_check_out(sender , instance , created , **kwargs):
     if created == True :
        Alert.objects.create(Part = '31', FK_User = request.user, Slug = Description)

@receiver(post_save)
def add_optional_attribute(sender , instance , created , **kwargs):
     if created == True :
        Alert.objects.create(Part = '32', FK_User = request.user, Slug = this_optional_attribute.id)




#------------------------------- Delete signal -------------------------------------------#

@receiver(post_delete)
def delete_shop_banner(sender , instance , **kwargs):
     Alert.objects.create(Part = '22', FK_User = request.user, Slug = banner_id)

@receiver(post_delete)
def delete_product_attribute(sender , instance , **kwargs):
     Alert.objects.create(Part = '24', FK_User = request.user, Slug = this_attribute_product.id)

@receiver(post_delete)
def delete_product_attribute_price(sender , instance , **kwargs):
     Alert.objects.create(Part = '25', FK_User = request.user, Slug = this_attrprice.id)

@receiver(post_delete)
def delete_shop_copun(sender , instance , **kwargs):
     Alert.objects.create(Part = '27', FK_User = request.user, Slug = coupon.id)

@receiver(post_delete)
def delete_product_banner(sender , instance , **kwargs):
     Alert.objects.create(FK_User = request.user, Part = '23', Slug = this_banner.id)

@receiver(post_delete)
def delete_optional_attribute(sender , instance , **kwargs): 
     Alert.objects.create(Part = '33', FK_User = request.user, Slug = this_optional_attribute.id)





                                                                                
    

