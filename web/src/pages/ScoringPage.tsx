import { useParams, Link } from 'react-router-dom'
import { useLeague, useTournamentScoring } from '../hooks/useLeague'
import { useTournament } from '../hooks/useTournaments'
import { useAuth } from '../hooks/useAuth'
import type { FantasyScore, PlayerScore } from '../types'

function PlayerScoreRow({ playerScore }: { playerScore: PlayerScore }) {
  const { breakdown } = playerScore

  return (
    <tr className="hover:bg-gray-50">
      <td className="px-4 py-3 text-sm font-medium text-gray-900">
        {playerScore.playerName}
      </td>
      <td className="px-4 py-3 text-sm text-gray-500 text-center">
        {breakdown.eagles > 0 && <span className="text-yellow-600">{breakdown.eagles}</span>}
      </td>
      <td className="px-4 py-3 text-sm text-gray-500 text-center">
        {breakdown.birdies > 0 && <span className="text-red-600">{breakdown.birdies}</span>}
      </td>
      <td className="px-4 py-3 text-sm text-gray-500 text-center">
        {breakdown.pars > 0 && breakdown.pars}
      </td>
      <td className="px-4 py-3 text-sm text-gray-500 text-center">
        {breakdown.bogeys > 0 && <span className="text-blue-600">{breakdown.bogeys}</span>}
      </td>
      <td className="px-4 py-3 text-sm text-gray-500 text-center">
        {breakdown.doubleBogeys > 0 && (
          <span className="text-blue-800">{breakdown.doubleBogeys}</span>
        )}
      </td>
      <td className="px-4 py-3 text-sm text-gray-500 text-center">
        {(breakdown.streakBonus || 0) > 0 && (
          <span className="text-green-600">+{breakdown.streakBonus}</span>
        )}
      </td>
      <td className="px-4 py-3 text-sm text-gray-500 text-center">
        {(breakdown.positionBonus || 0) > 0 && (
          <span className="text-purple-600">+{breakdown.positionBonus}</span>
        )}
      </td>
      <td className="px-4 py-3 text-sm font-bold text-gray-900 text-right">
        {playerScore.score.toFixed(1)}
      </td>
    </tr>
  )
}

function MemberScoreCard({
  score,
  isCurrentUser,
}: {
  score: FantasyScore
  isCurrentUser: boolean
}) {
  return (
    <div
      className={`bg-white rounded-lg shadow overflow-hidden ${
        isCurrentUser ? 'ring-2 ring-green-500' : ''
      }`}
    >
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-gray-50">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            {score.userName}
            {isCurrentUser && <span className="ml-2 text-sm text-green-600">(You)</span>}
          </h3>
          <p className="text-sm text-gray-500">Rank #{score.rank}</p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-gray-900">
            {score.totalScore.toFixed(1)}
          </div>
          <div className="text-sm text-gray-500">Total Points</div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                Player
              </th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
                Eagle
              </th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
                Birdie
              </th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
                Par
              </th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
                Bogey
              </th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
                Dbl+
              </th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
                Bonus
              </th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
                Pos
              </th>
              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                Pts
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {score.playerScores.map((playerScore) => (
              <PlayerScoreRow key={playerScore.playerId} playerScore={playerScore} />
            ))}
          </tbody>
          <tfoot>
            <tr className="bg-gray-50">
              <td colSpan={8} className="px-4 py-2 text-sm font-semibold text-gray-700">
                Total
              </td>
              <td className="px-4 py-2 text-sm font-bold text-gray-900 text-right">
                {score.totalScore.toFixed(1)}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  )
}

export default function ScoringPage() {
  const { id: leagueId, tournamentId } = useParams<{ id: string; tournamentId: string }>()
  const { user } = useAuth()
  const { data: league } = useLeague(leagueId!)
  const { data: tournament } = useTournament(tournamentId!)
  const { data: scores, isLoading } = useTournamentScoring(leagueId!, tournamentId!)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
      </div>
    )
  }

  const sortedScores = [...(scores || [])].sort((a, b) => a.rank - b.rank)

  return (
    <div>
      <div className="mb-6">
        <Link
          to={`/leagues/${leagueId}`}
          className="text-green-600 hover:text-green-700 text-sm flex items-center gap-1 mb-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to league
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Scoring Breakdown</h1>
        <p className="mt-1 text-gray-600">
          {tournament?.name} - {league?.name}
        </p>
      </div>

      {/* Scoring legend */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h2 className="text-sm font-semibold text-gray-900 mb-3">Scoring Key</h2>
        <div className="flex flex-wrap gap-4 text-sm">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 bg-yellow-500 rounded-full"></span>
            <span>Eagle: +{league?.scoringConfig.eagle_or_better}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 bg-red-500 rounded-full"></span>
            <span>Birdie: +{league?.scoringConfig.birdie}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 bg-gray-400 rounded-full"></span>
            <span>Par: +{league?.scoringConfig.par}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 bg-blue-500 rounded-full"></span>
            <span>Bogey: {league?.scoringConfig.bogey}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 bg-blue-800 rounded-full"></span>
            <span>Double+: {league?.scoringConfig.double_bogey_or_worse}</span>
          </div>
        </div>
      </div>

      {sortedScores.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500">No scores available yet.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {sortedScores.map((score) => (
            <MemberScoreCard
              key={score.userId}
              score={score}
              isCurrentUser={score.userId === user?.id}
            />
          ))}
        </div>
      )}
    </div>
  )
}
