package com.cfredericks.golfbetter.clients;

/**
 * Helpers for reading data from app engine.
 */
// TODO: Use GSON
public class SportsDataIoAppEngineClient {
  public static final String TOURNAMENT_FORMAT = "{tournament}";
   public static final String TOURNAMENTS_ENDPOINT = "https://stoked-depth-428423-j7.uc.r.appspot.com/api/v1/tournaments";
   public static final String LEADERBOARD_ENDPOINT = "https://stoked-depth-428423-j7.uc.r.appspot.com/api/v1/players?tournamentId=" + TOURNAMENT_FORMAT;

//  public static List<Tournament> getTournaments() {
//    final JSONArray json;
//    try {
//      json = Utils.getJSONArrayFromURL(TOURNAMENTS_ENDPOINT);
//    } catch (final IOException | JSONException e) {
//      Log.e(SportsDataIoAppEngineClient.class.getSimpleName(), String.format("Error reading from endpoint '%s'", TOURNAMENTS_ENDPOINT), e);
//      return null;
//    }
//
//    return Tournament.allFromApiJson(json);
//  }
//
//  public static TournamentLeaderboard getLeaderboard(final int tournamentId) {
//    final String endpoint = LEADERBOARD_ENDPOINT.replace(TOURNAMENT_FORMAT, Integer.toString(tournamentId));
//    final TournamentLeaderboard leaderboard;
//    try {
//      final JSONArray playersJson = Utils.getJSONArrayFromURL(endpoint);
//      leaderboard = TournamentLeaderboard.builder().players(LeaderboardPlayer.allFromApiJson(playersJson)).build();
//    } catch (final IOException | JSONException e) {
//      Log.e(SportsDataIoAppEngineClient.class.getSimpleName(), String.format("Error reading from endpoint '%s'", endpoint), e);
//      return null;
//    }
//
//    return leaderboard;
//  }
}
