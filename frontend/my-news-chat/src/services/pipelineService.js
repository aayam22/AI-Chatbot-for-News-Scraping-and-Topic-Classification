import axios from "axios";
import { API_CONFIG } from "../constants/config";

const api = axios.create({
  baseURL: API_CONFIG.BACKEND_URL,
  timeout: API_CONFIG.TIMEOUT,
});

const buildAuthHeaders = (token) => ({
  headers: { Authorization: `Bearer ${token}` },
});

export const getPipelineStatus = async (token) => {
  try {
    const response = await api.get(
      API_CONFIG.ENDPOINTS.PIPELINE_STATUS,
      buildAuthHeaders(token)
    );

    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    return {
      success: false,
      error:
        error.response?.data?.detail ||
        error.message ||
        "Failed to fetch pipeline status",
    };
  }
};

export const runPipeline = async (token, mode) => {
  try {
    const response = await api.post(
      API_CONFIG.ENDPOINTS.PIPELINE_RUN,
      { mode },
      buildAuthHeaders(token)
    );

    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    return {
      success: false,
      error:
        error.response?.data?.detail ||
        error.message ||
        "Failed to start pipeline",
    };
  }
};

export default { getPipelineStatus, runPipeline };
