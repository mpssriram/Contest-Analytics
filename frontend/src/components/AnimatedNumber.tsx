import { useEffect, useRef, useState } from "react";

interface AnimatedNumberProps {
  value: number;
  format?: (value: number) => string;
  duration?: number;
}

export function AnimatedNumber({ value, format = (currentValue) => `${Math.round(currentValue)}`, duration = 700 }: AnimatedNumberProps) {
  const [displayValue, setDisplayValue] = useState(0);
  const previousValue = useRef(0);

  useEffect(() => {
    const startTime = performance.now();
    const startValue = previousValue.current;
    const difference = value - startValue;
    let animationFrame = 0;

    const tick = (currentTime: number) => {
      const progress = Math.min((currentTime - startTime) / duration, 1);
      const easedProgress = 1 - Math.pow(1 - progress, 3);
      setDisplayValue(startValue + difference * easedProgress);

      if (progress < 1) {
        animationFrame = requestAnimationFrame(tick);
      } else {
        previousValue.current = value;
      }
    };

    animationFrame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animationFrame);
  }, [duration, value]);

  return <>{format(displayValue)}</>;
}
