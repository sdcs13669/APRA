import { useSpring } from "framer-motion";
import { useEffect, useState } from "react";

export function useSpringNumber(target: number, config?: { duration?: number; decimals?: number }) {
  const spring = useSpring(0, {
    stiffness: 80,
    damping: 20,
    duration: config?.duration ?? 1500,
  });

  const [display, setDisplay] = useState<number>(0);
  const decimals = config?.decimals ?? 0;

  useEffect(() => {
    spring.set(target);
  }, [spring, target]);

  useEffect(() => {
    const unsubscribe = spring.on("change", (v) => {
      setDisplay(Number(v.toFixed(decimals)));
    });
    return unsubscribe;
  }, [spring, decimals]);

  return display;
}
