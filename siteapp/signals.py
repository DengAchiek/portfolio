from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .content import seed_portfolio_content


@receiver(post_migrate)
def ensure_seed_content(sender, **kwargs):
  if sender.name != "siteapp":
    return
  seed_portfolio_content()
