import random
from datetime import datetime, timedelta, timezone
from typing import Any

from faker import Faker

from ddd_application.fake_factory.base_factory import BaseFakeFactory


class TransactionFakeFactory(BaseFakeFactory):
    def __init__(self) -> None:
        self.faker = Faker()
        self.compromised_users = self._mount_compromised_users()
        self.high_risk_merchants = self._mount_high_risk_merchants()

    def _mount_compromised_users(self) -> set[int]:
        """Retorna um conjunto de usuários comprometidos."""
        return set(random.sample(range(1000, 9999), 50))

    def _mount_high_risk_merchants(self) -> list[str]:
        """Retorna uma lista de merchants de alto risco."""
        return ["QuickCash", "PaydayLoan", "LoanShark"]

    def generate(self) -> dict[str, Any]:
        transaction = {
            "transaction_id": self.faker.uuid4(),
            "user_id": random.randint(1000, 9999),
            "amount": round(self.faker.pyfloat(min_value=0.01, max_value=10000), 2),
            "currency": "USD",
            "merchant": self.faker.company(),
            "timestamp": (
                datetime.now(timezone.utc)
                + timedelta(seconds=random.randint(-300, 3000))
            ).isoformat(),
            "location": self.faker.country_code(),
            "is_fraud": 0,
        }

        is_fraud = 0
        amount = transaction["amount"]
        user_id = transaction["user_id"]
        merchant = transaction["merchant"]

        # Account Takeover
        if user_id in self.compromised_users and amount > 500 and random.random() < 0.3:
            is_fraud = 1
            transaction["amount"] = random.uniform(500, 5000)
            transaction["merchant"] = random.choice(self.high_risk_merchants)

        # Card Testing
        if (
            not is_fraud
            and amount < 2.0
            and user_id % 1000 == 0
            and random.random() < 0.25
        ):
            is_fraud = 1
            transaction["amount"] = round(random.uniform(0.01, 2), 2)
            transaction["location"] = "US"

        # Merchant Collusion
        if (
            not is_fraud
            and merchant in self.high_risk_merchants
            and amount > 3000
            and random.random() < 0.15
        ):
            is_fraud = 1
            transaction["amount"] = random.uniform(300, 1500)

        # Geographical Anomaly
        if not is_fraud and user_id % 500 == 0 and random.random() < 0.1:
            is_fraud = 1
            transaction["location"] = random.choice(["CN", "GB", "RU"])

        # Baseline random fraud (0.1 - 0.3%)
        if not is_fraud and random.random() < 0.002:
            is_fraud = 1
            transaction["amount"] = random.uniform(100, 2000)

        # Garantindo que 98.5% das transações não sejam fraudulenta
        transaction["is_fraud"] = is_fraud if random.random() < 0.985 else 0

        return transaction
