package com.cfredericks.golfbetter;

import android.util.Log;

import com.cfredericks.golfbetter.models.Tournament;
import com.cfredericks.golfbetter.models.TournamentLeaderboard;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.List;

/**
 * Helpers for querying the api.sportsdata.io API endpoints.
 */
// TODO: Separate API and parsing code from UI code
public class SportsDataApiClient {
  // TODO: Allow passing this in or looking it up
  private static final String API_KEY = "";

  public static final String TOURNAMENT_FORMAT = "{tournament}";
  public static final String TOURNAMENTS_ENDPOINT = "https://api.sportsdata.io/golf/v2/json/Tournaments";
  public static final String LEADERBOARD_ENDPOINT = "https://api.sportsdata.io/golf/v2/json/Leaderboard/" + TOURNAMENT_FORMAT;

  public static List<Tournament> getTournaments() {
    final JSONArray json;
    try {
      json = Utils.getJSONArrayFromURL(TOURNAMENTS_ENDPOINT + "?key=" + API_KEY);
    } catch (final IOException | JSONException e) {
      Log.e(SportsDataApiClient.class.getSimpleName(), String.format("Error reading from endpoint '%s'", TOURNAMENTS_ENDPOINT), e);
      return null;
    }

    return Tournament.allFromApiJson(json);
  }

  public static TournamentLeaderboard getLeaderboard(final int tournamentId) {
    final String endpoint = LEADERBOARD_ENDPOINT.replace(TOURNAMENT_FORMAT, Integer.toString(tournamentId));
    final JSONObject json;
    try {
      json = Utils.getJSONObjectFromURL(endpoint + "?key=" + API_KEY);
    } catch (final IOException | JSONException e) {
      Log.e(SportsDataApiClient.class.getSimpleName(), String.format("Error reading from endpoint '%s'", endpoint), e);
      return null;
    }

    return TournamentLeaderboard.fromApiJson(json);
  }
}
