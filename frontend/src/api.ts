const API_BASE = "https://skillset-match-3.onrender.com/";
// const API_BASE = "http://localhost:8000";

export const fetchUsers = () =>
  fetch(`${API_BASE}/user/`).then(r => r.json());

export const fetchSkills = () =>
  fetch(`${API_BASE}/skill/`).then(r => r.json());

export const fetchSessions = () =>
  fetch(`${API_BASE}/session/`).then(r => r.json());

export const fetchSkillMatches = () =>
  fetch(`${API_BASE}/skillmatch/`).then(r => r.json());

export const createUser = (data: any) =>
  fetch(`${API_BASE}/user/`, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(data) }).then(r => r.json());

export const createUserSkill = (data: any) =>
  fetch(`${API_BASE}/userskill/`, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(data) }).then(r => r.json());

export const createSkill = (data: any) =>
  fetch(`${API_BASE}/skill/`, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(data) }).then(r => r.json());

export const createSkillRequest = (data: any) =>
  fetch(`${API_BASE}/skillrequest/`, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(data) }).then(r => r.json());

export const runMatching = () =>
  fetch(`${API_BASE}/run-matching/`, { method: "POST" }).then(r => r.json());

export const completeSession = (sessionId: number, rating: number, comment: string) =>
  fetch(`${API_BASE}/complete-session/${sessionId}/?rating=${rating}&comment=${encodeURIComponent(comment)}`, { method: "POST" }).then(r => r.json());
