import json
import os


DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "portable_engine_inventory.json")


def load_engine_inventory():
    """Read the portable engine inventory from disk."""
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_new_engine(form_data):
    """Append a new engine entry when the user selects 'Other'."""
    inventory = load_engine_inventory()

    equipment_value = form_data.get("other_equipment") or form_data.get("equipment")

    new_entry = {
        "equipment": equipment_value,
        "manufacturer": form_data.get("manufacturer"),
        "model_number": form_data.get("modelNumber"),
        "serial_number": form_data.get("serialNumber"),
        "manufacture_date": form_data.get("manufactureDate"),
        "tier": form_data.get("tier"),
        "fuel": form_data.get("fuel"),
        "horsepower": form_data.get("horsepower")
    }

    print("✅ Saving new engine:", new_entry)

    inventory.append(new_entry)

    with open(DATA_FILE, "w") as f:
        json.dump(inventory, f, indent=4)

    print("✅ Engine saved to:", DATA_FILE)
    return new_entry



def save_new_model(form_data):
    """
    Save a new model under an existing equipment.
    """

    inventory = load_engine_inventory()

    new_entry = {
        "equipment": form_data.get("equipment"),  # from top dropdown
        "manufacturer": form_data.get("manufacturer"),
        "model_number": form_data.get("modelNumber"),  # modelNumberOther was copied here
        "serial_number": form_data.get("serialNumber"),
        "manufacture_date": form_data.get("manufactureDate"),
        "tier": form_data.get("tier"),
        "fuel": form_data.get("fuel"),
        "horsepower": form_data.get("horsepower")
    }

    existing = next(
        (
            item
            for item in inventory
            if item.get("equipment") == new_entry["equipment"]
            and item.get("model_number") == new_entry["model_number"]
        ),
        None
    )

    if existing:
        print("✅ Model already exists")
        return existing

    inventory.append(new_entry)

    with open(DATA_FILE, "w") as f:
        json.dump(inventory, f, indent=4)

    print("✅ New model saved:", new_entry)

    return new_entry
