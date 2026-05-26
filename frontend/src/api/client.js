import axios from "axios"

const API = axios.create({
  baseURL: "http://127.0.0.1:8000"
})

export const uploadResume = (file) => {
  const form = new FormData()
  form.append("file", file)
  return API.post("/upload", form)
}

export const startSession = (role) =>
  API.post(`/start?role=${encodeURIComponent(role)}`)

export const getQuestion = (sessionId) =>
  API.get(`/question?session_id=${sessionId}`)

export const submitAnswer = (sessionId, answer) =>
  API.post(`/answer?session_id=${sessionId}&answer=${encodeURIComponent(answer)}`)

export const getSummary = (sessionId) =>
  API.get(`/summary?session_id=${sessionId}`)