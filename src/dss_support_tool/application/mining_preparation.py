from __future__ import annotations

from typing import Any

from dss_support_tool.application.mining_guidance_data import load_mining_guidance_data


GUIDANCE = load_mining_guidance_data()
DIFFICULTY_THRESHOLDS = GUIDANCE["difficultyThresholds"]


def build_mining_preparation(resource: dict[str, Any]) -> dict[str, Any] | None:
    family = str(resource.get("family") or "").lower()
    if family != "mining":
        return None

    stats = resource.get("stats") or {}
    group_ids = {str(group_id) for group_id in resource.get("groupIds", []) or [] if group_id}
    raw_kind = str(resource.get("rawKind") or "unknown").lower()
    name = str(resource.get("name") or "Unknown Resource")

    profile = _difficulty_profile(stats)
    platform = _platform_profile(group_ids, raw_kind)
    scan_signature = _format_number(stats.get("scanSignature"))
    ground_scan_signature = _format_number(stats.get("groundScanSignature"))

    return {
        "difficulty": profile,
        "minimalRequired": _build_minimal_requirement(platform, profile),
        "recommendedLoadouts": _build_loadouts(platform, profile, name),
        "scanning": {
            "headline": _scan_headline(platform),
            "workflow": _scan_workflow(platform, scan_signature, ground_scan_signature),
            "cautions": _scan_cautions(platform, profile, name),
        },
    }


def _difficulty_profile(stats: dict[str, Any]) -> dict[str, Any]:
    resistance = _float_or_none(stats.get("resistance"))
    instability = _float_or_none(stats.get("instability"))
    explosion = _float_or_none(stats.get("explosionMultiplier"))
    cluster = _float_or_none(stats.get("clusterFactor"))
    extreme = DIFFICULTY_THRESHOLDS["extreme"]
    advanced = DIFFICULTY_THRESHOLDS["advanced"]
    standard = DIFFICULTY_THRESHOLDS["standard"]

    if (
        (resistance is not None and resistance >= float(extreme["resistanceMin"]))
        or (instability is not None and instability >= float(extreme["instabilityMin"]))
        or (explosion is not None and explosion >= float(extreme["explosionMin"]))
    ):
        level = "extreme"
        label = str(extreme["label"])
        summary = str(extreme["summary"])
    elif (
        (resistance is not None and resistance >= float(advanced["resistanceMin"]))
        or (instability is not None and instability >= float(advanced["instabilityMin"]))
        or (explosion is not None and explosion >= float(advanced["explosionMin"]))
    ):
        level = "advanced"
        label = str(advanced["label"])
        summary = str(advanced["summary"])
    else:
        level = "standard"
        label = str(standard["label"])
        summary = str(standard["summary"])

    trait_lines: list[str] = []
    if resistance is not None:
        trait_lines.append(f"Resistance {format_metric(resistance)}")
    if instability is not None:
        trait_lines.append(f"Instability {format_metric(instability)}")
    if explosion is not None:
        trait_lines.append(f"Explosion {format_metric(explosion)}")
    if cluster is not None:
        trait_lines.append(f"Cluster {format_metric(cluster)}")

    return {
        "level": level,
        "label": label,
        "summary": summary,
        "traits": trait_lines,
    }


def _platform_profile(group_ids: set[str], raw_kind: str) -> str:
    if "fps-mining" in group_ids:
        return "hand"
    if "roc-mining" in group_ids or raw_kind == "crystal":
        return "roc"
    return "ship"


def _build_minimal_requirement(platform: str, profile: dict[str, Any]) -> dict[str, Any]:
    if platform == "hand":
        return {
            "label": "Minimal Required",
            "platform": "FPS mining",
            "vehicle": "On foot",
            "tool": "Pyro RYT Multi-Tool with OreBit Mining Attachment",
            "notes": [
                "Bring a backpack so harvested gems do not cap out immediately.",
                "Use this only for hand-minable nodes and caves.",
            ],
        }
    if platform == "roc":
        return {
            "label": "Minimal Required",
            "platform": "Vehicle mining",
            "vehicle": "Greycat ROC or ROC-DS",
            "tool": "Arbor MHV mining laser",
            "notes": [
                "ROC-class crystals are the minimum practical setup for this resource family.",
                "A ship miner is not the efficient first choice for these nodes.",
            ],
        }
    prospector_note = (
        "Prospector is the practical minimum, but high-mass rocks may still push you into MOLE territory."
        if profile["level"] in {"advanced", "extreme"}
        else "A Prospector can cover the minimum viable ship-mining path for this resource."
    )
    return {
        "label": "Minimal Required",
        "platform": "Ship mining",
        "vehicle": "MISC Prospector",
        "tool": "Size 1 mining head",
        "notes": [
            prospector_note,
            "Detailed scan values still decide whether a specific rock is worth attempting solo.",
        ],
    }


