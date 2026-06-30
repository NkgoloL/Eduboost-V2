"use client";

import React, { useEffect, useState } from "react";

export function LowDataMode() {
  const [lowDataMode, setLowDataMode] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("lowDataMode");
    if (saved) {
      setLowDataMode(saved === "true");
    }
  }, []);

  const toggleLowDataMode = () => {
    const newValue = !lowDataMode;
    setLowDataMode(newValue);
    localStorage.setItem("lowDataMode", String(newValue));
  };

  return (
    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
      <div className="text-2xl">📶</div>
      <div className="flex-1">
        <div className="font-medium text-gray-900 text-sm">Low Data Mode</div>
        <div className="text-xs text-gray-600">
          {lowDataMode ? "Enabled - reduces data usage" : "Disabled - full experience"}
        </div>
      </div>
      <button
        type="button"
        onClick={toggleLowDataMode}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
          lowDataMode ? "bg-blue-600" : "bg-gray-300"
        }`}
        aria-pressed={lowDataMode}
        aria-label="Toggle low data mode"
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            lowDataMode ? "translate-x-6" : "translate-x-1"
          }`}
        />
      </button>
    </div>
  );
}
