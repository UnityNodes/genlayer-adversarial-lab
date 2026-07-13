import pytest
from gltest.helpers import load_fixture
from gltest.assertions import tx_execution_succeeded

from tests.integration.fixtures import deploy_vulnerable_oracle


@pytest.mark.integration
def test_oracle_deploys():
    contract = load_fixture(deploy_vulnerable_oracle)
    assert contract.get_price(args=[]) == 0


@pytest.mark.integration
def test_oracle_settles_end_to_end():
    contract = load_fixture(deploy_vulnerable_oracle)
    receipt = contract.settle(
        args=["https://www.coindesk.com/price/bitcoin"],
        wait_interval=10000,
        wait_retries=20,
    )
    assert tx_execution_succeeded(receipt)
