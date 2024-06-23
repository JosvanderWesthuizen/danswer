from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.orm import Session

from danswer.db.models import LLMProvider as LLMProviderModel
from danswer.db.models import UserLLMSettings
from danswer.server.manage.llm.models import FullLLMProvider
from danswer.server.manage.llm.models import LLMProviderUpsertRequest

from danswer.auth.users import current_user
from danswer.db.models import User
from fastapi import Depends


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


def upsert_user_llm_settings(db_session: Session, settings: LLMProviderUpsertRequest,
                             user: User = Depends(current_user)
                             ) -> FullLLMProvider:
    user_id = user.id
    llm_settings = db_session.query(UserLLMSettings).filter(
        UserLLMSettings.user_id == user_id,
    ).first()
    
    if llm_settings:
        assert llm_settings.user_id == user_id
        llm_settings.provider = settings.provider
        llm_settings.api_key = settings.api_key
        llm_settings.api_base = settings.api_base
        llm_settings.api_version = settings.api_version
        llm_settings.custom_config = settings.custom_config
        llm_settings.default_model_name = settings.default_model_name
        llm_settings.fast_default_model_name = (
            settings.fast_default_model_name
        )
        llm_settings.model_names = settings.model_names
        
        llm_provider_model = LLMProviderModel(
            name=settings.name, # TODO: somehow ensure that each model created here has a unique primary key
            provider=settings.provider,
            api_key=settings.api_key,
            api_base=settings.api_base,
            api_version=settings.api_version,
            custom_config=settings.custom_config,
            default_model_name=settings.default_model_name,
            fast_default_model_name=settings.fast_default_model_name,
            model_names=settings.model_names,
            is_default_provider=None,
        )
        db_session.add(llm_provider_model)
        db_session.commit()
        return FullLLMProvider.from_model(llm_provider_model)
        
    llm_settings = UserLLMSettings(user_id=user_id, 
        name=settings.name,
        provider=settings.provider,
        api_key=settings.api_key,
        api_base=settings.api_base,
        api_version=settings.api_version,
        custom_config=settings.custom_config,
        default_model_name=settings.default_model_name,
        fast_default_model_name=settings.fast_default_model_name,
        model_names=settings.model_names,
        is_default_provider=None,
    )
    db_session.add(llm_settings)
    llm_provider_model = LLMProviderModel(
        name=settings.name,
        provider=settings.provider,
        api_key=settings.api_key,
        api_base=settings.api_base,
        api_version=settings.api_version,
        custom_config=settings.custom_config,
        default_model_name=settings.default_model_name,
        fast_default_model_name=settings.fast_default_model_name,
        model_names=settings.model_names,
        is_default_provider=None,
    )
    db_session.add(llm_provider_model)
    db_session.commit()
    
    return FullLLMProvider.from_model(llm_provider_model)


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

def fetch_user_default_provider(db_session: Session, user_id: int) -> FullLLMProvider | None:
    provider_model = db_session.scalar(
        select(UserLLMSettings).where(
            UserLLMSettings.user_id == user_id,
            UserLLMSettings.is_default_provider == True  # noqa: E712
        )
    )
    if not provider_model:
        return None
    model_to_return = LLMProviderModel(
        name=provider_model.name,
        provider=provider_model.provider,
        api_key=provider_model.api_key,
        api_base=provider_model.api_base,
        api_version=provider_model.api_version,
        custom_config=provider_model.custom_config,
        default_model_name=provider_model.default_model_name,
        fast_default_model_name=provider_model.fast_default_model_name,
        model_names=provider_model.model_names,
        is_default_provider=None,
    )
    return FullLLMProvider.from_model(model_to_return)


def fetch_user_provider(db_session: Session, user_id: int, provider_name: str) -> FullLLMProvider | None:
    provider_model = db_session.scalar(
        select(UserLLMSettings).where(
            UserLLMSettings.user_id == user_id,
        )
    )
    if not provider_model:
        return None
    model_to_return = LLMProviderModel(
        name=provider_model.name,
        provider=provider_model.provider,
        api_key=provider_model.api_key,
        api_base=provider_model.api_base,
        api_version=provider_model.api_version,
        custom_config=provider_model.custom_config,
        default_model_name=provider_model.default_model_name,
        fast_default_model_name=provider_model.fast_default_model_name,
        model_names=provider_model.model_names,
        is_default_provider=None,
    )
    return FullLLMProvider.from_model(model_to_return)


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
