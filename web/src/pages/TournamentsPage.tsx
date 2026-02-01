import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { useTournaments } from '../hooks/useTournaments'
import type { Tournament } from '../types'

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function TournamentCard({ tournament }: { tournament: Tournament }) {
  return (
    <Link
      to={`/leaderboard/${tournament.id}`}
      className="block bg-white rounded-lg shadow hover:shadow-md transition-shadow border border-gray-200"
    >
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              {tournament.name}
            </h3>
            <p className="text-sm text-gray-600 mb-2">
              {tournament.courseName}
            </p>
            <p className="text-sm text-gray-500">
              {tournament.city}, {tournament.state || tournament.country}
            </p>
          </div>
          <div className="text-right ml-4">
            <span
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                tournament.isCompleted
                  ? 'bg-gray-100 text-gray-800'
                  : 'bg-green-100 text-green-800'
              }`}
            >
              {tournament.isCompleted ? 'Completed' : 'In Progress'}
            </span>
          </div>
        </div>
        <div className="mt-4 pt-4 border-t border-gray-100 flex justify-between text-sm">
          <span className="text-gray-500">
            {formatDate(tournament.startDate)} - {formatDate(tournament.endDate)}
          </span>
          {tournament.purse && (
            <span className="text-gray-600 font-medium">
              ${(tournament.purse / 1000000).toFixed(1)}M
            </span>
          )}
        </div>
        {tournament.isCompleted && tournament.winnerName && (
          <div className="mt-3 flex items-center text-sm">
            <span className="text-yellow-600 mr-1">🏆</span>
            <span className="text-gray-700">{tournament.winnerName}</span>
          </div>
        )}
      </div>
    </Link>
  )
}

export default function TournamentsPage() {
  const { data: tournaments, isLoading, error } = useTournaments()
  const [filter, setFilter] = useState<'all' | 'upcoming' | 'completed'>('all')
  const [searchQuery, setSearchQuery] = useState('')

  const filteredTournaments = useMemo(() => {
    if (!tournaments) return []

    let filtered = [...tournaments]

    // Apply status filter
    if (filter === 'upcoming') {
      filtered = filtered.filter((t) => !t.isCompleted)
    } else if (filter === 'completed') {
      filtered = filtered.filter((t) => t.isCompleted)
    }

    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (t) =>
          t.name.toLowerCase().includes(query) ||
          t.courseName?.toLowerCase().includes(query) ||
          t.city?.toLowerCase().includes(query)
      )
    }

    // Sort by start date (most recent first)
    filtered.sort(
      (a, b) => new Date(b.startDate).getTime() - new Date(a.startDate).getTime()
    )

    return filtered
  }, [tournaments, filter, searchQuery])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-600">Failed to load tournaments. Please try again.</p>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">PGA Tournaments</h1>
        <p className="mt-1 text-gray-600">Browse and view tournament leaderboards</p>
      </div>

      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Search tournaments..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
        </div>
        <div className="flex gap-2">
          {(['all', 'upcoming', 'completed'] as const).map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === status
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {filteredTournaments.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No tournaments found.</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredTournaments.map((tournament) => (
            <TournamentCard key={tournament.id} tournament={tournament} />
          ))}
        </div>
      )}
    </div>
  )
}
