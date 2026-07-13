import pytest
from gltest.helpers import load_fixture
from gltest.assertions import tx_execution_succeeded

from tests.integration.fixtures import deploy_vulnerable_escrow


@pytest.mark.integration
def test_escrow_submit_review_end_to_end():
    contract = load_fixture(deploy_vulnerable_escrow)
    receipt = contract.submit_review(
        args=["Great product, arrived on time, works perfectly."]
    ).transact(wait_interval=10000, wait_retries=20)
    assert tx_execution_succeeded(receipt)
