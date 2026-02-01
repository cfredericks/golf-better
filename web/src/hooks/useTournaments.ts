import { useQuery } from '@tanstack/react-query';
import { getTournaments, getTournament, getLeaderboardPlayers, getPlayerScorecards } from '../services/api';

export function useTournaments() {
  return useQuery({
    queryKey: ['tournaments'],
    queryFn: () => getTournaments(),
  });
}

export function useTournament(id: string) {
  return useQuery({
    queryKey: ['tournament', id],
    queryFn: () => getTournament(id),
    enabled: !!id,
  });
}

export function useLeaderboard(tournamentId: string) {
  return useQuery({
    queryKey: ['leaderboard', tournamentId],
    queryFn: () => getLeaderboardPlayers(tournamentId),
    enabled: !!tournamentId,
  });
}

export function usePlayerScorecard(tournamentId: string, playerId: string) {
  return useQuery({
    queryKey: ['scorecard', tournamentId, playerId],
    queryFn: () => getPlayerScorecards(tournamentId, playerId),
    enabled: !!tournamentId && !!playerId,
  });
}
