import { useState, useEffect } from "react"
import { getSummary } from "../api/client"

export default function Summary({ sessionId }) {
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    fetchSummary()
  }, [])

  const fetchSummary = async () => {
    try {
      const res = await getSummary(sessionId)
      setSummary(res.data)
    } catch (err) {
      setError("Failed to load summary.")
    } finally {
      setLoading(false)
    }
  }

  if (loading) return (
    <div className="card">
      <div className="loading-box">
        <span className="spinner" /> Analyzing your interview...
      </div>
    </div>
  )

  if (error) return (
    <div className="card">
      <p className="error">{error}</p>
    </div>
  )

  const scoreColor = (score) => {
    if (score >= 8) return "#16a34a"
    if (score >= 6) return "#ca8a04"
    if (score >= 4) return "#ea580c"
    return "#dc2626"
  }

  const ratingEmoji = {
    "Excellent": "🏆",
    "Good": "👍",
    "Average": "📈",
    "Needs Improvement": "💪"
  }

  return (
    <div className="card">
      {/* Header */}
      <div className="summary-header">
        <h2>Interview Complete</h2>
        <span className="role-tag">{summary.role}</span>
      </div>

      {/* Overall score */}
      <div className="score-banner">
        <div className="score-circle" style={{ borderColor: scoreColor(summary.average_score) }}>
          <span style={{ color: scoreColor(summary.average_score) }}>
            {summary.average_score}
          </span>
          <small>/10</small>
        </div>
        <div className="score-info">
          <h3>
            {ratingEmoji[summary.overall_rating]} {summary.overall_rating}
          </h3>
          <p>{summary.answered} of {summary.total_questions} questions answered</p>
        </div>
      </div>

      {/* Q&A Breakdown */}
      <h3 className="breakdown-title">Question Breakdown</h3>

      {summary.breakdown ? (
        summary.breakdown.map((item, i) => (
          <div key={i} className="qa-card">
            <div className="qa-header">
              <span className="q-number">Q{i + 1}</span>
              {item.score !== undefined && (
                <span
                  className="q-score"
                  style={{ color: scoreColor(item.score) }}
                >
                  {item.score}/10 — {item.quality}
                </span>
              )}
            </div>

            <p className="q-text"><strong>Q:</strong> {item.question}</p>
            <p className="a-text"><strong>A:</strong> {item.answer}</p>

            {item.feedback && (
              <div className="feedback-box">
                💬 {item.feedback}
              </div>
            )}

            {item.missing_concept && item.missing_concept !== "None" && (
              <div className="missing-box">
                🔍 Missing: {item.missing_concept}
              </div>
            )}
          </div>
        ))
      ) : (
        // Fallback if no breakdown (analysis not implemented yet)
        summary.questions?.map((q, i) => (
          <div key={i} className="qa-card">
            <div className="qa-header">
              <span className="q-number">Q{i + 1}</span>
            </div>
            <p className="q-text"><strong>Q:</strong> {q}</p>
            <p className="a-text">
              <strong>A:</strong> {summary.answers?.[i] || "No answer given"}
            </p>
          </div>
        ))
      )}

      {/* Restart */}
      <button onClick={() => window.location.reload()}>
        Start New Interview
      </button>
    </div>
  )
}