import pandas as pd
import io
from flask import Flask, request

def generate_generatorExcel(form_data):


    print(form_data)
    # ✅ Define consistent column order (important!)
    columns = [
       "Inspector Name","Contractor","Generator", "Date", "Start Time", "Stop Time", "Run Duration",
       "Run Reason" ,"Emergency Type","Comments", "Visible Emissions","Comment Visible Emissions"
    ]

    vendor = form_data.get("vendor")

    if vendor == "Other":
        vendor = form_data.get("other_vendor") or "Other"

    run_reason = form_data.get("run_reason")

    if run_reason == "Other":
        run_reason = form_data.get("other_run_reason") or "Other"
 
    run_duration = form_data.get("run_duration")

    if run_duration:
        hours, minutes = map(int, run_duration.split(":"))
        total_hours = hours + (minutes / 60)
    else:
        total_hours = 0

    Emergency_type=form_data.get("emergency_type")

    if Emergency_type=="Other":
        Emergency_type = form_data.get("other_emergency_type") or "Other"


#  round to 2 decimal places
    total_hours = round(total_hours, 2)

    print(total_hours)



    # ✅ Convert incoming form data keys to match column names
    data = {
        "Inspector Name": form_data.get("inspector"),
        # "Contractor":form_data.get("contractor"),
        "Contractor": vendor,
        "Generator": form_data.get("generator"),
        "Date": form_data.get("date"),
        "Start Time": form_data.get("start_time"),
        "Stop Time": form_data.get("stop_time"),
        "Run Duration": total_hours,
        "Run Reason": run_reason,
        "Emergency Type":Emergency_type,
        "Comments": form_data.get("comments"),
        "Visible Emissions": form_data.get("emissions"),
        "Comment Visible Emissions": form_data.get("visibleEmissionComment")
        

    }

# columns inferred automatically
    df = pd.DataFrame([data], columns=columns)

    output = io.BytesIO()

    # ✅ Use Excel writer with xlsxwriter (supports tables)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='WorkLog')

        workbook = writer.book
        worksheet = writer.sheets['WorkLog']

        # ✅ Add Excel Table (THIS is the key for Power Automate)
        (max_row, max_col) = df.shape

        worksheet.add_table(
            0, 0, max_row, max_col - 1,
            {
                'columns': [{'header': col} for col in df.columns],
                'style': 'Table Style Medium 2'
            }
        )

        # ✅ Optional column width (nice UX)
        worksheet.set_column(0, max_col - 1, 20)

    output.seek(0)

    return output