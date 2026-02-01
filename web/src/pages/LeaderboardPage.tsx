import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useTournament, useLeaderboard, usePlayerScorecard } from '../hooks/useTournaments'
import type { LeaderboardPlayer, PlayerScorecard, ScorecardHole } from '../types'

function ScoreDisplay({ score, par }: { score: number; par: number }) {
  const diff = score - par
  let colorClass = 'text-gray-900'

  if (diff < -1) colorClass = 'text-yellow-600 font-bold' // Eagle or better
  else if (diff === -1) colorClass = 'text-red-600' // Birdie
  else if (diff === 1) colorClass = 'text-blue-600' // Bogey
  else if (diff > 1) colorClass = 'text-blue-800' // Double+

  return <span className={colorClass}>{score}</span>
}

function ScorecardRow({
  holes,
  label
}: {
  holes: ScorecardHole[]
  label: string
}) {
  const front9 = holes.slice(0, 9)
  const back9 = holes.slice(9, 18)
  const front9Total = front9.reduce((sum, h) => sum + h.score, 0)
  const back9Total = back9.reduce((sum, h) => sum + h.score, 0)
  const front9Par = front9.reduce((sum, h) => sum + h.par, 0)
  const back9Par = back9.reduce((sum, h) => sum + h.par, 0)

  return (
    <div className="mb-4">
      <div className="text-sm font-medium text-gray-700 mb-1">{label}</div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="bg-gray-100">
              <th className="px-2 py-1 text-left text-xs font-medium text-gray-500">Hole</th>
              {front9.map((h) => (
                <th key={h.holeNumber} className="px-2 py-1 text-center text-xs font-medium text-gray-500">
                  {h.holeNumber}
                </th>
              ))}
              <th className="px-2 py-1 text-center text-xs font-medium text-gray-500 bg-gray-200">Out</th>
              {back9.map((h) => (
                <th key={h.holeNumber} className="px-2 py-1 text-center text-xs font-medium text-gray-500">
                  {h.holeNumber}
                </th>
              ))}
              <th className="px-2 py-1 text-center text-xs font-medium text-gray-500 bg-gray-200">In</th>
              <th className="px-2 py-1 text-center text-xs font-medium text-gray-500 bg-gray-300">Tot</th>
            </tr>
          </thead>
          <tbody>
            <tr className="bg-gray-50">
              <td className="px-2 py-1 text-xs text-gray-500">Par</td>
              {front9.map((h) => (
                <td key={h.holeNumber} className="px-2 py-1 text-center text-xs text-gray-500">
                  {h.par}
                </td>
              ))}
              <td className="px-2 py-1 text-center text-xs text-gray-500 bg-gray-100">{front9Par}</td>
              {back9.map((h) => (
                <td key={h.holeNumber} className="px-2 py-1 text-center text-xs text-gray-500">
                  {h.par}
                </td>
              ))}
              <td className="px-2 py-1 text-center text-xs text-gray-500 bg-gray-100">{back9Par}</td>
              <td className="px-2 py-1 text-center text-xs text-gray-500 bg-gray-200">{front9Par + back9Par}</td>
            </tr>
            <tr>
              <td className="px-2 py-1 text-xs font-medium text-gray-700">Score</td>
              {front9.map((h) => (
                <td key={h.holeNumber} className="px-2 py-1 text-center">
                  <ScoreDisplay score={h.score} par={h.par} />
                </td>
              ))}
              <td className="px-2 py-1 text-center font-medium bg-gray-100">{front9Total}</td>
              {back9.map((h) => (
                <td key={h.holeNumber} className="px-2 py-1 text-center">
                  <ScoreDisplay score={h.score} par={h.par} />
                </td>
              ))}
              <td className="px-2 py-1 text-center font-medium bg-gray-100">{back9Total}</td>
              <td className="px-2 py-1 text-center font-bold bg-gray-200">{front9Total + back9Total}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}

function PlayerScorecard({ scorecard }: { scorecard: PlayerScorecard }) {
  return (
    <div className="mt-4 bg-gray-50 rounded-lg p-4">
      {scorecard.rounds.map((round) => (
        <ScorecardRow
          key={round.roundNumber}
          holes={round.holes}
          label={`Round ${round.roundNumber}`}
        />
      ))}
    </div>
  )
}

function LeaderboardRow({
  player,
  expanded,
  onToggle,
}: {
  player: LeaderboardPlayer
  expanded: boolean
  onToggle: () => void
}) {
  const { data: scorecards } = usePlayerScorecard(
    player.tournamentId,
    player.playerId
  )

  return (
    <>
      <tr
        className="hover:bg-gray-50 cursor-pointer transition-colors"
        onClick={onToggle}
      >
        <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
          {player.positionDisplay}
        </td>
        <td className="px-4 py-3 whitespace-nowrap">
          <div className="flex items-center">
            <div>
              <div className="text-sm font-medium text-gray-900">
                {player.playerName}
                {player.isAmateur && (
                  <span className="ml-1 text-xs text-gray-500">(a)</span>
                )}
              </div>
            </div>
          </div>
        </td>
        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 font-medium">
          {player.totalScoreDisplay}
        </td>
        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
          {player.thru}
        </td>
        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
          {player.roundScores?.join(' / ') || '-'}
        </td>
        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-400">
          <svg
            className={`w-5 h-5 transition-transform ${expanded ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </td>
      </tr>
      {expanded && scorecards && scorecards[0] && (
        <tr>
          <td colSpan={6} className="px-4 py-2 bg-gray-50">
            <PlayerScorecard scorecard={scorecards[0]} />
          </td>
        </tr>
      )}
    </>
  )
}

export default function LeaderboardPage() {
  const { tournamentId } = useParams<{ tournamentId: string }>()
  const { data: tournament, isLoading: tournamentLoading } = useTournament(tournamentId!)
  const { data: leaderboard, isLoading: leaderboardLoading } = useLeaderboard(tournamentId!)
  const [expandedPlayer, setExpandedPlayer] = useState<string | null>(null)

  const isLoading = tournamentLoading || leaderboardLoading

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
      </div>
    )
  }

  if (!tournament) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-600">Tournament not found.</p>
        <Link to="/" className="text-green-600 hover:underline mt-2 inline-block">
          Back to tournaments
        </Link>
      </div>
    )
  }

  const sortedLeaderboard = [...(leaderboard || [])].sort(
    (a, b) => a.position - b.position
  )

  return (
    <div>
      <div className="mb-6">
        <Link
          to="/"
          className="text-green-600 hover:text-green-700 text-sm flex items-center gap-1 mb-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to tournaments
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">{tournament.name}</h1>
        <p className="mt-1 text-gray-600">
          {tournament.courseName} - {tournament.city}, {tournament.state || tournament.country}
        </p>
      </div>

      {sortedLeaderboard.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No leaderboard data available.</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Pos
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Player
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Score
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Thru
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rounds
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">

                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {sortedLeaderboard.map((player) => (
                  <LeaderboardRow
                    key={player.id}
                    player={player}
                    expanded={expandedPlayer === player.id}
                    onToggle={() =>
                      setExpandedPlayer(
                        expandedPlayer === player.id ? null : player.id
                      )
                    }
                  />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
