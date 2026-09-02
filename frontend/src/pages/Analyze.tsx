import { useState } from "react";
import { motion } from "framer-motion";
import { AlertTriangle, Loader2, ScanFace, ServerCrash } from "lucide-react";
import { UploadBox } from "../components/UploadBox";
import { FaceBoundingBoxes } from "../components/FaceBoundingBoxes";
import { ResultCard } from "../components/ResultCard";
import { FaceCard } from "../components/FaceCard";
import { ApiError, predictEmotion } from "../services/api";
import type { AppState, PredictionResponse } from "../types";

export function Analyze() {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [state, setState] = useState<AppState>("idle");
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [selectedFaceId, setSelectedFaceId] = useState<number | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [errorKind, setErrorKind] = useState<"backend" | "generic">("generic");

  const handleFileSelected = async (selected: File) => {
    setPreviewUrl(URL.createObjectURL(selected));
    setResult(null);
    setErrorMessage(null);
    setState("analyzing");

    try {
      const response = await predictEmotion(selected);
      setResult(response);
      setSelectedFaceId(response.predictions[0]?.face_id ?? null);
      setState("success");
    } catch (err) {
      setState("error");
      if (err instanceof ApiError) {
        setErrorKind(err.status === 0 || err.status >= 500 ? "backend" : "generic");
        setErrorMessage(err.message);
      } else if (err instanceof TypeError) {
        // fetch() throws a TypeError on network failure (backend down/CORS)
        setErrorKind("backend");
        setErrorMessage("AI service is currently unavailable. Please check that the backend server is running.");
      } else {
        setErrorMessage("Something went wrong while analyzing this image.");
      }
    }
  };

  const handleClear = () => {
    setPreviewUrl(null);
    setResult(null);
    setErrorMessage(null);
    setSelectedFaceId(null);
    setState("idle");
  };

  const selectedPrediction = result?.predictions.find((p) => p.face_id === selectedFaceId) ?? null;

  return (
    <div className="mx-auto max-w-6xl px-5 py-14">
      <div className="mb-10">
        <h1 className="font-display text-3xl font-semibold">Emotion Analysis</h1>
        <p className="mt-2 max-w-xl text-sm text-[var(--text-muted)]">
          Upload a photo with one or more clearly visible faces. Each detected face
          is analyzed independently and shown as a <em>predicted facial expression</em>,
          not a certain reading of how someone actually feels.
        </p>
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        <div>
          {previewUrl && result && result.predictions.length > 0 ? (
            <FaceBoundingBoxes
              imageUrl={previewUrl}
              predictions={result.predictions}
              selectedFaceId={selectedFaceId}
              onSelectFace={setSelectedFaceId}
            />
          ) : (
            <UploadBox
              onFileSelected={handleFileSelected}
              previewUrl={previewUrl}
              onClear={handleClear}
              disabled={state === "analyzing"}
            />
          )}
          {previewUrl && (
            <button
              onClick={handleClear}
              className="mt-3 text-xs text-[var(--text-muted)] underline underline-offset-2 hover:text-[var(--text)]"
            >
              Upload a different image
            </button>
          )}
        </div>

        <div>
          {state === "idle" && (
            <div className="flex h-full min-h-[280px] flex-col items-center justify-center rounded-2xl border border-dashed border-[var(--border)] p-8 text-center text-sm text-[var(--text-muted)]">
              <ScanFace size={28} className="mb-3 text-[var(--text-muted)]" />
              Results will appear here once you upload an image.
            </div>
          )}

          {state === "analyzing" && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex h-full min-h-[280px] flex-col items-center justify-center rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-8 text-center"
            >
              <Loader2 size={28} className="mb-3 animate-spin text-signal-violet" />
              <p className="font-display text-base font-semibold">Scanning face and expression…</p>
              <p className="mt-1 text-sm text-[var(--text-muted)]">This usually takes a couple of seconds.</p>
            </motion.div>
          )}

          {state === "error" && (
            <div className="flex h-full min-h-[280px] flex-col items-center justify-center rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-8 text-center">
              {errorKind === "backend" ? (
                <ServerCrash size={28} className="mb-3 text-signal-coral" />
              ) : (
                <AlertTriangle size={28} className="mb-3 text-signal-coral" />
              )}
              <p className="font-display text-base font-semibold text-[var(--text)]">
                {errorKind === "backend" ? "AI service is unavailable" : "Couldn't analyze this image"}
              </p>
              <p className="mt-1 max-w-xs text-sm text-[var(--text-muted)]">{errorMessage}</p>
            </div>
          )}

          {state === "success" && result && result.faces_detected === 0 && (
            <div className="flex h-full min-h-[280px] flex-col items-center justify-center rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-8 text-center">
              <ScanFace size={28} className="mb-3 text-signal-amber" />
              <p className="font-display text-base font-semibold">No human face detected</p>
              <p className="mt-1 max-w-xs text-sm text-[var(--text-muted)]">
                Please upload an image containing a clearly visible, front-facing human face.
              </p>
            </div>
          )}

          {state === "success" && result && result.faces_detected > 0 && (
            <div className="space-y-5">
              {result.faces_detected > 1 && (
                <div>
                  <p className="mb-3 text-sm text-[var(--text-muted)]">
                    Detected faces: <span className="text-[var(--text)]">{result.faces_detected}</span>
                  </p>
                  <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                    {result.predictions.map((p) => (
                      <FaceCard
                        key={p.face_id}
                        prediction={p}
                        isSelected={p.face_id === selectedFaceId}
                        onSelect={() => setSelectedFaceId(p.face_id)}
                      />
                    ))}
                  </div>
                </div>
              )}
              {selectedPrediction && (
                <ResultCard
                  prediction={selectedPrediction}
                  label={result.faces_detected > 1 ? `Face ${selectedPrediction.face_id}` : "Primary expression"}
                />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
