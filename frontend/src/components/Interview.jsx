import { useState, useEffect, useRef } from "react"
import { getQuestion, submitAnswer } from "../api/client"

const MAX_QUESTIONS = 5

export default function Interview({ sessionId, onDone }) {
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState("")
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [questionCount, setQuestionCount] = useState(0)
  const [error, setError] = useState("")
  const [answered, setAnswered] = useState(false)
  const hasLoaded = useRef(false)

  // Fetch first question ONCE on mount
  useEffect(() => {
    if (!hasLoaded.current) {
      hasLoaded.current = true
      fetchQuestion()
    }
  }, [])

  const fetchQuestion = async () => {
    setLoading(true)
    setError("")
    setAnswered(false)
    setAnswer("")

    try {
      const res = await getQuestion(sessionId)
      setQuestion(res.data.question)
      setQuestionCount((prev) => prev + 1)
    } catch (err) {
      setError("Failed to fetch question. Is backend running?")
    } finally {
      setLoading(false)
    }
  }

  const handleSubmitAnswer = async () => {
    if (!answer.trim()) return setError("Please type an answer first")

    setSubmitting(true)
    setError("")

    try {
      await submitAnswer(sessionId, answer)
      setAnswered(true)
    } catch (err) {
      setError("Failed to submit answer.")
    } finally {
      setSubmitting(false)
    }
  }

  const handleNext = () => {
    if (questionCount >= MAX_QUESTIONS) {
      onDone()
    } else {
      fetchQuestion()
    }
  }

  return (
    <div className="card">
      {/* Header */}
      <div className="interview-header">
        <h2>Technical Interview</h2>
        <span className="counter">Question {questionCount} / {MAX_QUESTIONS}</span>
      </div>

      {/* Progress dots */}
      <div className="dots">
        {Array.from({ length: MAX_QUESTIONS }).map((_, i) => (
          <span
            key={i}
            className={`dot ${i < questionCount ? "filled" : ""}`}
          />
        ))}
      </div>

      {/* Question */}
      {loading ? (
        <div className="loading-box">
          <span className="spinner" /> Generating question...
        </div>
      ) : (
        <div className="question-box">
          <p>{question}</p>
        </div>
      )}

      {/* Answer input — only show when not loading and not yet answered */}
      {!loading && !answered && (
        <textarea
          placeholder="Type your answer here..."
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          rows={5}
        />
      )}

      {/* Show answer after submission */}
      {!loading && answered && (
        <div className="answered-box">
          <p><strong>Your answer:</strong> {answer}</p>
        </div>
      )}

      {error && <p className="error">{error}</p>}

      {/* Buttons */}
      {!loading && (
        <div className="btn-row">
          {!answered ? (
            <button onClick={handleSubmitAnswer} disabled={submitting}>
              {submitting ? "Submitting..." : "Submit Answer"}
            </button>
          ) : (
            <button onClick={handleNext}>
              {questionCount >= MAX_QUESTIONS ? "View Summary →" : "Next Question →"}
            </button>
          )}
        </div>
      )}
    </div>
  )
}