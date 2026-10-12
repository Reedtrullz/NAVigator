from runtime.discovery.classification import RouteEvaluator

class RouteEvaluatorV25:
    def __init__(self, inner: RouteEvaluator | None = None) -> None: ...
    def evaluate(self, service_verified: bool, eligibility_verified: bool,
                 access_methods: list[str], access_clear: bool, contact_documented: bool,
                 strong_access: bool | None = None, url: str | None = None) -> str: ...
