let config = {};
let updateInterval = null;

async function init() {
  try {
    const res = await fetch("/config");
    config = await res.json();
    applyConfig();
    startLiveUpdate();
  } catch (err) {
    console.error("Init config error:", err);
  }
}

function startLiveUpdate() {
  updateInterval = setInterval(async () => {
    try {
      const sensorRes = await fetch("/api/sensors");
      if (sensorRes.ok) {
        const data = await sensorRes.json();
        updateLcdDisplay(data);
      }
    } catch (err) {
      console.log("Fetching sensors failed:", err);
    }
  }, 1000);
}

function updateLcdDisplay(data) {
  const valueEl = document.getElementById("lcdValue");
  const cpuTag = document.getElementById("lcdCpuLabel");
  const gpuTag = document.getElementById("lcdGpuLabel");
  const unitC = document.getElementById("unitC");
  const unitF = document.getElementById("unitF");
  const unitPct = document.getElementById("unitPct");

  // Quick info telemetry cards
  const qCpu = document.getElementById("quickCpuTemp");
  const qGpu = document.getElementById("quickGpuTemp");
  const qLoad = document.getElementById("quickCpuLoad");

  if (qCpu) qCpu.textContent = data.cpu_temp !== undefined ? `${data.cpu_temp}°C` : "--";
  if (qGpu) qGpu.textContent = data.gpu_temp !== undefined ? `${data.gpu_temp}°C` : "--";
  if (qLoad) qLoad.textContent = data.cpu_usage !== undefined ? `${data.cpu_usage}%` : "--";

  let displayValue;
  let activeTag = "cpu";
  let showPct = false;

  switch (config.display_mode) {
    case "cpu":
      displayValue = data.cpu_temp ?? "--";
      activeTag = "cpu";
      break;
    case "gpu":
      displayValue = data.gpu_temp ?? "--";
      activeTag = "gpu";
      break;
    case "alternate": {
      const altIntervalMs = (config.alternate_interval || 3) * 1000;
      const isCpuTurn = (Date.now() % (altIntervalMs * 2)) < altIntervalMs;
      if (isCpuTurn) {
        displayValue = data.cpu_temp ?? "--";
        activeTag = "cpu";
      } else {
        displayValue = data.gpu_temp ?? "--";
        activeTag = "gpu";
      }
      break;
    }
    case "cpu_usage":
      displayValue = data.cpu_usage ?? "--";
      activeTag = "cpu";
      showPct = true;
      break;
    default:
      displayValue = data.cpu_temp ?? "--";
      activeTag = "cpu";
  }

  // Convert unit if fahrenheit
  if (config.temperature_unit === "fahrenheit" && !showPct && typeof displayValue === 'number') {
    displayValue = Math.round((displayValue * 9) / 5 + 32);
  }

  valueEl.textContent = displayValue;

  // Active tags update
  if (cpuTag) cpuTag.className = `sensor-tag ${activeTag === "cpu" ? "active" : ""}`;
  if (gpuTag) gpuTag.className = `sensor-tag ${activeTag === "gpu" ? "active" : ""}`;

  // Unit tags update
  if (unitPct) unitPct.className = `unit-tag ${showPct ? "active" : ""}`;
  if (unitC) unitC.className = `unit-tag ${!showPct && config.temperature_unit === "celsius" ? "active" : ""}`;
  if (unitF) unitF.className = `unit-tag ${!showPct && config.temperature_unit === "fahrenheit" ? "active" : ""}`;

  // Color reactive or static
  if (config.color_mode === "temperature" && typeof displayValue === 'number') {
    const rawTemp = (activeTag === "gpu" ? data.gpu_temp : data.cpu_temp) || displayValue;
    const colorHex = getTempColor(rawTemp);
    valueEl.style.color = "#" + colorHex;
    valueEl.style.textShadow = `0 0 20px #${colorHex}, 0 0 40px #${colorHex}88`;
  } else {
    const hex = config.color || "ff0000";
    valueEl.style.color = "#" + hex;
    valueEl.style.textShadow = `0 0 20px #${hex}, 0 0 40px #${hex}88`;
  }
}

function getTempColor(temp) {
  const map = config.temp_color_map || [
    { max: 30, color: "00ffff" },
    { max: 50, color: "00ff00" },
    { max: 70, color: "ffff00" },
    { max: 90, color: "ff8800" },
    { max: 999, color: "ff0000" }
  ];

  for (const entry of map) {
    if (temp <= entry.max) return entry.color;
  }
  return map[map.length - 1].color;
}

