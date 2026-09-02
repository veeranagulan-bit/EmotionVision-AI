export interface BoundingBox {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface FacePrediction {
  face_id: number;
  box: BoundingBox;
  emotion: string;
  confidence: number; // 0-1
  is_uncertain: boolean;
  probabilities: Record<string, number>;
}

export interface PredictionResponse {
  faces_detected: number;
  predictions: FacePrediction[];
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  classes: string[];
  version: string;
}

export interface PerClassMetric {
  precision: number;
  recall: number;
  f1_score: number;
  support: number;
}

export interface ModelMetrics {
  backbone: string;
  num_classes: number;
  classes: string[];
  final_train_accuracy?: number;
  final_val_accuracy?: number;
  test_accuracy?: number;
  test_loss?: number;
  test_auc?: number;
  overall_test_accuracy?: number;
  per_class?: Record<string, PerClassMetric>;
  macro_avg?: { precision: number; recall: number; "f1-score": number; support: number };
  weighted_avg?: { precision: number; recall: number; "f1-score": number; support: number };
  model_loaded: boolean;
}

export type AppState = "idle" | "uploading" | "analyzing" | "success" | "error";

export const EMOTION_EMOJI: Record<string, string> = {
  Happy: "😄",
  Sad: "😢",
  Angry: "😠",
  Fear: "😨",
  Surprise: "😲",
  Disgust: "🤢",
  Neutral: "😐",
};
