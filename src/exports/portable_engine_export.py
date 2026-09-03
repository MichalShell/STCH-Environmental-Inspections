import pandas as pd
import io
from flask import Flask, request
 
def generate_portableExcel(form_data):
 
    print(form_data)
    # ✅ Define consistent column order (important!)
    columns = [
       "Operator", "Contractor","Equipment", "Other Equipment", "Location", "Purpose", "Arrival Date", "In Service Date", "Initial Meter Read", "Departure Date","Final Meter Read","Total Hours",
       "Horsepower" ,"Manufacturer","Model Number", "Other Model Number","Serial Number", "Manufacture Date", "Tier", "Fuel", "On-Site Status",  "Comments"
    ]
 
    equipment = form_data.get("equipment")
 
    if equipment == "Other":
        equipment = form_data.get("other_equipment") or "Other"
 
    purpose = form_data.get("purpose")
 
    if purpose == "Other":
        purpose = form_data.get("other_purpose") or "Other"
 
    model_number=form_data.get("modelNumber")
 
    if model_number == "Other":
        model_number = form_data.get("modelNumberOther") or "Other"
 
    # ✅ Convert incoming form data keys to match column names
    data = {
        "Operator": form_data.get("operator"),
        "Contractor":form_data.get("contractor"),
        "Equipment": equipment,
        "Other Equipment": form_data.get("other_equipment"),
        "Location": form_data.get("location"),
        "Purpose": purpose,
        "Arrival Date": form_data.get("arrivalDate"),
        "In Service Date": form_data.get("date"),
        "Initial Meter Read": form_data.get("initialMeterRead"),
        "Departure Date": form_data.get("departureDate"),
        "Final Meter Read": form_data.get("finalMeterRead"),
        "Total Hours": float(request.form.get("totalHours") or 0),
        "Horsepower": form_data.get("horsepower"),
        "Manufacturer": form_data.get("manufacturer"),
        "Model Number": model_number,
        "Other Model Number": form_data.get("modelNumberOther"),
        "Serial Number": form_data.get("serialNumber"),
        "Manufacture Date": form_data.get("manufactureDate"),
        "Tier": form_data.get("tier"),
        "Fuel": form_data.get("fuel"),
        "On-Site Status": form_data.get("onsiteStatus"),
        "Comments": form_data.get("comments")  
 
    }
   
    print("Export form data portabke engine:",data)
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
