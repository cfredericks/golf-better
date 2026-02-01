import { useState, useMemo } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useLeague, useAvailablePlayers, usePicks, useSubmitPicks } from '../hooks/useLeague'
import { useTournament } from '../hooks/useTournaments'
import type { AvailablePlayer } from '../types'

function PlayerCard({
  player,
  selected,
  disabled,
  onSelect,
}: {
  player: AvailablePlayer
  selected: boolean
  disabled: boolean
  onSelect: () => void
}) {
  return (
    <button
      onClick={onSelect}
      disabled={disabled && !selected}
      className={`w-full p-4 rounded-lg border text-left transition-all ${
        selected
          ? 'border-green-500 bg-green-50 ring-2 ring-green-500'
          : disabled
          ? 'border-gray-200 bg-gray-50 opacity-50 cursor-not-allowed'
          : 'border-gray-200 hover:border-green-300 hover:bg-green-50'
      }`}
    >
      <div className="flex items-center justify-between">
        <div>
          <div className="font-medium text-gray-900">{player.name}</div>
          <div className="text-sm text-gray-500">
            {player.worldRanking && `World #${player.worldRanking}`}
            {player.tier && <span className="ml-2">Tier {player.tier}</span>}
          </div>
        </div>
        <div className="text-right">
          {player.salary && (
            <div className="text-sm font-medium text-gray-900">
              ${player.salary.toLocaleString()}
            </div>
          )}
          {selected && (
            <div className="mt-1">
              <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
          )}
        </div>
      </div>
    </button>
  )
}

