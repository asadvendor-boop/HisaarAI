from hisaarai.agents.ap_skeleton import root_agent as protected_ap
from hisaarai.agents.recovery_fleet import root_agent as recovery_fleet


def _models_by_agent_name(agent: object) -> dict[str, str]:
    models: dict[str, str] = {}

    def walk(node: object) -> None:
        name = getattr(node, "name", None)
        model = getattr(getattr(node, "model", None), "model", None)
        if isinstance(name, str) and isinstance(model, str):
            models[name] = model
        for child in getattr(node, "sub_agents", []):
            walk(child)

    walk(agent)
    return models


def test_final_agent_routing_uses_only_gemini_37_flash_and_flash_lite() -> None:
    assert protected_ap.model.model == "gemini-3.7-flash"
    assert _models_by_agent_name(recovery_fleet) == {
        "raasid_observer": "gemini-3.5-flash-lite",
        "kashif_investigator": "gemini-3.7-flash",
        "muslih_planner": "gemini-3.7-flash",
        "clean_ap_standby": "gemini-3.7-flash",
        "shaahid_witness": "gemini-3.5-flash-lite",
    }
