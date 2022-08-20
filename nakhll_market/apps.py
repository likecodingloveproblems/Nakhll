from django.apps import AppConfig


class NakhllMarketConfig(AppConfig):
    name = 'nakhll_market'
    verbose_name = 'بازار نخل'

    def ready(self):
        import nakhll_market.signals
