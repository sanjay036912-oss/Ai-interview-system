import { useState } from "react"
import UploadResume from "./components/UploadResume"
import RoleSelect from "./components/RoleSelect"
import Interview from "./components/Interview"
import Summary from "./components/Summary"
import "./App.css"

export default function App() {
  const [step, setStep] = useState(1)
  const [sessionId, setSessionId] = useState(null)
  const [skills, setSkills] = useState("")

  return (
    <div className="app">
      {/* Progress bar */}
      <div className="progress">
        {["Upload Resume", "Select Role", "Interview", "Summary"].map((label, i) => (
          <div key={i} className={`step ${step === i + 1 ? "active" : step > i + 1 ? "done" : ""}`}>
            <span>{i + 1}</span> {label}
          </div>
        ))}
      </div>

      {/* Screens */}
      {step === 1 && (
        <UploadResume
          onDone={(extractedSkills) => {
            setSkills(extractedSkills)
            setStep(2)
          }}
        />
      )}
      {step === 2 && (
        <RoleSelect
          onDone={(sid) => {
            setSessionId(sid)
            setStep(3)
          }}
        />
      )}
      {step === 3 && (
        <Interview
          sessionId={sessionId}
          onDone={() => setStep(4)}
        />
      )}
      {step === 4 && (
        <Summary sessionId={sessionId} />
      )}
    </div>
  )
}