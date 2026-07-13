"""Shared helpers for direct mode tests."""


def to_hex(addr_bytes):
    """Convert an address fixture to the EIP-55 checksummed hex key that
    contracts use in their maps (via Address.as_hex).

    Call after direct_deploy so the SDK is on sys.path.
    """
    if hasattr(addr_bytes, "as_hex"):
        return addr_bytes.as_hex
    from genlayer.py.types import Address

    return Address(addr_bytes).as_hex
