let config = {};

async function init() {
  const res = await fetch("/config");
  config = await res.json();

  applyConfig();
}

function applyConfig() {
  setMode(config.display_mode);
  setUnit(config.temperature_unit);
  setColorMode(config.color_mode || "static");
  setColor(config.color || "ff0000");
  setColorMode(config.color_mode || "static");
  const slider = document.getElementById("interval");
  const label = document.getElementById("intervalValue");

  slider.value = config.alternate_interval;
  label.innerText = config.alternate_interval + "s";
}

function setMode(mode) {
  config.display_mode = mode;

  document
    .querySelectorAll("[data-mode]")
    .forEach((b) => b.classList.remove("active"));

  document.querySelector(`[data-mode="${mode}"]`)?.classList.add("active");
}

function setUnit(unit) {
  config.temperature_unit = unit;

  document.getElementById("cBtn").classList.remove("active");
  document.getElementById("fBtn").classList.remove("active");

  if (unit === "celsius") {
    document.getElementById("cBtn").classList.add("active");
  } else {
    document.getElementById("fBtn").classList.add("active");
  }
}

function setColorMode(mode) {
  config.color_mode = mode;

  document
    .querySelectorAll("[data-color-mode]")
    .forEach((b) => b.classList.remove("active"));

  document
    .querySelector(`[data-color-mode="${mode}"]`)
    ?.classList.add("active");
}

function setColor(hex) {
  config.color = hex;

  const value = document.getElementById("lcdValue");

  value.style.color = "#" + hex;
  value.style.textShadow = "0 0 10px #" + hex;

  document.getElementById("colorPicker").value = "#" + hex;
}

const slider = document.getElementById("interval");

if (slider) {
  slider.addEventListener("input", () => {
    const label = document.getElementById("intervalValue");

    label.innerText = slider.value + "s";

    config.alternate_interval = parseInt(slider.value);
  });
}

async function save() {
  await fetch("/config", {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify(config),
  });

  alert("Saved");
}

window.addEventListener("DOMContentLoaded", init);