def _build_loadouts(platform: str, profile: dict[str, Any], resource_name: str) -> list[dict[str, Any]]:
    if platform == "hand":
        return [
            {
                "id": "hand-mining",
                "label": "Hand Mining",
                "platform": "Solo",
                "vehicle": "On foot",
                "radar": "None",
                "head": "OreBit Mining Attachment",
                "modules": ["None"],
                "gadgets": ["None"],
                "fit": "Use for caves and hand nodes only.",
                "notes": [
                    "Pair with a backpack for collection efficiency.",
                    "Prospector, Golem, and MOLE are not the right tools for this resource class.",
                ],
            }
        ]

    if platform == "roc":
        return [
            {
                "id": "roc-mining",
                "label": "ROC",
                "platform": "Solo vehicle",
                "vehicle": "Greycat ROC / ROC-DS",
                "radar": "Use the carrier ship scanner to locate surface clusters, then switch to the ROC.",
                "head": "Arbor MHV mining laser",
                "modules": ["Vehicle mining modifiers if fitted"],
                "gadgets": ["None"],
                "fit": "Best for surface gem nodes after a low-altitude scan pass.",
                "notes": [
                    "Treat this as a surface vehicle route, not a ship-mining route.",
                    "If you are hunting only this resource class, bring a carrier plus ROC rather than a Prospector.",
                ],
            }
        ]

    loadouts = [
        {
            "id": "golem",
            "label": "Starter Golem",
            "platform": "Solo starter",
            "vehicle": "Drake Golem",
            "radar": "Surveyor-Lite industrial radar",
            "head": "Pitman Mining Laser (stock starter fit)",
            "modules": ["Keep stock until you can tune a dedicated setup"],
            "gadgets": _starter_gadgets(profile["level"]),
            "fit": "Low-cost scouting and starter cracking.",
            "notes": [
                "The Golem is the cheapest clean entry into ship mining, but not the best answer for hard rocks.",
                "Use it to learn scans, chase easier rocks, and skip bad detailed scans quickly.",
            ],
        },
        {
            "id": "prospector",
            "label": "Solo Prospector",
            "platform": "Solo optimal",
            "vehicle": "MISC Prospector",
            "radar": "Surveyor-Lite industrial radar",
            "head": "Helix I Mining Laser",
            "modules": ["Rieger-C3 Module", "Focus III Module", "Carry Surge and Stampede actives as swap-ins"],
            "gadgets": _prospector_gadgets(profile["level"]),
            "fit": _prospector_fit(profile["level"], resource_name),
            "notes": [
                "This is the main solo recommendation when the user only has one ship and wants real throughput.",
                "The Helix/Rieger/Focus combination is based on current community solo loadout guidance and the Helix's higher power profile.",
            ],
        },
        {
            "id": "mole",
            "label": "Crew MOLE",
            "platform": "Crew optimal",
            "vehicle": "ARGO MOLE",
            "radar": "Surveyor industrial radar",
            "head": "Mixed S2 heads: Arbor MH2 baseline plus Lancet MH2 support",
            "modules": ["Focus III Module", "Rieger-C3 Module", "Carry Stampede and Surge for tough fractures"],
            "gadgets": _mole_gadgets(profile["level"]),
            "fit": _mole_fit(profile["level"], resource_name),
            "notes": [
                "The MOLE is the safest recommendation once rocks become unstable, high mass, or time-sensitive.",
                "Use separate turret roles: one stable baseline beam and one stronger assist beam when needed.",
            ],
        },
    ]

    if profile["level"] == "extreme":
        loadouts[0]["notes"].append("Treat extreme rocks as optional in the Golem. Walk away from bad mass or narrow windows.")
        loadouts[1]["notes"].append("Prospector is viable only when the mass is reasonable and the pilot already knows the crack profile.")

    return loadouts