export default function PicksPage() {
  const { id: leagueId, tournamentId } = useParams<{ id: string; tournamentId: string }>()
  const navigate = useNavigate()

  const { data: league } = useLeague(leagueId!)
  const { data: tournament } = useTournament(tournamentId!)
  const { data: availablePlayers, isLoading: playersLoading } = useAvailablePlayers(
    leagueId!,
    tournamentId!
  )
  const { data: existingPicks } = usePicks(leagueId!, tournamentId)
  const submitPicks = useSubmitPicks()

  const [selectedPlayerIds, setSelectedPlayerIds] = useState<string[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [tierFilter, setTierFilter] = useState<number | null>(null)

  // Initialize with existing picks
  useState(() => {
    if (existingPicks) {
      setSelectedPlayerIds(existingPicks.map((p) => p.playerId))
    }
  })

  const rosterConfig = league?.rosterConfig
  const maxPicks = rosterConfig?.roster_size || 6
  const useTiers = rosterConfig?.use_tiers || false
  const useSalaryCap = rosterConfig?.use_salary_cap || false
  const salaryCap = rosterConfig?.salary_cap || 0

  const selectedPlayers = useMemo(() => {
    return availablePlayers?.filter((p) => selectedPlayerIds.includes(p.id)) || []
  }, [availablePlayers, selectedPlayerIds])

  const totalSalary = useMemo(() => {
    return selectedPlayers.reduce((sum, p) => sum + (p.salary || 0), 0)
  }, [selectedPlayers])

  const tierCounts = useMemo(() => {
    const counts: Record<number, number> = {}
    selectedPlayers.forEach((p) => {
      if (p.tier) {
        counts[p.tier] = (counts[p.tier] || 0) + 1
      }
    })
    return counts
  }, [selectedPlayers])

  const filteredPlayers = useMemo(() => {
    if (!availablePlayers) return []

    let filtered = [...availablePlayers]

    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter((p) => p.name.toLowerCase().includes(query))
    }

    if (tierFilter !== null) {
      filtered = filtered.filter((p) => p.tier === tierFilter)
    }

    // Sort by tier, then world ranking
    filtered.sort((a, b) => {
      if (a.tier !== b.tier) return (a.tier || 99) - (b.tier || 99)
      return (a.worldRanking || 999) - (b.worldRanking || 999)
    })

    return filtered
  }, [availablePlayers, searchQuery, tierFilter])

  const canSelectPlayer = (player: AvailablePlayer): boolean => {
    // Already selected
    if (selectedPlayerIds.includes(player.id)) return true

    // Max picks reached
    if (selectedPlayerIds.length >= maxPicks) return false

    // Check tier limit
    if (useTiers && player.tier) {
      const tierConfig = rosterConfig?.tiers?.find((t) => t.tier === player.tier)
      if (tierConfig) {
        const currentTierCount = tierCounts[player.tier] || 0
        if (currentTierCount >= tierConfig.picks_allowed) return false
      }
    }

    // Check salary cap
    if (useSalaryCap && player.salary) {
      if (totalSalary + player.salary > salaryCap) return false
    }

    return true
  }

  const handleSelectPlayer = (playerId: string) => {
    setSelectedPlayerIds((prev) =>
      prev.includes(playerId)
        ? prev.filter((id) => id !== playerId)
        : [...prev, playerId]
    )
  }

  const handleSubmit = async () => {
    if (!leagueId || !tournamentId) return

    try {
      await submitPicks.mutateAsync({
        leagueId,
        tournamentId,
        playerIds: selectedPlayerIds,
      })
      navigate(`/leagues/${leagueId}`)
    } catch {
      // Error handled through mutation state
    }
  }

  const uniqueTiers = useMemo(() => {
    const tiers = new Set<number>()
    availablePlayers?.forEach((p) => {
      if (p.tier) tiers.add(p.tier)
    })
    return Array.from(tiers).sort()
  }, [availablePlayers])

  if (playersLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
      </div>
    )
  }

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
        <h1 className="text-2xl font-bold text-gray-900">Make Your Picks</h1>
        <p className="mt-1 text-gray-600">
          {tournament?.name} - {league?.name}
        </p>
      </div>

      {/* Selection summary */}
      <div className="bg-white rounded-lg shadow p-4 mb-6 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div>
              <span className="text-sm text-gray-500">Selected</span>
              <div className="text-lg font-semibold">
                {selectedPlayerIds.length} / {maxPicks}
              </div>
            </div>
            {useSalaryCap && (
              <div>
                <span className="text-sm text-gray-500">Salary</span>
                <div
                  className={`text-lg font-semibold ${
                    totalSalary > salaryCap ? 'text-red-600' : 'text-gray-900'
                  }`}
                >
                  ${totalSalary.toLocaleString()} / ${salaryCap.toLocaleString()}
                </div>
              </div>
            )}
          </div>
          <button
            onClick={handleSubmit}
            disabled={
              selectedPlayerIds.length !== maxPicks ||
              (useSalaryCap && totalSalary > salaryCap) ||
              submitPicks.isPending
            }
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitPicks.isPending ? 'Saving...' : 'Save Picks'}
          </button>
        </div>
        {useTiers && rosterConfig?.tiers && (
          <div className="mt-3 pt-3 border-t border-gray-100 flex gap-4 text-sm">
            {rosterConfig.tiers.map((tier) => (
              <div key={tier.tier}>
                <span className="text-gray-500">Tier {tier.tier}:</span>{' '}
                <span
                  className={`font-medium ${
                    (tierCounts[tier.tier] || 0) === tier.picks_allowed
                      ? 'text-green-600'
                      : 'text-gray-900'
                  }`}
                >
                  {tierCounts[tier.tier] || 0}/{tier.picks_allowed}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {submitPicks.error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600">
            {submitPicks.error instanceof Error
              ? submitPicks.error.message
              : 'Failed to save picks. Please try again.'}
          </p>
        </div>
      )}

      {/* Filters */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Search players..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
        </div>
        {useTiers && uniqueTiers.length > 0 && (
          <div className="flex gap-2">
            <button
              onClick={() => setTierFilter(null)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                tierFilter === null
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              All
            </button>
            {uniqueTiers.map((tier) => (
              <button
                key={tier}
                onClick={() => setTierFilter(tier)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  tierFilter === tier
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Tier {tier}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Player grid */}
      {filteredPlayers.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No players found.</p>
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {filteredPlayers.map((player) => (
            <PlayerCard
              key={player.id}
              player={player}
              selected={selectedPlayerIds.includes(player.id)}
              disabled={!canSelectPlayer(player)}
              onSelect={() => handleSelectPlayer(player.id)}
            />
          ))}
        </div>
      )}
    </div>
  )
}
