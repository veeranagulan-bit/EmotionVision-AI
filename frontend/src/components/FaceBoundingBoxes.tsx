import { useRef, useState } from "react";
import type { FacePrediction } from "../types";

interface FaceBoundingBoxesProps {
  imageUrl: string;
  predictions: FacePrediction[];
  selectedFaceId: number | null;
  onSelectFace: (faceId: number) => void;
}

export function FaceBoundingBoxes({
  imageUrl,
  predictions,
  selectedFaceId,
  onSelectFace,
}: FaceBoundingBoxesProps) {
  const imgRef = useRef<HTMLImageElement>(null);
  const [naturalSize, setNaturalSize] = useState<{ w: number; h: number } | null>(null);

  return (
    <div className="relative overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--surface)]">
      <img
        ref={imgRef}
        src={imageUrl}
        alt="Analyzed"
        className="w-full object-contain"
        onLoad={(e) => {
          const img = e.currentTarget;
          setNaturalSize({ w: img.naturalWidth, h: img.naturalHeight });
        }}
      />
      {naturalSize &&
        predictions.map((pred) => {
          const isSelected = pred.face_id === selectedFaceId;
          const left = (pred.box.x / naturalSize.w) * 100;
          const top = (pred.box.y / naturalSize.h) * 100;
          const width = (pred.box.w / naturalSize.w) * 100;
          const height = (pred.box.h / naturalSize.h) * 100;
          return (
            <button
              key={pred.face_id}
              onClick={() => onSelectFace(pred.face_id)}
              style={{ left: `${left}%`, top: `${top}%`, width: `${width}%`, height: `${height}%` }}
              className={`absolute rounded-md border-2 transition-colors ${
                isSelected ? "border-signal-violet" : "border-signal-teal/70 hover:border-signal-teal"
              }`}
            >
              <span
                className={`absolute -top-6 left-0 rounded px-1.5 py-0.5 text-[10px] font-medium text-white ${
                  isSelected ? "bg-signal-violet" : "bg-signal-teal"
                }`}
              >
                Face {pred.face_id}
              </span>
            </button>
          );
        })}
    </div>
  );
}
