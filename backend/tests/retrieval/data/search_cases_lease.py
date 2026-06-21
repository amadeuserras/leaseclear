import pytest

SEARCH_CASES_LEASE = [
    pytest.param(
        "What is the monthly rent?",
        "3. Rent",
        id="monthly_rent",
    ),
    pytest.param(
        "How much is the security deposit?",
        "5. Security Deposit",
        id="security_deposit",
    ),
    pytest.param(
        "When does the lease end?",
        "2. Term",
        id="lease_end",
    ),
    pytest.param(
        "Can the tenant have pets?",
        "7. Pets",
        id="pets",
    ),
    pytest.param(
        "How much notice must the landlord give before entering?",
        "9. Entry",
        id="landlord_entry",
    ),
    pytest.param(
        "What is the pet deposit?",
        "2. Pet Deposit and Rent",
        id="pet_deposit",
    ),
]
