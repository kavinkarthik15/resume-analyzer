const STORAGE_KEY = 'resumes'

function parseStoredWorkspaces() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    const parsed = raw ? JSON.parse(raw) : []
    return Array.isArray(parsed) ? parsed : []
  } catch (error) {
    console.error('Failed to parse stored workspaces:', error)
    return []
  }
}

function writeWorkspaces(workspaces) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(workspaces))
}

export function createWorkspaceId() {
  return `resume_${Date.now()}_${Math.floor(Math.random() * 10000)}`
}

export function listWorkspaces() {
  return parseStoredWorkspaces().sort((a, b) => (b?.updatedAt || 0) - (a?.updatedAt || 0))
}

export function loadWorkspace(id) {
  return parseStoredWorkspaces().find((workspace) => workspace?.id === id) || null
}

export function saveWorkspace(workspace) {
  if (!workspace?.id) return

  const existing = parseStoredWorkspaces()
  const updated = [
    ...existing.filter((item) => item?.id !== workspace.id),
    workspace,
  ]

  writeWorkspaces(updated)
}

export function deleteWorkspace(id) {
  const existing = parseStoredWorkspaces()
  const updated = existing.filter((workspace) => workspace?.id !== id)
  writeWorkspaces(updated)
  return updated
}
