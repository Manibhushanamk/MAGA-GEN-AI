"use client";

import { useState } from "react";
import axios from "axios";

export default function Home() {
  const [form, setForm] = useState({
    area: 1000,
    floors: 2,
    deadline: 120,
    budget: 5000000,
    workforce_cap: 50,
    provider: "gemini",
    api_key: "",
  });

  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await axios.post(
        "http://localhost:8000/analyze_project",
        form,
      );
      setResult(response.data);
    } catch (err: any) {
      setError(
        "API Error. Check backend. " +
          (err.response?.data?.detail || err.message),
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 p-8 font-sans">
      <div className="max-w-5xl mx-auto space-y-6">
        <h1 className="text-4xl font-extrabold text-center text-slate-800 tracking-tight">
          Constructive Builder
        </h1>
        <p className="text-center text-slate-500">
          Autonomous Construction Project Estimation & Scheduling
        </p>

        <div className="bg-white p-6 rounded-xl shadow-lg border border-slate-200">
          <h2 className="text-lg font-semibold mb-4 text-slate-700">
            Project Parameters
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.keys(form).map((key) => (
              <div key={key} className="flex flex-col">
                <label className="text-sm font-medium text-slate-600 mb-1 capitalize">
                  {key.replace("_", " ")}
                </label>
                <input
                  type={
                    key === "api_key"
                      ? "password"
                      : key === "provider"
                        ? "text"
                        : "number"
                  }
                  placeholder={key === "provider" ? "gemini or groq" : ""}
                  value={(form as any)[key]}
                  onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                  className="border border-slate-300 p-2 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none transition"
                />
              </div>
            ))}
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading}
            className={`mt-6 w-full ${loading ? "bg-blue-400" : "bg-blue-600 hover:bg-blue-700"} text-white font-bold py-3 px-4 rounded transition duration-200 ease-in-out shadow-md`}
          >
            {loading ? "Analyzing Project..." : "Run Analysis"}
          </button>

          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded mt-4 border border-red-200 text-sm">
              Error: {error}
            </div>
          )}
        </div>

        {result && (
          <div className="bg-white p-8 rounded-xl shadow-lg border border-slate-200 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-center border-b pb-4">
              <h2 className="text-2xl font-bold text-slate-800">
                Analysis Results
              </h2>
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${result.feasibility_status === "Feasible" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}
              >
                {result.feasibility_status}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
                <p className="text-sm text-slate-500">Total Duration</p>
                <p className="text-2xl font-bold text-slate-800">
                  {result.total_duration} days
                </p>
              </div>
              <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
                <p className="text-sm text-slate-500">Total Cost</p>
                <p className="text-2xl font-bold text-slate-800">
                  {typeof result.total_cost === "object"
                    ? result.total_cost.total_cost?.toLocaleString()
                    : result.total_cost?.toLocaleString()}
                </p>
              </div>
              <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
                <p className="text-sm text-slate-500">Risk Profile (P80)</p>
                <p className="text-2xl font-bold text-slate-800">
                  {result.simulation_results?.p80_duration?.toFixed(0)} days
                </p>
              </div>
            </div>

            {typeof result.total_cost === "object" && (
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                <h3 className="font-semibold text-blue-800 mb-2">
                  Cost Breakdown
                </h3>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-blue-600 block">Labor</span>
                    <span className="font-medium">
                      {result.total_cost.labor_cost?.toLocaleString()}
                    </span>
                  </div>
                  <div>
                    <span className="text-blue-600 block">Material</span>
                    <span className="font-medium">
                      {result.total_cost.material_cost?.toLocaleString()}
                    </span>
                  </div>
                  <div>
                    <span className="text-blue-600 block">Overhead</span>
                    <span className="font-medium">
                      {result.total_cost.overhead_cost?.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-slate-700 mb-2">
                  Critical Path Tasks
                </h3>
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-100 max-h-60 overflow-y-auto">
                  <ul className="list-disc ml-4 space-y-1 text-sm text-slate-600">
                    {result.critical_path_tasks?.map((t: string) => (
                      <li key={t}>{t}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div>
                <h3 className="font-semibold text-slate-700 mb-2">
                  Executive Summary
                </h3>
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-100 max-h-60 overflow-y-auto prose prose-sm">
                  <p className="whitespace-pre-wrap text-slate-600">
                    {result.executive_summary}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
