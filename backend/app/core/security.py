"""Security and authorization foundation for RecoverAI backend.

Note: In Phase 2, this module provides the architectural extension points
for API key verification, merchant context extraction, and role-based access
control (RBAC) to be implemented in subsequent phases.
"""

from typing import Any
from fastapi import Request
from pydantic import BaseModel


class AuthenticatedMerchant(BaseModel):
    """Authenticated merchant context injected into protected endpoint handlers."""

    merchant_id: str
    business_name: str
    role: str = "admin"
    permissions: list[str] = []


async def get_current_merchant_optional(request: Request) -> AuthenticatedMerchant | None:
    """Optional authentication dependency for mixed endpoints.

    In future phases, this will validate bearer tokens or API key headers.
    """
    # Placeholder for Phase 7/17 auth implementations
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    return AuthenticatedMerchant(
        merchant_id="mer_acme_prod_01",
        business_name="Acme Commerce",
        role="admin",
        permissions=["read", "write", "execute_recovery"],
    )
