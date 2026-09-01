import axios from 'axios';
import type { Personnel, AnalysisResult, PersonnelHistory, RosterSummary, SampleScenario } from '../types';

// Use direct backend URL (with fallback to relative /api proxy)
const API_BASE = 'http://localhost:8000/api';

export const api = {
  // Personnel
  async getPersonnel(): Promise<Personnel[]> {
    const res = await axios.get(`${API_BASE}/personnel`);
    return res.data;
  },

  async createPersonnel(data: { personnel_id: string; name?: string; unit?: string; force_type?: string; age?: number }): Promise<Personnel> {
    const res = await axios.post(`${API_BASE}/personnel`, data);
    return res.data;
  },

  async getPersonnelHistory(id: number): Promise<PersonnelHistory> {
    const res = await axios.get(`${API_BASE}/personnel/${id}/history`);
    return res.data;
  },

  // Upload & Pipeline
  async uploadSensorFile(file: File, personnelCode: string, scenarioTag?: string): Promise<AnalysisResult> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('personnel_code', personnelCode);
    if (scenarioTag) {
      formData.append('scenario_tag', scenarioTag);
    }
    const res = await axios.post(`${API_BASE}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },

  // Samples
  async getSampleScenarios(): Promise<SampleScenario[]> {
    const res = await axios.get(`${API_BASE}/samples`);
    return res.data;
  },

  async runSampleScenario(scenarioType: string): Promise<AnalysisResult> {
    const res = await axios.post(`${API_BASE}/samples/run/${scenarioType}`);
    return res.data;
  },

  // Analysis Retrieval
  async getAnalysis(id: number): Promise<AnalysisResult> {
    const res = await axios.get(`${API_BASE}/analysis/${id}`);
    return res.data;
  },

  // Commander Roster
  async getRoster(): Promise<RosterSummary> {
    const res = await axios.get(`${API_BASE}/roster`);
    return res.data;
  }
};
