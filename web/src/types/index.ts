// Tournament types
export interface Tournament {
  id: string;
  name: string;
  startDate: string;
  endDate: string;
  courseName: string;
  city: string;
  state: string;
  country: string;
  isCompleted: boolean;
  purse?: number;
  winnerId?: string;
  winnerName?: string;
}

// Leaderboard types
export interface LeaderboardPlayer {
  id: string;
  tournamentId: string;
  playerId: string;
  playerName: string;
  position: number;
  positionDisplay: string;
  totalScore: number;
  totalScoreDisplay: string;
  thru: string;
  roundScores: number[];
  isAmateur: boolean;
}

// Scorecard types
export interface ScorecardHole {
  holeNumber: number;
  par: number;
  score: number;
  scoreToPar: number;
}

export interface ScorecardRound {
  roundNumber: number;
  holes: ScorecardHole[];
  totalScore: number;
  totalScoreToPar: number;
}

export interface PlayerScorecard {
  id: string;
  tournamentId: string;
  playerId: string;
  playerName: string;
  rounds: ScorecardRound[];
}

// User types
export interface User {
  id: string;
  email: string;
  name: string;
  photoUrl?: string;
}

// League types
export type LeagueType = 'season' | 'tournament';
export type MemberRole = 'owner' | 'admin' | 'member';
export type PickDeadlineType = 'tournament_start' | 'first_tee_time' | 'custom';

export interface RosterConfig {
  roster_size: number;
  use_tiers: boolean;
  tiers?: TierConfig[];
  use_salary_cap: boolean;
  salary_cap?: number;
}

export interface TierConfig {
  tier: number;
  name: string;
  picks_allowed: number;
}

export interface ScoringConfig {
  eagle_or_better: number;
  birdie: number;
  par: number;
  bogey: number;
  double_bogey_or_worse: number;
  streak_bonus_3: number;
  streak_bonus_5: number;
  bounce_back: number;
  bogey_free_round: number;
  position_1: number;
  position_2: number;
  position_3: number;
  position_4?: number;
  position_5?: number;
  position_6_10?: number;
  position_11_20?: number;
  position_21_30?: number;
  made_cut?: number;
}

export interface League {
  id: string;
  name: string;
  ownerId: string;
  ownerName?: string;
  leagueType: LeagueType;
  tournamentId?: string;
  rosterConfig: RosterConfig;
  scoringConfig: ScoringConfig;
  pickDeadlineType: PickDeadlineType;
  inviteCode?: string;
  isPublic: boolean;
  created: string;
  memberCount?: number;
}

export interface LeagueMember {
  id: string;
  leagueId: string;
  userId: string;
  userName: string;
  role: MemberRole;
  joinedAt: string;
}

export interface TournamentPick {
  id: string;
  leagueId: string;
  userId: string;
  tournamentId: string;
  playerId: string;
  playerName?: string;
  tier?: number;
  salary?: number;
  pickedAt: string;
}

export interface PlayerScore {
  playerId: string;
  playerName: string;
  score: number;
  breakdown: ScoreBreakdown;
}

export interface ScoreBreakdown {
  eagles: number;
  birdies: number;
  pars: number;
  bogeys: number;
  doubleBogeys: number;
  streakBonus: number;
  bounceBack: number;
  bogeyFreeRounds: number;
  positionBonus: number;
}

export interface FantasyScore {
  id: string;
  leagueId: string;
  userId: string;
  userName: string;
  tournamentId: string;
  playerScores: PlayerScore[];
  totalScore: number;
  rank: number;
  calculatedAt: string;
}

export interface LeagueStanding {
  userId: string;
  userName: string;
  totalScore: number;
  tournamentScores: { tournamentId: string; score: number }[];
  rank: number;
}

export interface AvailablePlayer {
  id: string;
  name: string;
  tier?: number;
  salary?: number;
  worldRanking?: number;
  recentForm?: string;
}

// Favorites
export type FavoriteType = 'player' | 'tournament';

export interface Favorite {
  id: string;
  userId: string;
  favoriteType: FavoriteType;
  targetId: string;
}

// League invitation
export interface LeagueInvitation {
  id: string;
  leagueId: string;
  leagueName?: string;
  invitedEmail: string;
  invitedBy: string;
  invitedByName?: string;
  status: 'pending' | 'accepted' | 'declined' | 'expired';
  expiresAt: string;
}

// API response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
}
