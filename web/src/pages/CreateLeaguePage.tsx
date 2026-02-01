import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useTournaments } from '../hooks/useTournaments'
import { useCreateLeague } from '../hooks/useLeague'
import type { RosterConfig, ScoringConfig, TierConfig } from '../types'

const DEFAULT_SCORING_CONFIG: ScoringConfig = {
  eagle_or_better: 8,
  birdie: 3,
  par: 0.5,
  bogey: -0.5,
  double_bogey_or_worse: -1,
  streak_bonus_3: 3,
  streak_bonus_5: 5,
  bounce_back: 2,
  bogey_free_round: 3,
  position_1: 30,
  position_2: 20,
  position_3: 18,
  position_4: 16,
  position_5: 14,
  position_6_10: 10,
  position_11_20: 5,
  position_21_30: 3,
  made_cut: 1,
}

const DEFAULT_TIERS: TierConfig[] = [
  { tier: 1, name: 'Tier 1', picks_allowed: 1 },
  { tier: 2, name: 'Tier 2', picks_allowed: 1 },
  { tier: 3, name: 'Tier 3', picks_allowed: 2 },
  { tier: 4, name: 'Tier 4', picks_allowed: 2 },
]

export default function CreateLeaguePage() {
  const navigate = useNavigate()
  const { data: tournaments } = useTournaments()
  const createLeague = useCreateLeague()

  const [name, setName] = useState('')
  const [leagueType, setLeagueType] = useState<'season' | 'tournament'>('season')
  const [tournamentId, setTournamentId] = useState('')
  const [isPublic, setIsPublic] = useState(false)
  const [pickDeadlineType, setPickDeadlineType] = useState('tournament_start')

  // Roster config
  const [rosterSize, setRosterSize] = useState(6)
  const [useTiers, setUseTiers] = useState(false)
  const [tiers, setTiers] = useState<TierConfig[]>(DEFAULT_TIERS)
  const [useSalaryCap, setUseSalaryCap] = useState(false)
  const [salaryCap, setSalaryCap] = useState(50000)

  const [scoringConfig] = useState<ScoringConfig>(DEFAULT_SCORING_CONFIG)
  const [showAdvanced, setShowAdvanced] = useState(false)

  const upcomingTournaments = tournaments?.filter(t => !t.isCompleted) || []

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const rosterConfig: RosterConfig = {
      roster_size: rosterSize,
      use_tiers: useTiers,
      tiers: useTiers ? tiers : undefined,
      use_salary_cap: useSalaryCap,
      salary_cap: useSalaryCap ? salaryCap : undefined,
    }

    try {
      const league = await createLeague.mutateAsync({
        name,
        leagueType,
        tournamentId: leagueType === 'tournament' ? tournamentId : undefined,
        rosterConfig,
        scoringConfig,
        pickDeadlineType,
        isPublic,
      })
      navigate(`/leagues/${league.id}`)
    } catch {
      // Error handling is done through the mutation state
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
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
        <h1 className="text-2xl font-bold text-gray-900">Create Fantasy League</h1>
        <p className="mt-1 text-gray-600">Set up a new fantasy golf league</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">Basic Info</h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              League Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Enter league name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              League Type
            </label>
            <div className="flex gap-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="season"
                  checked={leagueType === 'season'}
                  onChange={(e) => setLeagueType(e.target.value as 'season' | 'tournament')}
                  className="mr-2 text-green-600 focus:ring-green-500"
                />
                <span className="text-sm text-gray-700">Season Long</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="tournament"
                  checked={leagueType === 'tournament'}
                  onChange={(e) => setLeagueType(e.target.value as 'season' | 'tournament')}
                  className="mr-2 text-green-600 focus:ring-green-500"
                />
                <span className="text-sm text-gray-700">Single Tournament</span>
              </label>
            </div>
          </div>

          {leagueType === 'tournament' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tournament
              </label>
              <select
                value={tournamentId}
                onChange={(e) => setTournamentId(e.target.value)}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="">Select a tournament</option>
                {upcomingTournaments.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="isPublic"
              checked={isPublic}
              onChange={(e) => setIsPublic(e.target.checked)}
              className="rounded border-gray-300 text-green-600 focus:ring-green-500"
            />
            <label htmlFor="isPublic" className="text-sm text-gray-700">
              Make this league public (anyone can join)
            </label>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">Roster Configuration</h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Roster Size
            </label>
            <input
              type="number"
              value={rosterSize}
              onChange={(e) => setRosterSize(parseInt(e.target.value) || 6)}
              min={1}
              max={20}
              className="w-32 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
            <p className="mt-1 text-sm text-gray-500">Number of players each member picks</p>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="useTiers"
              checked={useTiers}
              onChange={(e) => setUseTiers(e.target.checked)}
              className="rounded border-gray-300 text-green-600 focus:ring-green-500"
            />
            <label htmlFor="useTiers" className="text-sm text-gray-700">
              Use tiered picks (e.g., 1 from Tier 1, 2 from Tier 2, etc.)
            </label>
          </div>

          {useTiers && (
            <div className="pl-6 space-y-2">
              {tiers.map((tier, index) => (
                <div key={tier.tier} className="flex items-center gap-4">
                  <span className="text-sm text-gray-600 w-16">Tier {tier.tier}</span>
                  <input
                    type="number"
                    value={tier.picks_allowed}
                    onChange={(e) => {
                      const newTiers = [...tiers]
                      newTiers[index].picks_allowed = parseInt(e.target.value) || 1
                      setTiers(newTiers)
                    }}
                    min={1}
                    className="w-20 px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm"
                  />
                  <span className="text-sm text-gray-500">picks</span>
                </div>
              ))}
            </div>
          )}

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="useSalaryCap"
              checked={useSalaryCap}
              onChange={(e) => setUseSalaryCap(e.target.checked)}
              className="rounded border-gray-300 text-green-600 focus:ring-green-500"
            />
            <label htmlFor="useSalaryCap" className="text-sm text-gray-700">
              Use salary cap
            </label>
          </div>

          {useSalaryCap && (
            <div className="pl-6">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Salary Cap
              </label>
              <div className="flex items-center gap-2">
                <span className="text-gray-500">$</span>
                <input
                  type="number"
                  value={salaryCap}
                  onChange={(e) => setSalaryCap(parseInt(e.target.value) || 50000)}
                  min={10000}
                  step={1000}
                  className="w-32 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Pick Deadline</h2>
          </div>

          <div>
            <select
              value={pickDeadlineType}
              onChange={(e) => setPickDeadlineType(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="tournament_start">Tournament Start</option>
              <option value="first_tee_time">First Tee Time</option>
            </select>
            <p className="mt-1 text-sm text-gray-500">
              Picks must be submitted before this deadline
            </p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center justify-between w-full text-left"
          >
            <h2 className="text-lg font-semibold text-gray-900">Scoring Rules</h2>
            <svg
              className={`w-5 h-5 text-gray-500 transition-transform ${showAdvanced ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {showAdvanced && (
            <div className="mt-4 space-y-4">
              <p className="text-sm text-gray-600">
                Using PGA Tour Fantasy scoring rules. Customization coming soon.
              </p>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Eagle or Better</span>
                    <span className="font-medium">+{scoringConfig.eagle_or_better}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Birdie</span>
                    <span className="font-medium">+{scoringConfig.birdie}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Par</span>
                    <span className="font-medium">+{scoringConfig.par}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Bogey</span>
                    <span className="font-medium">{scoringConfig.bogey}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Double Bogey+</span>
                    <span className="font-medium">{scoringConfig.double_bogey_or_worse}</span>
                  </div>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-gray-600">1st Place</span>
                    <span className="font-medium">+{scoringConfig.position_1}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">2nd Place</span>
                    <span className="font-medium">+{scoringConfig.position_2}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">3rd Place</span>
                    <span className="font-medium">+{scoringConfig.position_3}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Bogey Free Round</span>
                    <span className="font-medium">+{scoringConfig.bogey_free_round}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Bounce Back</span>
                    <span className="font-medium">+{scoringConfig.bounce_back}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {createLeague.error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-600 text-sm">
              {createLeague.error instanceof Error
                ? createLeague.error.message
                : 'Failed to create league. Please try again.'}
            </p>
          </div>
        )}

        <div className="flex gap-4">
          <button
            type="submit"
            disabled={createLeague.isPending}
            className="flex-1 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {createLeague.isPending ? 'Creating...' : 'Create League'}
          </button>
          <Link
            to="/leagues"
            className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
          >
            Cancel
          </Link>
        </div>
      </form>
    </div>
  )
}
