import { useState, useEffect } from "react";

export default function LoadingDots({ text = "Generating" }) {
  const [dots, setDots] = useState(".");

  useEffect(() => {
    const interval = setInterval(() => {
      setDots((prev) => {
        if (prev === ".") return "..";
        if (prev === "..") return "...";
        if (prev === "...") return "....";
        return ".";
      });
    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <span className="inline-flex items-center gap-2 text-sm font-semibold text-current">
      <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-current" />
      <span>
        {text}
        {dots}
      </span>
    </span>
  );
}
