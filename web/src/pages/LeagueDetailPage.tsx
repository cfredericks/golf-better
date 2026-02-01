import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useLeague, useLeagueMembers, useLeagueStandings, useInviteToLeague } from '../hooks/useLeague'
import { useTournaments } from '../hooks/useTournaments'
import { useAuth } from '../hooks/useAuth'

export default function LeagueDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const { data: league, isLoading: leagueLoading } = useLeague(id!)
  const { data: members } = useLeagueMembers(id!)
  const { data: standings } = useLeagueStandings(id!)
  const { data: tournaments } = useTournaments()
  const inviteToLeague = useInviteToLeague()

  const [activeTab, setActiveTab] = useState<'standings' | 'members' | 'settings'>('standings')
  const [inviteEmail, setInviteEmail] = useState('')
  const [showInviteModal, setShowInviteModal] = useState(false)

  const isOwner = league?.ownerId === user?.id

  const upcomingTournaments = tournaments?.filter(t => !t.isCompleted) || []

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!id || !inviteEmail) return
    try {
      await inviteToLeague.mutateAsync({ leagueId: id, email: inviteEmail })
      setInviteEmail('')
      setShowInviteModal(false)
    } catch {
      // Error handling done through mutation state
    }
  }

  if (leagueLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
      </div>
    )
  }

  if (!league) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-600">League not found.</p>
        <Link to="/leagues" className="text-green-600 hover:underline mt-2 inline-block">
          Back to leagues
        </Link>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6">
        <Link
          to="/leagues"
          className="text-green-600 hover:text-green-700 text-sm flex items-center gap-1 mb-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to leagues
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{league.name}</h1>
            <p className="mt-1 text-gray-600">
              {league.leagueType === 'season' ? 'Season League' : 'Tournament League'}
              {league.isPublic && <span className="ml-2 text-blue-600">(Public)</span>}
            </p>
          </div>
          {isOwner && (
            <button
              onClick={() => setShowInviteModal(true)}
              className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
            >
              Invite Members
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {(['standings', 'members', 'settings'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab
                  ? 'border-green-500 text-green-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </nav>
      </div>

      {/* Standings Tab */}
      {activeTab === 'standings' && (
        <div className="space-y-6">
          {/* Upcoming tournaments for picks */}
          {upcomingTournaments.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Make Your Picks</h2>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {upcomingTournaments.slice(0, 3).map((tournament) => (
                  <Link
                    key={tournament.id}
                    to={`/leagues/${id}/picks/${tournament.id}`}
                    className="p-4 border border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50 transition-colors"
                  >
                    <div className="font-medium text-gray-900">{tournament.name}</div>
                    <div className="text-sm text-gray-500 mt-1">
                      Starts {new Date(tournament.startDate).toLocaleDateString()}
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Standings table */}
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">League Standings</h2>
            </div>
            {standings && standings.length > 0 ? (
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Rank
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Player
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total Score
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {standings.map((standing) => (
                    <tr key={standing.userId} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {standing.rank}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {standing.userName}
                        {standing.userId === user?.id && (
                          <span className="ml-2 text-xs text-green-600">(You)</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right font-medium">
                        {standing.totalScore.toFixed(1)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="px-6 py-8 text-center text-gray-500">
                No standings yet. Scores will appear after picks are made.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Members Tab */}
      {activeTab === 'members' && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h2 className="text-lg font-semibold text-gray-900">
              Members ({members?.length || 0})
            </h2>
            {league.inviteCode && (
              <div className="text-sm">
                <span className="text-gray-500">Invite Code: </span>
                <code className="bg-gray-100 px-2 py-1 rounded font-mono">
                  {league.inviteCode}
                </code>
              </div>
            )}
          </div>
          {members && members.length > 0 ? (
            <ul className="divide-y divide-gray-200">
              {members.map((member) => (
                <li key={member.id} className="px-6 py-4 flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {member.userName}
                      {member.userId === user?.id && (
                        <span className="ml-2 text-xs text-green-600">(You)</span>
                      )}
                    </div>
                    <div className="text-sm text-gray-500">
                      Joined {new Date(member.joinedAt).toLocaleDateString()}
                    </div>
                  </div>
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      member.role === 'owner'
                        ? 'bg-purple-100 text-purple-800'
                        : member.role === 'admin'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {member.role}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="px-6 py-8 text-center text-gray-500">
              No members yet.
            </div>
          )}
        </div>
      )}

      {/* Settings Tab */}
      {activeTab === 'settings' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Roster Configuration</h2>
            <dl className="grid grid-cols-2 gap-4">
              <div>
                <dt className="text-sm text-gray-500">Roster Size</dt>
                <dd className="text-sm font-medium text-gray-900">
                  {league.rosterConfig.roster_size} players
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Pick Style</dt>
                <dd className="text-sm font-medium text-gray-900">
                  {league.rosterConfig.use_tiers ? 'Tiered' : 'Open'}
                </dd>
              </div>
              {league.rosterConfig.use_salary_cap && (
                <div>
                  <dt className="text-sm text-gray-500">Salary Cap</dt>
                  <dd className="text-sm font-medium text-gray-900">
                    ${league.rosterConfig.salary_cap?.toLocaleString()}
                  </dd>
                </div>
              )}
              <div>
                <dt className="text-sm text-gray-500">Pick Deadline</dt>
                <dd className="text-sm font-medium text-gray-900">
                  {league.pickDeadlineType === 'tournament_start'
                    ? 'Tournament Start'
                    : 'First Tee Time'}
                </dd>
              </div>
            </dl>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Scoring Rules</h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Eagle or Better</span>
                  <span className="font-medium">+{league.scoringConfig.eagle_or_better}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Birdie</span>
                  <span className="font-medium">+{league.scoringConfig.birdie}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Par</span>
                  <span className="font-medium">+{league.scoringConfig.par}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Bogey</span>
                  <span className="font-medium">{league.scoringConfig.bogey}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Double Bogey+</span>
                  <span className="font-medium">{league.scoringConfig.double_bogey_or_worse}</span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">1st Place</span>
                  <span className="font-medium">+{league.scoringConfig.position_1}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">2nd Place</span>
                  <span className="font-medium">+{league.scoringConfig.position_2}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">3rd Place</span>
                  <span className="font-medium">+{league.scoringConfig.position_3}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Bogey Free Round</span>
                  <span className="font-medium">+{league.scoringConfig.bogey_free_round}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Bounce Back</span>
                  <span className="font-medium">+{league.scoringConfig.bounce_back}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Invite Member</h3>
            <form onSubmit={handleInvite}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="Enter email address"
                />
              </div>
              {inviteToLeague.error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-600 text-sm">
                    {inviteToLeague.error instanceof Error
                      ? inviteToLeague.error.message
                      : 'Failed to send invitation'}
                  </p>
                </div>
              )}
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={inviteToLeague.isPending}
                  className="flex-1 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium disabled:opacity-50"
                >
                  {inviteToLeague.isPending ? 'Sending...' : 'Send Invite'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowInviteModal(false)}
                  className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
