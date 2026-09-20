"""V2.5 route-state cap: FULLY_VERIFIED requires service-specific
provenance. New-lineage wrapper over the frozen RouteEvaluator.

Root cause (frozen V2.4 holdout, generalized): municipal section/landing
pages carry contact markers and universal-offer phrasing, so the frozen
evaluator marked them ROUTE_FULLY_VERIFIED although they only evidence that
the section exists. Rule: a page is service-specific when its URL path is
deep enough to name the service (>= 2 path segments) or its slug contains a
service term. Otherwise the route state is capped at ROUTE_ACCESS_PARTIAL.
No case IDs, no municipality names, no expected labels.
"""

from urllib.parse import urlparse

from .classification_gate_v25 import is_service_specific_url


class RouteEvaluatorV25:
    """Wrap the frozen RouteEvaluator; cap FV on section-level provenance."""

    def __init__(self, inner=None):
        from runtime.discovery.classification import RouteEvaluator
        self._inner = inner or RouteEvaluator()

    def evaluate(self, service_verified, eligibility_verified,
                 access_methods, access_clear, contact_documented,
                 strong_access=None, url=None):
        state = self._inner.evaluate(
            service_verified=service_verified,
            eligibility_verified=eligibility_verified,
            access_methods=access_methods,
            access_clear=access_clear,
            contact_documented=contact_documented,
            strong_access=strong_access,
        )
        if (state == "ROUTE_FULLY_VERIFIED" and url
                and not is_service_specific_url(url)):
            return "ROUTE_ACCESS_PARTIAL"
        return state
