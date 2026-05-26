import { useState } from "react"
import { uploadResume } from "../api/client"

export default function UploadResume({ onDone }) {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleUpload = async () => {
    if (!file) return setError("Please select a file first")

    setLoading(true)
    setError("")

    try {
      const res = await uploadResume(file)
      onDone(res.data.skills)
    } catch (err) {
      setError("Upload failed. Is your backend running?")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Upload Your Resume</h2>
      <p>Supported format: PDF</p>

      <input
        type="file"
        accept=".pdf"
        onChange={(e) => setFile(e.target.files[0])}
      />

      {file && <p className="filename">📄 {file.name}</p>}
      {error && <p className="error">{error}</p>}

      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Processing..." : "Upload & Continue →"}
      </button>
    </div>
  )
}