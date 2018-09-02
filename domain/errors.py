class DomainError(Exception):
    pass


class InvalidExchange(DomainError):
    pass


class InvalidSymbol(DomainError):
    pass


class InvalidOperation(DomainError):
    pass
