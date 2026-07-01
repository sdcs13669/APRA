import { useRef } from "react";
import { useParticleCanvas } from "../../hooks/useParticleCanvas";

export default function ParticleBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  useParticleCanvas(canvasRef);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none"
      style={{ zIndex: 0 }}
    />
  );
}
