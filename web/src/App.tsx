import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import TournamentsPage from './pages/TournamentsPage'
import LeaderboardPage from './pages/LeaderboardPage'
import LeaguesPage from './pages/LeaguesPage'
import LeagueDetailPage from './pages/LeagueDetailPage'
import CreateLeaguePage from './pages/CreateLeaguePage'
import PicksPage from './pages/PicksPage'
import ScoringPage from './pages/ScoringPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<TournamentsPage />} />
        <Route path="leaderboard/:tournamentId" element={<LeaderboardPage />} />
        <Route path="leagues" element={<LeaguesPage />} />
        <Route path="leagues/create" element={<CreateLeaguePage />} />
        <Route path="leagues/:id" element={<LeagueDetailPage />} />
        <Route path="leagues/:id/picks/:tournamentId" element={<PicksPage />} />
        <Route path="leagues/:id/scoring/:tournamentId" element={<ScoringPage />} />
      </Route>
    </Routes>
  )
}

export default App
