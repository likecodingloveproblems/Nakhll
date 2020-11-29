from Payment.models import Factor, FactorPost

for factor in Factor.objects.all():
    for factorPost in factor.FK_FactorPost.all():
        factorPost.Factor = factor
        factorPost.save()