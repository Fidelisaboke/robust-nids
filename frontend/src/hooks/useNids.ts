import { useMutation, useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/apiClient";

export interface NetworkFlowFeatures {
  [key: string]: number | string;
}

export interface BinaryPrediction {
  label: string;
  confidence: number;
  is_malicious: boolean;
}

export interface MulticlassPrediction {
  label: string;
  confidence: number;
  probabilities: Record<string, number>;
}

export interface AnomalyDetection {
  is_anomaly: boolean;
  anomaly_score: number;
  threshold: number;
}

export interface UnifiedPredictionResponse {
  id?: string;
  src_ip: string;
  dst_ip: string;
  timestamp: string;
  threat_level: "Low" | "Medium" | "High" | "Critical";
  binary: BinaryPrediction;
  multiclass: MulticlassPrediction;
  anomaly: AnomalyDetection;
}

export interface FeatureContribution {
  feature: string;
  value: number;
  shap_value: number;
}

export interface ExplanationResponse {
  status: string;
  base_value: number;
  contributions: FeatureContribution[];
}

const NIDS_BASE = "/api/v1/nids/";

/**
 * Hook for full NIDS prediction (Binary + Multiclass + Anomaly)
 */
export const useNidsPrediction = () => {
  return useMutation<UnifiedPredictionResponse, Error, NetworkFlowFeatures>({
    mutationFn: async (features: NetworkFlowFeatures) => {
      const response = await apiClient.post<UnifiedPredictionResponse>(
        `${NIDS_BASE}predict/full`,
        { features },
      );
      return response.data;
    },
  });
};

/**
 * Hook for SHAP explanation of binary classification decision
 */
export const useNidsExplanation = () => {
  return useMutation<ExplanationResponse, Error, NetworkFlowFeatures>({
    mutationFn: async (features: NetworkFlowFeatures) => {
      const response = await apiClient.post<ExplanationResponse>(
        `${NIDS_BASE}explain/binary`,
        { features },
      );
      return response.data;
    },
  });
};

/**
 * Hook for live polling of latest threats
 */
export const useLiveThreats = () => {
  return useQuery({
    queryKey: ["live-threats"],
    queryFn: async () => {
      const res = await apiClient.get<UnifiedPredictionResponse[]>(
        `${NIDS_BASE}live-events`,
      );
      return res.data;
    },
    refetchInterval: 2000, // Poll every 2 seconds
  });
};

/**
 * Combined hook that provides both prediction and explanation
 * with coordinated state management
 */
export const useNidsAnalysis = () => {
  const prediction = useNidsPrediction();
  const explanation = useNidsExplanation();

  const analyzeThreat = async (features: NetworkFlowFeatures) => {
    try {
      const predictionResult = await prediction.mutateAsync(features);
      return { prediction: predictionResult };
    } catch (error) {
      throw error;
    }
  };

  const explainPrediction = async (features: NetworkFlowFeatures) => {
    try {
      const explanationResult = await explanation.mutateAsync(features);
      return { explanation: explanationResult };
    } catch (error) {
      throw error;
    }
  };

  return {
    analyzeThreat,
    explainPrediction,
    isPredicting: prediction.isPending,
    isExplaining: explanation.isPending,
    predictionError: prediction.error,
    explanationError: explanation.error,
    predictionData: prediction.data,
    explanationData: explanation.data,
    resetPrediction: prediction.reset,
    resetExplanation: explanation.reset,
  };
};
