from collections import defaultdict

REDEPLOYMENT_KEYS = [
    "namespace",
    "name",
    "resource",
]

AVAILABLE_RESOURCES = [
    "deployment",
    "stateful-set",
    "job",
]


def validate_secret_label(
    label_name: str,
    label_value: str,
    redeployments: defaultdict,
) -> dict:
    if isinstance(redeployments, dict):
        redeployments = defaultdict(dict, redeployments)
    if not label_name.startswith("redeployable"):
        return {}
    label_keys = label_name.split("-")
    if len(label_keys) != 3:
        raise ValueError(
            f"Invalid redeployment label '{label_name}'. "
            "Must be in the format "
            "'redeployable-<number>-<name/namespace/resource>'. "
            f"Skipping..."
        )
    else:
        label_number = label_keys[1]
        try:
            label_number = int(label_number)
        except ValueError:
            raise ValueError(
                f"Invalid number '{label_number}' "
                f" for redeployment label '{label_name}'."
                "Must be an integer. Skipping..."
            )
        label_key = label_keys[2]
        if label_key not in REDEPLOYMENT_KEYS:
            raise ValueError(
                f"Invalid redeployment key '{label_key}'. "
                f"Must be in {REDEPLOYMENT_KEYS}. "
                "Skipping..."
            )
        existing_label_keys = redeployments.get(label_number, None)
        if existing_label_keys:
            if label_key in existing_label_keys:
                raise ValueError(
                    f"Duplicate redeployment key '{label_key}' "
                    f"for redeployment label '{label_name}'. "
                    "Skipping..."
                )
        if label_key == "resource" and label_value not in AVAILABLE_RESOURCES:
            raise ValueError(
                f"Invalid resource '{label_value}'. "
                f"Must be in {AVAILABLE_RESOURCES}. "
                "Skipping..."
            )
        redeployments[label_number][label_key] = label_value
    return redeployments
