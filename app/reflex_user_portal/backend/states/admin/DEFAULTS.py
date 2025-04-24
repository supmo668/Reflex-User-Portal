from ....models.admin.subscription import SubscriptionFeature

features = [
    SubscriptionFeature(
        name="Free",
        max_hosts=1,
        max_guests=1,
        can_use_creative_tools=False,
        can_use_premium_tools=False,
    ),
    SubscriptionFeature(
        name="Hobby",
        max_hosts=3,
        max_guests=3,
        can_use_creative_tools=True,
        can_use_premium_tools=False,
    ),
    SubscriptionFeature(
        name="Creative",
        max_hosts=10,
        max_guests=10,
        can_use_creative_tools=True,
        can_use_premium_tools=True,
    ),
]