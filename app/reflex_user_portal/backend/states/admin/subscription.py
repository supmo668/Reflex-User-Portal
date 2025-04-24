import reflex as rx
import sqlmodel
from sqlmodel import select
from ....models.admin.subscription import Subscription, SubscriptionFeature

class SubscriptionFeatureState(rx.State):
    """State for managing subscription features."""
    @rx.event
    def initialize_default_features(self):
        """Initialize default subscription features if they do not exist."""
        with rx.session() as session:
            count = session.exec(sqlmodel.select(sqlmodel.func.count(SubscriptionFeature.id))).one()
            if count == 0:
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
                for feature in features:
                    session.add(feature)
                session.commit()

class SubscriptionState(rx.State):
    selected_hosts: list[str] = []
    selected_guests: list[str] = []
    feature: SubscriptionFeature = None

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