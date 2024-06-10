from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.orm import Session

from danswer.db.models import LLMProvider as LLMProviderModel
from danswer.db.models import UserLLMSettings
from danswer.server.manage.llm.models import FullLLMProvider, FullUserLLMProvider
from danswer.server.manage.llm.models import LLMProviderUpsertRequest


def upsert_llm_provider(
    db_session: Session, llm_provider: LLMProviderUpsertRequest
) -> FullLLMProvider:
    existing_llm_provider = db_session.scalar(
        select(LLMProviderModel).where(LLMProviderModel.name == llm_provider.name)
    )
    if existing_llm_provider:
        existing_llm_provider.provider = llm_provider.provider
        existing_llm_provider.api_key = llm_provider.api_key
        existing_llm_provider.api_base = llm_provider.api_base
        existing_llm_provider.api_version = llm_provider.api_version
        existing_llm_provider.custom_config = llm_provider.custom_config
        existing_llm_provider.default_model_name = llm_provider.default_model_name
        existing_llm_provider.fast_default_model_name = (
            llm_provider.fast_default_model_name
        )
        existing_llm_provider.model_names = llm_provider.model_names
        db_session.commit()
        return FullLLMProvider.from_model(existing_llm_provider)

    # if it does not exist, create a new entry
    llm_provider_model = LLMProviderModel(
        name=llm_provider.name,
        provider=llm_provider.provider,
        api_key=llm_provider.api_key,
        api_base=llm_provider.api_base,
        api_version=llm_provider.api_version,
        custom_config=llm_provider.custom_config,
        default_model_name=llm_provider.default_model_name,
        fast_default_model_name=llm_provider.fast_default_model_name,
        model_names=llm_provider.model_names,
        is_default_provider=None,
    )
    db_session.add(llm_provider_model)
    db_session.commit()

    return FullLLMProvider.from_model(llm_provider_model)


def upsert_user_llm_settings(db_session: Session, user_id: int, settings: dict) -> FullUserLLMProvider:
    llm_settings = db_session.query(UserLLMSettings).filter(
        UserLLMSettings.user_id == user_id,
        UserLLMSettings.name == settings['name']
    ).first()
    
    if llm_settings:
        for key, value in settings.items():
            setattr(llm_settings, key, value)
        db_session.commit()
        return FullUserLLMProvider.from_model(llm_settings)
        
    llm_settings = UserLLMSettings(user_id=user_id, **settings)
    db_session.add(llm_settings)
    db_session.commit()
    
    return FullUserLLMProvider.from_model(llm_settings)


def fetch_existing_llm_providers(db_session: Session) -> list[LLMProviderModel]:
    return list(db_session.scalars(select(LLMProviderModel)).all())


def fetch_default_provider(db_session: Session) -> FullLLMProvider | None:
    provider_model = db_session.scalar(
        select(LLMProviderModel).where(
            LLMProviderModel.is_default_provider == True  # noqa: E712
        )
    )
    if not provider_model:
        return None
    return FullLLMProvider.from_model(provider_model)


def fetch_provider(db_session: Session, provider_name: str) -> FullLLMProvider | None:
    provider_model = db_session.scalar(
        select(LLMProviderModel).where(LLMProviderModel.name == provider_name)
    )
    if not provider_model:
        return None
    return FullLLMProvider.from_model(provider_model)

def fetch_user_llm_settings(db_session: Session, user_id: int) -> list[UserLLMSettings]:
    return db_session.query(UserLLMSettings).filter(UserLLMSettings.user_id == user_id).all()

def fetch_user_default_provider(db_session: Session, user_id: int) -> FullUserLLMProvider | None:
    provider_model = db_session.scalar(
        select(UserLLMSettings).where(
            UserLLMSettings.user_id == user_id,
            UserLLMSettings.is_default_provider == True  # noqa: E712
        )
    )
    if not provider_model:
        return None
    return FullUserLLMProvider.from_model(provider_model)


def fetch_user_provider(db_session: Session, user_id: int, provider_name: str) -> FullUserLLMProvider | None:
    provider_model = db_session.scalar(
        select(UserLLMSettings).where(
            UserLLMSettings.user_id == user_id,
            UserLLMSettings.name == provider_name
        )
    )
    if not provider_model:
        return None
    return FullUserLLMProvider.from_model(provider_model)


def remove_llm_provider(db_session: Session, provider_id: int) -> None:
    db_session.execute(
        delete(LLMProviderModel).where(LLMProviderModel.id == provider_id)
    )
    db_session.commit()


def update_default_provider(db_session: Session, provider_id: int) -> None:
    new_default = db_session.scalar(
        select(LLMProviderModel).where(LLMProviderModel.id == provider_id)
    )
    if not new_default:
        raise ValueError(f"LLM Provider with id {provider_id} does not exist")

    existing_default = db_session.scalar(
        select(LLMProviderModel).where(
            LLMProviderModel.is_default_provider == True  # noqa: E712
        )
    )
    if existing_default:
        existing_default.is_default_provider = None
        # required to ensure that the below does not cause a unique constraint violation
        db_session.flush()

    new_default.is_default_provider = True
    db_session.commit()
