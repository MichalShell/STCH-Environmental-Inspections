let engines = []; // Store the engine records loaded from the server.

document.addEventListener("DOMContentLoaded", function () {
  // Attach date validation listeners (all date fields are optional in this form)
  attachDateValidationListeners(
    ["arrivalDate", "date", "departureDate", "manufactureDate"],
    ["arrivalDate", "date", "departureDate", "manufactureDate"]
  );

  // Load engine data and equipment options before enabling form interactions.
  Promise.all([
    loadEngines(),
    loadEquipment()
  ]).then(() => {
    setupEventListeners();
  });

  const initialInput = document.getElementById("initialMeterRead");
  const finalInput = document.getElementById("finalMeterRead");
  const form = document.querySelector("form");

  // Calculate the running time from the two meter readings.
  function calculateTotal() {
    const initial = parseFloat(initialInput.value) || 0;
    const final = parseFloat(finalInput.value) || 0;

    if (final >= initial) {
      const total = final - initial;
      document.getElementById("total_time").value = total.toFixed(2);
    } else {
      document.getElementById("total_time").value = "Invalid";
    }
  }

  // Prevent invalid input where the initial reading is higher than the final reading.
  function validateMeterRange() {
    const initial = parseFloat(initialInput.value);
    const final = parseFloat(finalInput.value);

    if (Number.isNaN(initial) || Number.isNaN(final)) {
      initialInput.setCustomValidity("");
      finalInput.setCustomValidity("");
      return true;
    }

    if (initial > final) {
      initialInput.setCustomValidity("Initial meter read cannot be greater than final meter read.");
      finalInput.setCustomValidity("Final meter read must be greater than or equal to initial meter read.");
      return false;
    }

    initialInput.setCustomValidity("");
    finalInput.setCustomValidity("");
    return true;
  }

  // Recalculate totals and validate the meter range whenever either field changes.
  initialInput.addEventListener("input", () => {
    calculateTotal();
    validateMeterRange();
  });

  finalInput.addEventListener("input", () => {
    calculateTotal();
    validateMeterRange();
  });

  function fillMissingDates() {
    const arrivalDate = document.getElementById("arrivalDate");
    if (!arrivalDate) return;

    const today = new Date().toISOString().split("T")[0];
    if (!arrivalDate.value) {
      arrivalDate.value = today;
    }
    // Do NOT auto-fill departureDate - leave it empty if user didn't enter it
  }

  if (form) {
    form.addEventListener("submit", function (event) {

      document.getElementById("fuelInput").disabled = false;  
      const dateFields = ["arrivalDate", "date", "departureDate", "manufactureDate"];
      const excludeFields = ["departureDate", "manufactureDate"];

      const isDateValid = validateAndFillDates(dateFields, excludeFields);
      if (!isDateValid) {
        event.preventDefault();
        return false;
      }

      fillMissingDates();

      const isValid = validateMeterRange();
      if (!isValid) {
        event.preventDefault();
        initialInput.reportValidity();
        finalInput.reportValidity();
      }
    });
  }

  // Update the on-site/off-site status based on whether a departure date exists.
  const departureDate = document.getElementById("departureDate");
  const onsiteStatus = document.getElementById("onsiteStatus");

  function updateStatus() {
    onsiteStatus.value = departureDate.value ? "Off-Site" : "On-Site";
  }

  updateStatus();
  departureDate.addEventListener("change", updateStatus);
});

// Fetch the engine inventory from the Flask API.
function loadEngines() {
  return fetch("/api/engines")
    .then(res => res.json())
    .then(data => {
      engines = data;
      console.log("Engines loaded - Total count:", engines.length);
    })
    .catch(err => console.error("Fetch error:", err));
}

// Attach the form-change handlers after the data has loaded.
function setupEventListeners() {
  document.getElementById("equipment").addEventListener("change", filterModels);
  document.getElementById("modelNumber").addEventListener("change", autoFillFromEquipment);
}

