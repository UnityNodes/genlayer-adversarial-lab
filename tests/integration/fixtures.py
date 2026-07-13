from gltest import get_contract_factory


def deploy_vulnerable_oracle():
    factory = get_contract_factory("WebPriceOracle")
    return factory.deploy(args=[])


def deploy_vulnerable_escrow():
    factory = get_contract_factory("SentimentEscrow")
    return factory.deploy(args=[])