function updateTicks(val) {
  document.querySelectorAll(".tick-label").forEach((el) => {
    const tickSec = parseInt(el.textContent);
    if (tickSec === val) {
      el.classList.add("active");
    } else {
      el.classList.remove("active");
    }
  });
}

function applyConfig() {
  setMode(config.display_mode || "cpu");
  setUnit(config.temperature_unit || "celsius");
  setColorMode(config.color_mode || "static");
  setColor(config.color || "ff0000");

  const slider = document.getElementById("interval");
  const label = document.getElementById("intervalValue");

  if (slider && label) {
    const val = config.alternate_interval || 3;
    slider.value = val;
    label.innerText = val + " seconds";
    updateTicks(val);
  }
}

function setMode(mode) {
  config.display_mode = mode;
  document.querySelectorAll("[data-mode]").forEach((b) => b.classList.remove("active"));
  document.querySelector(`[data-mode="${mode}"]`)?.classList.add("active");
}

function setUnit(unit) {
  config.temperature_unit = unit;
  const cBtn = document.getElementById("cBtn");
  const fBtn = document.getElementById("fBtn");

  if (cBtn && fBtn) {
    cBtn.classList.remove("active");
    fBtn.classList.remove("active");

    if (unit === "celsius") {
      cBtn.classList.add("active");
    } else {
      fBtn.classList.add("active");
    }
  }
}

function setColorMode(mode) {
  config.color_mode = mode;
  document.querySelectorAll("[data-color-mode]").forEach((b) => b.classList.remove("active"));
  document.querySelector(`[data-color-mode="${mode}"]`)?.classList.add("active");

  const legendBox = document.getElementById("tempLegendBox");
  const paletteBox = document.getElementById("colorPaletteBox");

  if (legendBox && paletteBox) {
    if (mode === "temperature") {
      legendBox.style.opacity = "1";
      paletteBox.style.opacity = "0.4";
      paletteBox.style.pointerEvents = "none";
    } else {
      legendBox.style.opacity = "0.4";
      paletteBox.style.opacity = "1";
      paletteBox.style.pointerEvents = "auto";
    }
  }
}

function setColor(hex) {
  config.color = hex;
  const value = document.getElementById("lcdValue");
  const picker = document.getElementById("colorPicker");
  const hexText = document.getElementById("colorCodeText");

  if (value && config.color_mode !== "temperature") {
    value.style.color = "#" + hex;
    value.style.textShadow = `0 0 20px #${hex}, 0 0 40px #${hex}88`;
  }

  if (picker) picker.value = "#" + hex;
  if (hexText) hexText.textContent = "#" + hex.toUpperCase();
}

const slider = document.getElementById("interval");
if (slider) {
  slider.addEventListener("input", () => {
    const label = document.getElementById("intervalValue");
    const val = parseInt(slider.value);
    if (label) label.innerText = val + " seconds";
    config.alternate_interval = val;
    updateTicks(val);
  });
}

const colorPicker = document.getElementById("colorPicker");
if (colorPicker) {
  colorPicker.addEventListener("input", (e) => {
    const hex = e.target.value.replace("#", "");
    setColor(hex);
  });
}

async function save() {
  const saveBtn = document.querySelector(".btn-save");
  const saveMsg = document.getElementById("saveMsg");

  try {
    if (saveBtn) {
      saveBtn.disabled = true;
      saveBtn.style.opacity = "0.7";
    }

    const res = await fetch("/config", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(config),
    });

    if (res.ok) {
      if (saveMsg) {
        saveMsg.textContent = "✓ Configuration saved & active!";
        saveMsg.style.color = "#10b981";
        setTimeout(() => {
          saveMsg.textContent = "All settings synced with driver.";
          saveMsg.style.color = "var(--text-sub)";
        }, 3000);
      }
    }
  } catch (err) {
    if (saveMsg) {
      saveMsg.textContent = "✗ Failed to save config.";
      saveMsg.style.color = "#f43f5e";
    }
  } finally {
    if (saveBtn) {
      saveBtn.disabled = false;
      saveBtn.style.opacity = "1";
    }
  }
}

window.addEventListener("DOMContentLoaded", init);
