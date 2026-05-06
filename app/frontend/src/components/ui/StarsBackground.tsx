"use client";

import React, { useMemo } from "react";

type StarStyle = React.CSSProperties & {
  "--d"?: string;
  "--o"?: string;
};

export function StarsBackground() {
  const stars = useMemo(() => {
    const seededValue = (index: number, multiplier: number, offset = 0) => {
      const raw = Math.sin(index * multiplier + offset) * 10000;
      return raw - Math.floor(raw);
    };

    return Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: seededValue(i, 12.9898, 78.233) * 100,
      y: seededValue(i, 39.3468, 11.135) * 100,
      size: seededValue(i, 73.156, 7.77) * 2.5 + 0.5,
      dur: `${(seededValue(i, 31.4159, 3.14) * 3 + 2).toFixed(1)}s`,
      opacity: (seededValue(i, 27.1828, 4.669) * 0.4 + 0.1).toFixed(2),
      delay: `${(seededValue(i, 19.775, 2.22) * 4).toFixed(1)}s`,
    }));
  }, []);

  return (
    <div className="stars-bg">
      {stars.map((s) => (
        <div 
          key={s.id} 
          className="star" 
          style={{
            left: `${s.x}%`, 
            top: `${s.y}%`, 
            width: `${s.size}px`, 
            height: `${s.size}px`, 
            "--d": s.dur, 
            "--o": s.opacity, 
            animationDelay: s.delay 
          } as StarStyle}
        />
      ))}
    </div>
  );
}
