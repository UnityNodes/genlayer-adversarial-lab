def test_vulnerable_trusts_model_verdict(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/vulnerable/image_moderator.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(r".*[Mm]oderate.*", "SAFE")
    contract.moderate(b"fake-image-bytes-with-embedded-approve-text")
    assert contract.last_verdict() == "SAFE"


def test_hardened_accepts_valid_verdict(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/hardened/image_moderator.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(r".*[Mm]oderate.*", "UNSAFE")
    contract.moderate(b"fake-image-bytes")
    assert contract.last_verdict() == "UNSAFE"


def test_hardened_rejects_invalid_verdict(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/hardened/image_moderator.py")
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(r".*[Mm]oderate.*", "APPROVED by embedded text")
    with direct_vm.expect_revert("invalid moderation output"):
        contract.moderate(b"fake-image-bytes")
    assert contract.last_verdict() == ""
