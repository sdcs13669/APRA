import { useSpring } from "framer-motion";
import { useEffect, useState } from "react";

export function useSpringNumber(target: number, config?: { duration?: number }) {
  const spring = useSpring(0, {
    stiffness: 80,
    damping: 20,
    duration: config?.duration ?? 1500,
  });

  const [display, setDisplay] = useState(0);

  useEffect(() => {
    spring.set(target);
  }, [spring, target]);

  useEffect(() => {
    const unsubscribe = spring.on("change", (v) => {
      setDisplay(Math.round(v));
    });
    return unsubscribe;
  }, [spring]);

  return display;
}
