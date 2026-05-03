"""Role-based access control dependencies for V2 routers."""
from app.core.security import Role, require_roles

require_role = require_roles

__all__ = ["Role", "require_role", "require_roles"]
