import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Mock Firebase
vi.mock('../services/firebase', () => ({
  auth: {
    currentUser: null,
  },
}))

vi.mock('../services/auth', () => ({
  onAuthStateChanged: vi.fn((callback) => {
    callback(null)
    return () => {}
  }),
  getCurrentUser: vi.fn(() => null),
  signInWithGoogle: vi.fn(),
  signOut: vi.fn(),
  getIdToken: vi.fn(() => Promise.resolve(null)),
}))

import App from '../App'

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{ui}</BrowserRouter>
    </QueryClientProvider>
  )
}

describe('App', () => {
  it('redirects to login when not authenticated', () => {
    renderWithProviders(<App />)
    expect(screen.getByText('Golf Better')).toBeInTheDocument()
    expect(screen.getByText('Sign in with Google')).toBeInTheDocument()
  })
})
