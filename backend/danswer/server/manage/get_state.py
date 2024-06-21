from fastapi import APIRouter

from danswer import __version__
from danswer.auth.users import user_needs_to_be_verified
from danswer.configs.app_configs import AUTH_TYPE
from danswer.server.manage.models import AuthTypeResponse
from danswer.server.manage.models import VersionResponse
from danswer.server.models import StatusResponse

router = APIRouter()


@router.get("/health")
def healthcheck() -> StatusResponse:
    return StatusResponse(success=True, message="ok")


@router.get("/auth/type")
def get_auth_type() -> AuthTypeResponse:
    auth_type = AUTH_TYPE
    print(f"Auth type requested: {auth_type}")
    return AuthTypeResponse(
        auth_type=auth_type, requires_verification=user_needs_to_be_verified()
    )


@router.get("/version")
def get_version() -> VersionResponse:
    return VersionResponse(backend_version=__version__)
