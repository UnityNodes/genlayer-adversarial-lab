import pytest
from gltest.helpers import load_fixture

from tests.integration.fixtures import deploy_vulnerable_oracle


@pytest.mark.integration
def test_oracle_deploys():
    contract = load_fixture(deploy_vulnerable_oracle)
    assert contract.get_price(args=[]).call() == 0
