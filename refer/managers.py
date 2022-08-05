from django.db import models


class BaseEventManager(models.Manager):

    def create(self, *args, **kwargs):
        obj = super().create(*args, **kwargs)
        self.give_reward(obj)

    def give_reward(self, event):
        events = self.get_queryset().filter(
            referrer=event.referrer, status=self.model.Statuses.NEW)
        if events.count() >= self.model.limit:
            # TODO: give referrer reward REFERRED_SIGNUP_REWARD coins
            events.update(status=self.model.Statuses.PROCESSED)