// Filter the available model choices based on the selected equipment type.
function filterModels() {
  const selectedEquipment = document.getElementById("equipment").value;
  const modelDropdown = document.getElementById("modelNumber");
  const modelInput = document.getElementById("modelNumberInput");

  // Clear all fields when equipment changes
  clearFormFields();

  // Equipment is "Other" → skip the dropdown entirely, type the model by hand.
  if (selectedEquipment && selectedEquipment.toLowerCase() === "other") {
    modelDropdown.style.display = "none";
    modelInput.style.display = "block";
    modelInput.required = true
    modelInput.value = "";
    toggleManualMode(true);
    return;
  }

  // Normal mode
  modelDropdown.style.display = "block";
  modelInput.required = true;
  modelInput.style.display = "none";
  modelDropdown.innerHTML = '<option disabled selected hidden>Select Model</option>';

  const filtered = engines.filter(e => e.equipment === selectedEquipment);

  if (filtered.length === 0) {
    console.warn(`No engines found for equipment: "${selectedEquipment}"`);
    const noOption = document.createElement("option");
    noOption.textContent = "No models available";
    noOption.disabled = true;
    modelDropdown.appendChild(noOption);
    toggleManualMode(false);
    return;
  }

  filtered.forEach((engine, index) => {
    const option = document.createElement("option");
    option.value = index; // index inside filtered list

    const modelText = engine.model_number ? engine.model_number : "(No Model)";
    option.textContent = `${engine.manufacturer} ${modelText}`;

    // Store the position in the full engines array
    option.dataset.engineIndex = engines.indexOf(engine);
    modelDropdown.appendChild(option);
  });

  const otherOption = document.createElement("option");
  otherOption.value = "OTHER";
  otherOption.textContent = "Other";
  modelDropdown.appendChild(otherOption);

  toggleManualMode(false);
}

// Fill the form fields from the selected engine record.
function autoFillFromEquipment() {
  const modelDropdown = document.getElementById("modelNumber");
  const modelInput = document.getElementById("modelNumberInput");

  // Equipment is "Other" — the dropdown isn't in play at all.
  if (modelDropdown.style.display === "none") return;

  if (modelDropdown.value === "OTHER") {
    clearFormFields();
    modelInput.style.display = "block";
    modelInput.required = true;

    modelInput.value = "";
    toggleManualMode(true);
    modelInput.focus();
    return;
  }

  // A real model was chosen → always hide the manual box again.
  modelInput.style.display = "none";
  modelInput.required = false;

  const selectedOption = modelDropdown.selectedOptions[0];
  if (!selectedOption) return;

  const engine = engines[Number(selectedOption.dataset.engineIndex)];
  if (!engine) return;

  document.getElementById("manufacturerInput").value = engine.manufacturer || "";
  document.getElementById("modelNumberInput").value = engine.model_number || "";
  document.querySelector("[name='serialNumber']").value = engine.serial_number || "";
  document.getElementById("manufactureDate").value = engine.manufacture_date || "";
  document.getElementById("TierInput").value = engine.tier || "";
  console.log("engine.fuel =", engine.fuel);
  document.getElementById("fuelInput").value = engine.fuel || "";
  document.getElementById("horsepowerInput").value = Array.isArray(engine.horsepower)
    ? engine.horsepower[0]
    : (engine.horsepower || "");

  toggleManualMode(false);
}

// Enable or disable editing for the auto-filled fields.
function toggleManualMode(enable) {
  const fields = [
    "manufacturerInput",
    "modelNumberInput",
    "TierInput",
    "fuelInput",
    "horsepowerInput"
  ];

  fields.forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;

    if (el.tagName === "SELECT") {
      el.disabled = !enable;   // select fields use disabled
    } else {
      el.readOnly = !enable;   // input fields use readOnly
    }
  });

  document.querySelector("[name='serialNumber']").readOnly = !enable;
  document.getElementById("manufactureDate").readOnly = !enable;
}

// Clear the auto-filled details.
function clearFormFields() {
  document.getElementById("manufacturerInput").value = "";
  document.getElementById("modelNumberInput").value = "";
  document.querySelector("[name='serialNumber']").value = "";
  document.getElementById("manufactureDate").value = "";
  document.getElementById("TierInput").value = "";
  document.getElementById("fuelInput").value = "";
  document.getElementById("horsepowerInput").value = "";
}

// Load the equipment list from the API and populate the dropdown.
function loadEquipment() {
  return fetch("/api/equipment")
    .then(res => res.json())
    .then(data => {
      const dropdown = document.getElementById("equipment");
      dropdown.innerHTML = '<option disabled selected>Select Equipment</option>';

      data.forEach(eq => {
        const option = document.createElement("option");
        option.value = eq;
        option.textContent = eq;
        dropdown.appendChild(option);
      });

      const other = document.createElement("option");
      other.value = "Other";
      other.textContent = "Other";
      dropdown.appendChild(other);
    });
}
