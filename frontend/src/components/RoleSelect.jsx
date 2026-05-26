import { useState } from "react"
import { startSession } from "../api/client"

const ROLES = [
  "Backend Engineer",
  "AI/ML Engineer",
  "Data Scientist",
  "Frontend Engineer",
  "DevOps Engineer"
]

export default function RoleSelect({ onDone }) {
  const [selected, setSelected] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleStart = async () => {
    if (!selected) return setError("Please select a role")

    setLoading(true)
    setError("")

    try {
      const res = await startSession(selected)
      onDone(res.data.session_id)
    } catch (err) {
      setError("Failed to start session. Is your backend running?")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Select Your Target Role</h2>
      <p>Questions will be tailored to this role</p>

      <div className="roles">
        {ROLES.map((role) => (
          <button
            key={role}
            className={`role-btn ${selected === role ? "selected" : ""}`}
            onClick={() => setSelected(role)}
          >
            {role}
          </button>
        ))}
      </div>

      {error && <p className="error">{error}</p>}

      <button onClick={handleStart} disabled={loading || !selected}>
        {loading ? "Starting..." : "Start Interview →"}
      </button>
    </div>
  )
}