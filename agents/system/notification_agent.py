import asyncio
from datetime import date
from agents.base_agent import BaseAgent

class AgentNotification(BaseAgent):
    name = "AgentNotification"

    async def run(self) -> dict:
        start = self._timestamp()
        opp_service = self.model.services.get("opportunity")
        notif_service = self.model.services.get("notification")
        user_service = self.model.services.get("user")

        if not all([opp_service, notif_service, user_service]):
            return self._make_report(False, 0, ["Missing services for NotificationAgent"], self._duration(start))

        expiring = await opp_service.get_expiring_soon(days=7)
        users = await user_service.get_all_users()

        created = 0
        errors = []

        for opp in expiring:
            opp_category = (opp.category or "").lower()
            for user in users:
                user_interests = [i.lower() for i in (user.interests or [])]
                if any(opp_category in interest for interest in user_interests):
                    try:
                        days_left = (opp.deadline - date.today()).days
                        message = (
                            f"'{opp.title}' closes in "
                            f"{days_left} day(s) — don't miss it!"
                        )
                        await notif_service.create_notification(
                            user_id=user.user_id,
                            opportunity_id=opp.id,
                            message=message
                        )
                        created += 1
                    except Exception as e:
                        errors.append(str(e))

        return self._make_report(
            success=True,
            items=created,
            errors=errors,
            duration=self._duration(start),
            notifications_created=created
        )

    def notify(self) -> None:
        """Synchronous bridge for step activation."""
        asyncio.run(self.run_safe())
