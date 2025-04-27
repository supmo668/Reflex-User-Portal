import reflex as rx
from sqlmodel import func, select
from ....models.admin.subscription import Subscription, SubscriptionFeature
from ...configs.default_configurations import DEFAULT_SUBSCRIPTION_FEATURES

import logging
logger = logging.getLogger(__name__)

class SubscriptionState(rx.State):
    selected_hosts: list[str] = []
    selected_guests: list[str] = []
    feature: SubscriptionFeature = None

    @rx.event
    def initialize_default_features(self):
        """Initialize default subscription features if they do not exist."""
        logging.info("Initializing default subscription features.")
        with rx.session() as session:
            count = session.exec(
                select(func.count(SubscriptionFeature.id))
            ).one()
            if count == 0:
                for feature in DEFAULT_SUBSCRIPTION_FEATURES:
                    session.add(feature)
                session.commit()

    @rx.event
    def load_subscription(self, user_id: int):
        with rx.session() as session:
            subscription = session.exec(
                select(Subscription).where(Subscription.user_id == user_id, Subscription.is_active == True)
            ).first()
            if subscription:
                self.feature = session.exec(
                    select(SubscriptionFeature).where(SubscriptionFeature.id == subscription.feature_id)
                ).first()
            else:
                self.feature = session.exec(
                    select(SubscriptionFeature).where(SubscriptionFeature.name == "Free")
                ).first()

    @rx.event
    def select_host(self, host_id: str):
        if self.feature and len(self.selected_hosts) >= self.feature.max_hosts:
            return rx.toast.error(f"Upgrade to select more than {self.feature.max_hosts} hosts.")
        if host_id not in self.selected_hosts:
            self.selected_hosts.append(host_id)

    @rx.event
    def select_guest(self, guest_id: str):
        if self.feature and len(self.selected_guests) >= self.feature.max_guests:
            return rx.toast.error(f"Upgrade to select more than {self.feature.max_guests} guests.")
        if guest_id not in self.selected_guests:
            self.selected_guests.append(guest_id)