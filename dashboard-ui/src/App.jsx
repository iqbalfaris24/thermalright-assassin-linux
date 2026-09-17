/* eslint-disable react-hooks/exhaustive-deps */
import { useState, useEffect, useRef } from "react";
import { Chart as ChartJS, ArcElement, Legend } from "chart.js";
import { Doughnut } from "react-chartjs-2";
import { Switch } from "@/components/ui/switch";
import { io } from "socket.io-client";
import {
  FiSun,
  FiMoon,
  FiCpu,
  FiHardDrive,
  FiServer,
  FiClock,
  FiActivity,
  FiLayers,
  FiZap,
} from "react-icons/fi";
import { SiAmd, SiLinux } from "react-icons/si";

ChartJS.register(ArcElement, Legend);

function App() {
  const [connected, setConnected] = useState(false);
  const [darkMode, setDarkMode] = useState(true); // Default dark theme
  const [status, setStatus] = useState({
    cpu: {
      current: 0,
      min: 0,
      max: 0,
      temperature: 0,
      percent: 0,
      cores_physical: 6,
      cores_logical: 12,
      load_avg: [0, 0, 0],
      per_core: [],
    },
    gpu: {
      name: "AMD Radeon RX 580 / 570 Series",
      vendor: "AMD",
      usage_percent: 0,
      temperature: 0,
      memory_percent: 0,
      memory_used: 0,
      memory_total: 0,
      power_watts: 0,
      clock_mhz: 0,
      is_available: true,
    },
    memory: {
      percent: 0,
      total: 0,
      used: 0,
      available: 0,
      swap_used: 0,
      swap_total: 0,
      swap_percent: 0,
    },
    storage: {
      percent: 0,
      total: 0,
      used: 0,
      free: 0,
    },
    disks: [],
    system_info: {
      uptime: { days: 0, hours: 0, minutes: 0 },
      os: "Linux",
      os_pretty: "Zorin OS 18.1",
      os_version: "18.1",
      kernel: "7.0.0-31-generic",
      hostname: "Flexy",
    },
  });

  const socketUrl =
    import.meta.env.VITE_WS_URL ||
    (typeof window !== "undefined"
      ? `${window.location.protocol}//${window.location.host}`
      : "http://localhost:5000");

  const socket = io(socketUrl, {
    autoConnect: false,
    transports: ["websocket", "polling"],
  });
  const socketRef = useRef(socket);

  useEffect(() => {
    socketRef.current.connect();

    socketRef.current.on("connect", () => {
      setConnected(true);
    });

    socketRef.current.on("disconnect", () => {
      setConnected(false);
    });

    socketRef.current.on("status_update", (data) => {
      setStatus(data);
    });

    return () => {
      socketRef.current.off("connect");
      socketRef.current.off("disconnect");
      socketRef.current.off("status_update");
    };
  }, [socketRef]);

  // CPU Donut
  const cpuPercent = Number(status.cpu?.percent) || 0;
  const cpuData = {
    datasets: [
      {
        data: [
          Math.min(Math.max(cpuPercent, 0), 100),
          Math.max(100 - Math.min(Math.max(cpuPercent, 0), 100), 0),
        ],
        backgroundColor: [
          cpuPercent > 85 ? "#ef4444" : cpuPercent > 65 ? "#f59e0b" : "#10b981",
          darkMode ? "#1e293b" : "#e2e8f0",
        ],
        borderWidth: 0,
      },
    ],
  };

  // GPU Donut
  const gpuPercent = Number(status.gpu?.usage_percent) || 0;
  const gpuData = {
    datasets: [
      {
        data: [
          Math.min(Math.max(gpuPercent, 0), 100),
          Math.max(100 - Math.min(Math.max(gpuPercent, 0), 100), 0),
        ],
        backgroundColor: [
          gpuPercent > 80 ? "#ef4444" : gpuPercent > 50 ? "#a855f7" : "#8b5cf6",
          darkMode ? "#1e293b" : "#e2e8f0",
        ],
        borderWidth: 0,
      },
    ],
  };

  // Memory Donut
  const memoryPercent = Number(status.memory?.percent) || 0;
  const memoryData = {
    datasets: [
      {
        data: [
          Math.min(Math.max(memoryPercent, 0), 100),
          Math.max(100 - Math.min(Math.max(memoryPercent, 0), 100), 0),
        ],
        backgroundColor: [
          memoryPercent > 85 ? "#ef4444" : "#3b82f6",
          darkMode ? "#1e293b" : "#e2e8f0",
        ],
        borderWidth: 0,
      },
    ],
  };

  const options = {
    cutout: "82%",
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      tooltip: { enabled: false },
      legend: { display: false },
    },
  };

  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem("darkMode", JSON.stringify(newMode));
  };

  useEffect(() => {
    const saved = localStorage.getItem("darkMode");
    if (saved !== null) {
      setDarkMode(JSON.parse(saved));
    }
  }, []);

  return (
    <div className={darkMode ? "dark" : ""}>
      <div className="min-h-screen flex flex-col justify-between bg-slate-100 text-slate-800 dark:bg-[#090e1a] dark:text-slate-100 transition-colors duration-200">
        
        {/* Top Header */}
        <header className="sticky top-0 z-30 bg-white/95 dark:bg-[#0f172a]/95 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-4 md:px-8 py-3.5 shadow-xs">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-indigo-600 text-white shadow-md shadow-indigo-500/20">
                <FiServer className="text-xl" />
              </div>
              <div>
                <h1 className="text-lg font-black tracking-tight text-slate-900 dark:text-white flex items-center gap-2">
                  System Monitor
                  <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 dark:bg-indigo-950/70 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                    {status.system_info?.hostname || "Flexy"}
                  </span>
                </h1>
                <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                  Realtime Hardware & Storage Dashboard
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Dark mode switch */}
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-200/80 dark:bg-slate-800/90 border border-slate-300 dark:border-slate-700">
                <FiSun className={`text-sm ${darkMode ? "text-slate-400" : "text-amber-500 font-bold"}`} />
                <Switch checked={darkMode} onCheckedChange={toggleDarkMode} />
                <FiMoon className={`text-sm ${darkMode ? "text-indigo-400 font-bold" : "text-slate-400"}`} />
              </div>

              {/* Live Connection Pill */}
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-200/80 dark:bg-slate-800/90 border border-slate-300 dark:border-slate-700">
                <span className="relative flex h-2.5 w-2.5">
                  <span
                    className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                      connected ? "bg-emerald-400" : "bg-rose-400"
                    }`}
                  />
                  <span
                    className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
                      connected ? "bg-emerald-500" : "bg-rose-500"
                    }`}
                  />
                </span>
                <span className={`text-xs font-bold font-mono tracking-wide ${connected ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"}`}>
                  {connected ? "LIVE" : "OFFLINE"}
                </span>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl w-full mx-auto px-4 md:px-8 py-6 space-y-6">

          {/* Section 1: Top System Overview Banner */}
          <section className="bg-gradient-to-br from-slate-900 via-slate-850 to-indigo-950 text-white rounded-2xl p-5 md:p-6 shadow-xl border border-slate-700/60 relative overflow-hidden">
            <div className="absolute top-0 right-0 -mt-10 -mr-10 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-5 items-center">
              
              {/* OS / Distro Details */}
              <div className="md:col-span-2 flex items-center gap-4">
                <div className="p-3.5 bg-indigo-500/20 border border-indigo-500/40 rounded-2xl shadow-inner text-indigo-400 shrink-0">
                  <SiLinux className="text-4xl" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold font-mono text-indigo-400 uppercase tracking-widest">
                      Operating System
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded font-bold bg-indigo-500/30 text-indigo-200 border border-indigo-400/30">
                      v{status.system_info?.os_version || "18.1"}
                    </span>
                  </div>
                  <h2 className="text-xl md:text-2xl font-black text-white mt-0.5 tracking-tight">
                    {status.system_info?.os_pretty || "Zorin OS 18.1"}
                  </h2>
                  <p className="text-xs font-mono text-slate-300 mt-1">
                    Kernel: <span className="text-white font-semibold">{status.system_info?.kernel || "Linux 7.0.0-31-generic"}</span>
                  </p>
                </div>
              </div>

              {/* Processor Spec */}
              <div className="border-t md:border-t-0 md:border-l border-slate-700/60 pt-3 md:pt-0 md:pl-5">
                <div className="flex items-center gap-2 text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">
                  <SiAmd className="text-rose-400 text-sm" />
                  <span>Processor Spec</span>
                </div>
                <h3 className="text-sm font-bold text-slate-100 leading-snug">
                  {status.cpu?.processor || "AMD Ryzen 5 3600"}
                </h3>
                <p className="text-xs text-indigo-300 font-mono mt-1 font-medium">
                  {status.cpu?.cores_physical || 6} Cores / {status.cpu?.cores_logical || 12} Threads
                </p>
              </div>

              {/* Live Uptime */}
              <div className="border-t md:border-t-0 md:border-l border-slate-700/60 pt-3 md:pt-0 md:pl-5">
                <div className="flex items-center gap-2 text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">
                  <FiClock className="text-emerald-400 text-sm" />
                  <span>System Uptime</span>
                </div>
                <h3 className="text-lg font-black text-emerald-400 font-mono">
                  {status.system_info?.uptime
                    ? `${status.system_info.uptime.days}d ${status.system_info.uptime.hours}h ${status.system_info.uptime.minutes}m`
                    : "0d 0h 0m"}
                </h3>
                <p className="text-xs text-slate-400 font-medium">Active Session</p>
              </div>

            </div>
          </section>

          {/* Section 2: Core Hardware Metrics (CPU, GPU, Memory) */}
          <section className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            
            {/* CPU Status Card */}
            <div className="bg-white dark:bg-[#111827] rounded-2xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                <div className="flex items-center gap-2">
                  <FiCpu className="text-indigo-500 text-lg" />
                  <h3 className="font-bold text-base text-slate-900 dark:text-slate-100">CPU Status</h3>
                </div>
                <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-600 dark:bg-indigo-950/60 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800">
                  {status.cpu.current} GHz
                </span>
              </div>

              <div className="flex items-center gap-4 my-4 justify-around">
                <div className="relative w-28 h-28 shrink-0">
                  <Doughnut data={cpuData} options={options} />
                  <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                    <span className="text-2xl font-black text-slate-900 dark:text-white">{cpuPercent}%</span>
                    <span className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-semibold">Load</span>
                  </div>
                </div>

                <div className="w-full text-xs space-y-2 font-medium">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-500 dark:text-slate-400">Temperature</span>
                    <span className="font-bold text-amber-500 font-mono text-sm">{status.cpu.temperature}°C</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-500 dark:text-slate-400">Clock Speed</span>
                    <span className="font-bold font-mono text-slate-800 dark:text-slate-200">{status.cpu.current} GHz</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-500 dark:text-slate-400">Load Average</span>
                    <span className="font-bold font-mono text-[11px] text-slate-800 dark:text-slate-200">
                      {status.cpu.load_avg ? status.cpu.load_avg.join(", ") : "-"}
                    </span>
                  </div>
                </div>
              </div>

              {/* 12-Core Multi-Thread Visualizer */}
              {status.cpu.per_core && status.cpu.per_core.length > 0 && (
                <div className="pt-3 border-t border-slate-100 dark:border-slate-800">
                  <div className="flex justify-between items-center mb-1.5">
                    <span className="text-[10px] text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider">
                      Thread Activity ({status.cpu.per_core.length} Cores)
                    </span>
                  </div>
                  <div className="grid grid-cols-6 gap-1">
                    {status.cpu.per_core.map((load, idx) => (
                      <div key={idx} className="flex flex-col items-center" title={`Core ${idx + 1}: ${load}%`}>
                        <div className="w-full bg-slate-100 dark:bg-slate-800 h-7 rounded-sm overflow-hidden flex flex-col justify-end p-0.5 border border-slate-200/50 dark:border-slate-700/50">
                          <div
                            className={`w-full rounded-xs transition-all duration-300 ${
                              load > 80 ? "bg-rose-500" : load > 50 ? "bg-amber-500" : "bg-emerald-500"
                            }`}
                            style={{ height: `${Math.max(load, 8)}%` }}
                          />
                        </div>
                        <span className="text-[8px] font-mono text-slate-500 dark:text-slate-400 mt-0.5 font-bold">C{idx + 1}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* GPU Status Card */}
            <div className="bg-white dark:bg-[#111827] rounded-2xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                <div className="flex items-center gap-2">
                  <FiZap className="text-purple-500 text-lg" />
                  <h3 className="font-bold text-base text-slate-900 dark:text-slate-100">GPU Status</h3>
                </div>
                <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-purple-50 text-purple-600 dark:bg-purple-950/60 dark:text-purple-400 border border-purple-200 dark:border-purple-800">
                  {status.gpu?.vendor || "AMD"}
                </span>
              </div>

              <div className="flex items-center gap-4 my-4 justify-around">
                <div className="relative w-28 h-28 shrink-0">
                  <Doughnut data={gpuData} options={options} />
                  <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                    <span className="text-2xl font-black text-slate-900 dark:text-white">{gpuPercent}%</span>
                    <span className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-semibold">GPU Load</span>
                  </div>
                </div>

                <div className="w-full text-xs space-y-2 font-medium">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-500 dark:text-slate-400">Model</span>
                    <span className="font-bold text-slate-800 dark:text-slate-200 truncate max-w-[130px]" title={status.gpu?.name}>
                      {status.gpu?.name ? status.gpu.name.replace("Advanced Micro Devices, Inc. [AMD/ATI] ", "") : "AMD Radeon RX 580"}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-500 dark:text-slate-400">Temperature</span>
                    <span className="font-bold text-purple-600 dark:text-purple-400 font-mono text-sm">
                      {status.gpu?.temperature || "0"}°C
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-500 dark:text-slate-400">Engine Clock</span>
                    <span className="font-bold font-mono text-slate-800 dark:text-slate-200">
                      {status.gpu?.clock_mhz ? `${status.gpu.clock_mhz} MHz` : "Dynamic"}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-500 dark:text-slate-400">Power Draw</span>
                    <span className="font-bold font-mono text-amber-500">
                      {status.gpu?.power_watts ? `${status.gpu.power_watts} W` : "-"}
                    </span>
                  </div>
                </div>
              </div>

              {/* VRAM / Memory Busy Progress */}
              <div className="pt-3 border-t border-slate-100 dark:border-slate-800 text-xs">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-[10px] text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider">
                    VRAM Controller Load
                  </span>
                  <span className="font-mono text-[11px] font-bold text-purple-600 dark:text-purple-400">
                    {status.gpu?.memory_percent || 0}%
                  </span>
                </div>
                <div className="w-full bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden border border-slate-200/50 dark:border-slate-700/50">
                  <div
                    className="h-full bg-purple-500 transition-all duration-300"
                    style={{ width: `${Math.min(status.gpu?.memory_percent || 0, 100)}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Memory & Swap Card */}
            <div className="bg-white dark:bg-[#111827] rounded-2xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                <div className="flex items-center gap-2">
                  <FiLayers className="text-blue-500 text-lg" />
                  <h3 className="font-bold text-base text-slate-900 dark:text-slate-100">Memory Status</h3>
                </div>
                <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-600 dark:bg-blue-950/60 dark:text-blue-400 border border-blue-200 dark:border-blue-800">
                  {status.memory.total} GB Total
                </span>
              </div>

              <div className="flex items-center gap-4 my-4 justify-around">
                <div className="relative w-28 h-28 shrink-0">
                  <Doughnut data={memoryData} options={options} />
                  <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                    <span className="text-2xl font-black text-slate-900 dark:text-white">{memoryPercent}%</span>
                    <span className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-semibold">RAM Used</span>
                  </div>
                </div>

                <div className="w-full text-xs space-y-2 font-medium">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-500 dark:text-slate-400">Used RAM</span>
                    <span className="font-bold font-mono text-slate-800 dark:text-slate-200">{status.memory.used} GB</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-500 dark:text-slate-400">Available</span>
                    <span className="font-bold text-emerald-600 dark:text-emerald-400 font-mono">
                      {status.memory.available || "-"} GB
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-500 dark:text-slate-400">Total Installed</span>
                    <span className="font-bold font-mono text-slate-800 dark:text-slate-200">{status.memory.total} GB</span>
                  </div>
                </div>
              </div>

              {/* Swap Memory Details */}
              <div className="pt-3 border-t border-slate-100 dark:border-slate-800 text-xs">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-[10px] text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider">
                    Swap Partition
                  </span>
                  <span className="font-mono text-[11px] font-bold text-slate-700 dark:text-slate-300">
                    {status.memory.swap_used || "0"} / {status.memory.swap_total || "0"} GB ({status.memory.swap_percent || 0}%)
                  </span>
                </div>
                <div className="w-full bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden border border-slate-200/50 dark:border-slate-700/50">
                  <div
                    className="h-full bg-blue-500 transition-all duration-300"
                    style={{ width: `${Math.min(status.memory.swap_percent || 0, 100)}%` }}
                  />
                </div>
              </div>
            </div>

          </section>

          {/* Section 3: All Mounted Storages Autodetected */}
          <section className="bg-white dark:bg-[#111827] rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2">
                <FiHardDrive className="text-orange-500 text-xl" />
                <div>
                  <h3 className="font-bold text-lg text-slate-900 dark:text-slate-100">
                    Storage Drives & Mounted Partitions
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Autodetected NVMe SSD, SATA, & External Volumes
                  </p>
                </div>
              </div>
              <span className="text-xs font-mono font-bold px-2.5 py-1 rounded-full bg-orange-50 text-orange-600 dark:bg-orange-950/60 dark:text-orange-400 border border-orange-200 dark:border-orange-800">
                {status.disks?.length || 1} Volumes Active
              </span>
            </div>

            {/* Grid of Storage Partitions (Responsive 1/2/3 Col with Dark Mode Native Cards) */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {(status.disks && status.disks.length > 0 ? status.disks : [
                {
                  device: "/dev/nvme0n1p6",
                  mount: "/",
                  label: "System Root (/)",
                  fstype: "ext4",
                  total: status.storage.total,
                  used: status.storage.used,
                  free: status.storage.free,
                  percent: status.storage.percent,
                }
              ]).map((disk, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-xl bg-slate-50 dark:bg-[#1a2333] border border-slate-200 dark:border-slate-700/60 hover:border-orange-500/50 dark:hover:border-orange-500/60 transition-all duration-200 flex flex-col justify-between shadow-xs"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2.5">
                        <div className="p-2 rounded-lg bg-orange-500/10 text-orange-500 dark:bg-orange-500/20">
                          <FiHardDrive className="text-base" />
                        </div>
                        <div>
                          <h4 className="font-bold text-sm text-slate-900 dark:text-white">
                            {disk.label}
                          </h4>
                          <span className="text-[10px] font-mono text-slate-500 dark:text-slate-400">
                            {disk.device} ({disk.fstype})
                          </span>
                        </div>
                      </div>
                      <span className="text-sm font-black font-mono text-orange-600 dark:text-orange-400">
                        {disk.percent}%
                      </span>
                    </div>

                    <div className="w-full bg-slate-200 dark:bg-slate-700/70 h-2.5 rounded-full overflow-hidden my-3">
                      <div
                        className={`h-full transition-all duration-300 ${
                          disk.percent > 90
                            ? "bg-rose-500"
                            : disk.percent > 75
                            ? "bg-amber-500"
                            : "bg-orange-500"
                        }`}
                        style={{ width: `${Math.min(disk.percent, 100)}%` }}
                      />
                    </div>
                  </div>

                  <div className="flex justify-between items-center text-xs font-mono pt-2.5 border-t border-slate-200 dark:border-slate-700/60 text-slate-600 dark:text-slate-300">
                    <span>Used: <strong className="text-slate-900 dark:text-white font-bold">{disk.used} GB</strong></span>
                    <span>Free: <strong className="text-emerald-600 dark:text-emerald-400 font-bold">{disk.free} GB</strong></span>
                    <span>Total: <strong className="text-slate-900 dark:text-white font-bold">{disk.total} GB</strong></span>
                  </div>
                </div>
              ))}
            </div>
          </section>

        </main>

        {/* Footer */}
        <footer className="mt-8 py-5 border-t border-slate-200 dark:border-slate-800/80 text-center text-xs text-slate-500 dark:text-slate-400">
          <p>
            WebSocket System Information Monitor • Made with ❤️ by{" "}
            <a
              href="https://github.com/iqbalfaris24/WebSocketSystemInformation"
              target="_blank"
              rel="noopener noreferrer"
              className="text-indigo-600 dark:text-indigo-400 hover:underline font-semibold"
            >
              Iqbal Faris
            </a>
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;
