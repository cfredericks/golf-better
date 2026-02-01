import { getIdToken } from './auth';
import type {
  Tournament,
  LeaderboardPlayer,
  PlayerScorecard,
  League,
  LeagueMember,
  TournamentPick,
  FantasyScore,
  LeagueStanding,
  AvailablePlayer,
  Favorite,
  LeagueInvitation,
  RosterConfig,
  ScoringConfig,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';
const API_PREFIX = '/api/v1';

async function fetchWithAuth<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getIdToken();
  if (!token) {
    throw new Error('Not authenticated');
  }

  const url = `${API_BASE_URL}${API_PREFIX}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `HTTP ${response.status}`);
  }

  return response.json();
}

// Tournament endpoints
export const getTournaments = async (id?: string): Promise<Tournament[]> => {
  const params = id ? `?id=${id}` : '';
  return fetchWithAuth<Tournament[]>(`/pga-tournaments${params}`);
};

export const getTournament = async (id: string): Promise<Tournament> => {
  const tournaments = await getTournaments(id);
  if (tournaments.length === 0) {
    throw new Error('Tournament not found');
  }
  return tournaments[0];
};

// Leaderboard endpoints
export const getLeaderboardPlayers = async (
  tournamentId?: string,
  playerId?: string
): Promise<LeaderboardPlayer[]> => {
  const params = new URLSearchParams();
  if (tournamentId) params.append('tournamentId', tournamentId);
  if (playerId) params.append('id', playerId);
  const queryString = params.toString();
  return fetchWithAuth<LeaderboardPlayer[]>(
    `/pga-leaderboard-players${queryString ? `?${queryString}` : ''}`
  );
};

// Scorecard endpoints
export const getPlayerScorecards = async (
  tournamentId?: string,
  playerId?: string
): Promise<PlayerScorecard[]> => {
  const params = new URLSearchParams();
  if (tournamentId) params.append('tournamentId', tournamentId);
  if (playerId) params.append('id', playerId);
  const queryString = params.toString();
  return fetchWithAuth<PlayerScorecard[]>(
    `/pga-player-scorecards${queryString ? `?${queryString}` : ''}`
  );
};

// User registration
export const registerUser = async (user: {
  id: string;
  email: string;
  name: string;
}): Promise<void> => {
  await fetchWithAuth('/users', {
    method: 'POST',
    body: JSON.stringify(user),
  });
};

// League endpoints
export const getLeagues = async (): Promise<League[]> => {
  return fetchWithAuth<League[]>('/leagues');
};

export const getLeague = async (id: string): Promise<League> => {
  return fetchWithAuth<League>(`/leagues/${id}`);
};

export const createLeague = async (league: {
  name: string;
  leagueType: 'season' | 'tournament';
  tournamentId?: string;
  rosterConfig: RosterConfig;
  scoringConfig: ScoringConfig;
  pickDeadlineType: string;
  isPublic: boolean;
}): Promise<League> => {
  return fetchWithAuth<League>('/leagues', {
    method: 'POST',
    body: JSON.stringify(league),
  });
};

export const updateLeague = async (
  id: string,
  updates: Partial<League>
): Promise<League> => {
  return fetchWithAuth<League>(`/leagues/${id}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  });
};

export const joinLeague = async (
  leagueId: string,
  inviteCode: string
): Promise<LeagueMember> => {
  return fetchWithAuth<LeagueMember>(`/leagues/${leagueId}/join`, {
    method: 'POST',
    body: JSON.stringify({ inviteCode }),
  });
};

export const inviteToLeague = async (
  leagueId: string,
  email: string
): Promise<LeagueInvitation> => {
  return fetchWithAuth<LeagueInvitation>(`/leagues/${leagueId}/invite`, {
    method: 'POST',
    body: JSON.stringify({ email }),
  });
};

export const getLeagueMembers = async (leagueId: string): Promise<LeagueMember[]> => {
  return fetchWithAuth<LeagueMember[]>(`/leagues/${leagueId}/members`);
};

// Pick endpoints
export const getPicks = async (
  leagueId: string,
  tournamentId?: string
): Promise<TournamentPick[]> => {
  const params = tournamentId ? `?tournamentId=${tournamentId}` : '';
  return fetchWithAuth<TournamentPick[]>(`/leagues/${leagueId}/picks${params}`);
};

export const submitPicks = async (
  leagueId: string,
  tournamentId: string,
  playerIds: string[]
): Promise<TournamentPick[]> => {
  return fetchWithAuth<TournamentPick[]>(`/leagues/${leagueId}/picks`, {
    method: 'POST',
    body: JSON.stringify({ tournamentId, playerIds }),
  });
};

export const getAvailablePlayers = async (
  leagueId: string,
  tournamentId: string
): Promise<AvailablePlayer[]> => {
  return fetchWithAuth<AvailablePlayer[]>(
    `/leagues/${leagueId}/picks/${tournamentId}/available-players`
  );
};

// Standings and scoring endpoints
export const getLeagueStandings = async (leagueId: string): Promise<LeagueStanding[]> => {
  return fetchWithAuth<LeagueStanding[]>(`/leagues/${leagueId}/standings`);
};

export const getTournamentScoring = async (
  leagueId: string,
  tournamentId: string
): Promise<FantasyScore[]> => {
  return fetchWithAuth<FantasyScore[]>(
    `/leagues/${leagueId}/scoring/${tournamentId}`
  );
};

// Favorites endpoints
export const getFavorites = async (): Promise<Favorite[]> => {
  return fetchWithAuth<Favorite[]>('/favorites');
};

export const addFavorite = async (
  favoriteType: 'player' | 'tournament',
  targetId: string
): Promise<Favorite> => {
  return fetchWithAuth<Favorite>('/favorites', {
    method: 'POST',
    body: JSON.stringify({ favoriteType, targetId }),
  });
};

export const removeFavorite = async (id: string): Promise<void> => {
  await fetchWithAuth(`/favorites/${id}`, {
    method: 'DELETE',
  });
};

// Invitation endpoints
export const getInvitations = async (): Promise<LeagueInvitation[]> => {
  return fetchWithAuth<LeagueInvitation[]>('/invitations');
};

export const respondToInvitation = async (
  id: string,
  accept: boolean
): Promise<void> => {
  await fetchWithAuth(`/invitations/${id}`, {
    method: 'POST',
    body: JSON.stringify({ accept }),
  });
};
