let config = {}

async function init(){

    const res = await fetch("/config")
    config = await res.json()

    applyConfig()

}



function setMode(mode){
    config.display_mode = mode

    document.querySelectorAll("[data-mode]").forEach(b=>b.classList.remove("active"))
    document.querySelector(`[data-mode="${mode}"]`).classList.add("active")
}

function setUnit(unit){
    config.temperature_unit = unit

    document.getElementById("cBtn").classList.remove("active")
    document.getElementById("fBtn").classList.remove("active")

    if(unit === "celsius"){
        document.getElementById("cBtn").classList.add("active")
    } else {
        document.getElementById("fBtn").classList.add("active")
    }
}

function setActive(group, value){
    document.querySelectorAll(group).forEach(btn=>{
        btn.classList.remove("active")
    })

    document.querySelector(`[data-${group}="${value}"]`)?.classList.add("active")
}

function applyConfig(){

    // COLOR
    setColor(config.color)

    // MODE
    setMode(config.display_mode)

    // UNIT
    setUnit(config.temperature_unit)

    // INTERVAL
    const slider = document.getElementById("interval")
    const label = document.getElementById("intervalValue")
    document.getElementById("colorPicker").value = "#" + config.color

    slider.value = config.alternate_interval
    label.innerText = config.alternate_interval + "s"

}

const slider = document.getElementById("interval")
const label = document.getElementById("intervalValue")
const picker = document.getElementById("colorPicker")

picker.addEventListener("input", (e)=>{

    let hex = e.target.value  // "#ff0000"

    hex = hex.replace("#","") // "ff0000"

    setColor(hex)

})

slider.addEventListener("input", ()=>{
    label.innerText = slider.value + "s"
    config.alternate_interval = parseInt(slider.value)
})

function setColor(hex){

    // simpan ke config TANPA #
    config.color = hex.toLowerCase()

    const el = document.querySelector(".value")

    // tampilkan pakai #
    el.style.color = "#" + hex

    el.style.textShadow = `
        0 0 5px #${hex},
        0 0 10px #${hex},
        0 0 20px #${hex}
    `
}

async function save(){
    config.alternate_interval = parseInt(
        document.getElementById("interval").value
    )

    await fetch("/config",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify(config)
    })

    alert("Saved")
}

init()