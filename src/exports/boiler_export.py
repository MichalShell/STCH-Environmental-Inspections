import pandas as pd
import io

# ✅ Helper to correctly read checkbox values
def get_checkbox(form_data, field):
    return "Checked" if form_data.get(field + "cb") == "Checked" else "Not Checked"


def generate_boilerExcel(form_data):

    print("Generating Excel with form data:", form_data)

    # ✅ Define consistent column order
    columns = [
        "Operator","Boiler Number","Boiler Status", "Date", "Time", "Water Level",
        "Blow Down Water Column", "Blow Down Sight Glass", "Blow Down Low Water Cut Out",
        "Bottom Blow Boiler",
        "Checked Burner Ring For Proper Flame Pattern", "Checked Excess Oxygen For Proper Level",
        "Checked For Excess Combustibles", "Visually Checked Entire Boiler",
        "Visible Emissions",
        "Time Smoke First Observed", "Time Smoke Cleared", "Comments"
    ]

    # ✅ Map form data (FIXED ✅ checkboxes now read correctly)
    data = {
        "Operator": form_data.get("operator"),
        "Boiler Number": form_data.get("boilerNumber"),
        "Boiler Status":form_data.get("boilerStatus"),
        "Date": form_data.get("date"),
        "Time": form_data.get("time"),
        "Water Level": get_checkbox(form_data, "check_water_level"),
        "Blow Down Water Column": get_checkbox(form_data, "blowDownWaterColumn"),
        "Blow Down Sight Glass": get_checkbox(form_data, "blowDownSightGlass"),
        "Blow Down Low Water Cut Out": get_checkbox(form_data, "blowDownLowWaterCutOut"),
        "Bottom Blow Boiler": get_checkbox(form_data, "bottomBlowBoiler"),

        "Checked Burner Ring For Proper Flame Pattern": get_checkbox(form_data, "checkedBurnerRingForProperFlamePattern"),
        "Checked Excess Oxygen For Proper Level": get_checkbox(form_data, "checkedExcessOxygenForProperLevel"),
        "Checked For Excess Combustibles": get_checkbox(form_data, "checkedForExcessCombustibles"),
        "Visually Checked Entire Boiler": get_checkbox(form_data, "visuallyCheckedEntireBoiler"),

        "Visible Emissions": form_data.get("emissions"),

        "Time Smoke First Observed": form_data.get("timeSmokeFirstObserved"),
        "Time Smoke Cleared": form_data.get("timeSmokeCleared"),
        "Comments": form_data.get("comments")
    }

    # ✅ Create DataFrame
    df = pd.DataFrame([data], columns=columns)

    output = io.BytesIO()

    # ✅ Write to Excel
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='WorkLog')

        workbook = writer.book
        worksheet = writer.sheets['WorkLog']

        # ✅ Add Excel Table (important for Power Automate)
        (max_row, max_col) = df.shape

        worksheet.add_table(
            0, 0, max_row, max_col - 1,
            {
                'columns': [{'header': col} for col in df.columns],
                'style': 'Table Style Medium 2'
            }
        )

        # ✅ Set column width
        worksheet.set_column(0, max_col - 1, 20)

    output.seek(0)

    return output