import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getLeagues,
  getLeague,
  createLeague,
  updateLeague,
  joinLeague,
  inviteToLeague,
  getLeagueMembers,
  getPicks,
  submitPicks,
  getAvailablePlayers,
  getLeagueStandings,
  getTournamentScoring,
} from '../services/api';
import type { League, RosterConfig, ScoringConfig } from '../types';

export function useLeagues() {
  return useQuery({
    queryKey: ['leagues'],
    queryFn: getLeagues,
  });
}

export function useLeague(id: string) {
  return useQuery({
    queryKey: ['league', id],
    queryFn: () => getLeague(id),
    enabled: !!id,
  });
}

export function useLeagueMembers(leagueId: string) {
  return useQuery({
    queryKey: ['league-members', leagueId],
    queryFn: () => getLeagueMembers(leagueId),
    enabled: !!leagueId,
  });
}

export function useCreateLeague() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (league: {
      name: string;
      leagueType: 'season' | 'tournament';
      tournamentId?: string;
      rosterConfig: RosterConfig;
      scoringConfig: ScoringConfig;
      pickDeadlineType: string;
      isPublic: boolean;
    }) => createLeague(league),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leagues'] });
    },
  });
}

export function useUpdateLeague() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: Partial<League> }) =>
      updateLeague(id, updates),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['league', id] });
      queryClient.invalidateQueries({ queryKey: ['leagues'] });
    },
  });
}

export function useJoinLeague() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ leagueId, inviteCode }: { leagueId: string; inviteCode: string }) =>
      joinLeague(leagueId, inviteCode),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leagues'] });
    },
  });
}

export function useInviteToLeague() {
  return useMutation({
    mutationFn: ({ leagueId, email }: { leagueId: string; email: string }) =>
      inviteToLeague(leagueId, email),
  });
}

export function usePicks(leagueId: string, tournamentId?: string) {
  return useQuery({
    queryKey: ['picks', leagueId, tournamentId],
    queryFn: () => getPicks(leagueId, tournamentId),
    enabled: !!leagueId,
  });
}

export function useSubmitPicks() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      leagueId,
      tournamentId,
      playerIds,
    }: {
      leagueId: string;
      tournamentId: string;
      playerIds: string[];
    }) => submitPicks(leagueId, tournamentId, playerIds),
    onSuccess: (_, { leagueId, tournamentId }) => {
      queryClient.invalidateQueries({ queryKey: ['picks', leagueId, tournamentId] });
    },
  });
}

export function useAvailablePlayers(leagueId: string, tournamentId: string) {
  return useQuery({
    queryKey: ['available-players', leagueId, tournamentId],
    queryFn: () => getAvailablePlayers(leagueId, tournamentId),
    enabled: !!leagueId && !!tournamentId,
  });
}

export function useLeagueStandings(leagueId: string) {
  return useQuery({
    queryKey: ['standings', leagueId],
    queryFn: () => getLeagueStandings(leagueId),
    enabled: !!leagueId,
  });
}

export function useTournamentScoring(leagueId: string, tournamentId: string) {
  return useQuery({
    queryKey: ['scoring', leagueId, tournamentId],
    queryFn: () => getTournamentScoring(leagueId, tournamentId),
    enabled: !!leagueId && !!tournamentId,
  });
}
