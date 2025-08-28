import adalflow as adal

from api.core.config import get_config_manager


def get_embedder() -> adal.Embedder:
    manager = get_config_manager()
    embedder_config = manager.get_embedder_config() or {}

    # --- Initialize Embedder ---
    model_client_class = embedder_config.get("model_client")
    if model_client_class is None:
        raise KeyError("model_client")

    if "initialize_kwargs" in embedder_config:
        model_client = model_client_class(**embedder_config["initialize_kwargs"])
    else:
        model_client = model_client_class()
    embedder = adal.Embedder(
        model_client=model_client,
        model_kwargs=embedder_config.get("model_kwargs", {}),
    )
    return embedder