def _scan_headline(platform: str) -> str:
    if platform == "hand":
        return "Search caves, wreck interiors, and hand-minable pockets."
    if platform == "roc":
        return "Scan low and slow over surfaces, then swap into the ROC once you confirm gem nodes."
    return "Use ship ping first, then detailed scan before you commit to a fracture."


def _scan_workflow(platform: str, scan_signature: str, ground_scan_signature: str) -> list[str]:
    if platform == "hand":
        return [
            "Bring the Pyro RYT Multi-Tool, OreBit attachment, and a backpack before leaving the station.",
            "Search caves and enclosed POI routes rather than wide open terrain.",
            "Inspect the node directly and mine only what you can safely carry back out.",
        ]
    if platform == "roc":
        return [
            "Run a low-altitude search pass in a support ship and look for gem fields on the surface.",
            "Land nearby, deploy the ROC, and inspect nodes from close range before you start the charge cycle.",
            "Use the ROC only on vehicle-sized gems; leave hand nodes to the multitool and big rocks to ship miners.",
        ]

    workflow = [
        "Start with broad ping sweeps, then reduce speed and rescan once a cluster resolves.",
        "Approach the candidate rock, switch to detailed scan, and read resistance, instability, and mass before committing.",
    ]
    if scan_signature != "Unknown" or ground_scan_signature != "Unknown":
        workflow.append(
            f"Known signatures for this resource are around ship {scan_signature} / ground {ground_scan_signature}. Treat multiples as possible clusters, not guaranteed pure hits."
        )
    workflow.extend(
        [
            "If the first detailed scan looks ugly for your ship, skip it and keep moving instead of forcing the crack.",
            "For volatile ore, crack everything before you start scooping so you are not holding a half-finished problem under timer pressure.",
        ]
    )
    return workflow


def _scan_cautions(platform: str, profile: dict[str, Any], resource_name: str) -> list[str]:
    cautions: list[str] = []
    if platform == "ship":
        cautions.append("Detailed scan quality matters more than the resource name alone. Bad mass can invalidate a good ore.")
    if resource_name.lower() in {"quantainium", "quantanium"}:
        cautions.append("Quantanium-style volatile ore should be cracked cleanly and moved fast. Do not overcharge or linger on half-scooped loads.")
    if profile["level"] == "extreme":
        cautions.append("Expect narrow optimal windows. Bring a stability gadget or crew support instead of brute-forcing it.")
    elif profile["level"] == "advanced":
        cautions.append("Use gadgets proactively. This target is still easy to lose if you chase the bar too aggressively.")
    return cautions


def _starter_gadgets(level: str) -> list[str]:
    if level == "extreme":
        return ["WaveShift for a wider window", "BoreMax if the rock is unstable and worth the slower crack"]
    if level == "advanced":
        return ["WaveShift", "Okunis"]
    return ["Okunis for easier charge control"]


def _prospector_gadgets(level: str) -> list[str]:
    if level == "extreme":
        return ["BoreMax for stability", "WaveShift when the optimal window is too narrow", "Sabir if resistance is the main blocker"]
    if level == "advanced":
        return ["WaveShift", "BoreMax", "Okunis"]
    return ["Okunis", "WaveShift"]


def _mole_gadgets(level: str) -> list[str]:
    if level == "extreme":
        return ["BoreMax on the problem rock", "Okunis or WaveShift on the support ship if the crew wants a larger working window"]
    if level == "advanced":
        return ["WaveShift", "BoreMax"]
    return ["Okunis", "WaveShift"]


def _prospector_fit(level: str, resource_name: str) -> str:
    if level == "extreme":
        return f"Best solo setup for {resource_name}, but only on manageable rock mass. Skip bad scans and leave oversized rocks for crew mining."
    if level == "advanced":
        return f"Optimal solo fit for {resource_name} when you want real throughput without moving into multicrew."
    return f"Fastest all-around solo fit for {resource_name} in a standard ship-mining loop."


def _mole_fit(level: str, resource_name: str) -> str:
    if level == "extreme":
        return f"Best answer for the hardest {resource_name} rocks. Use crew coordination and mixed beams rather than single-laser force."
    if level == "advanced":
        return f"Safest high-yield choice for {resource_name} when you can bring crew."
    return f"High-capacity option for {resource_name} when you want fewer refinery trips and more margin."


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _format_number(value: Any) -> str:
    number = _float_or_none(value)
    if number is None:
        return "Unknown"
    if number.is_integer():
        return str(int(number))
    return format_metric(number)


def format_metric(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")
