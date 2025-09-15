import React, { useState } from "react";

function InteractiveChatbot() {
  const [skills, setSkills] = useState("");
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const response = await fetch("/api/gemini", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          student_profile: {
            student_id: "user-test",
            interests: [],
            projects: [],
            aptitude_scores: {},
            skills: skills.split(",").map((s) => s.trim()),
          },
          top_k: 3,
        }),
      });
      const data = await response.json();
      setRecommendations(data);
    } catch (error) {
      console.error("Error fetching recommendations:", error);
      setRecommendations({ error: "Failed to fetch recommendations." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-xl font-semibold">Get Career Recommendations</h2>
      <div className="flex flex-col">
        <label htmlFor="skills-input" className="mb-2">
          Enter your skills (comma separated):
        </label>
        <input
          id="skills-input"
          type="text"
          value={skills}
          onChange={(e) => setSkills(e.target.value)}
          className="p-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-black"
          placeholder="e.g., Python, SQL, Data Visualization"
        />
      </div>
      <button
        onClick={handleSubmit}
        disabled={loading}
        className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors disabled:opacity-50"
      >
        {loading ? "Loading..." : "Get Recommendations"}
      </button>
      {recommendations && (
        <div className="bg-slate-100 dark:bg-slate-700 p-4 rounded-md font-mono text-sm">
          <pre>{JSON.stringify(recommendations, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default InteractiveChatbot;
