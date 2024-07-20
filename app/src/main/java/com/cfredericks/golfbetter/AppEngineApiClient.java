package com.cfredericks.golfbetter;

import static com.cfredericks.golfbetter.Utils.isInteger;
import static com.cfredericks.golfbetter.Utils.optionalIter;

import android.util.Log;

import com.cfredericks.golfbetter.models.LeaderboardPlayer;
import com.cfredericks.golfbetter.models.LeaderboardPlayerRound;
import com.cfredericks.golfbetter.models.LeaderboardPlayerRoundHole;
import com.cfredericks.golfbetter.models.Tournament;
import com.cfredericks.golfbetter.models.TournamentLeaderboard;

import com.cfredericks.golfbetter.models.pga.LeaderboardV3;
import com.cfredericks.golfbetter.models.pga.Schedule;
import com.cfredericks.golfbetter.models.pga.ScorecardV3;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;

import org.json.JSONArray;
import org.json.JSONException;

import java.io.IOException;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Helpers for reading data from app engine.
 */
public class AppEngineApiClient {
  public static final String TOURNAMENT_FORMAT = "{tournament}";
  public static final String TOURNAMENTS_ENDPOINT = "https://stoked-depth-428423-j7.uc.r.appspot.com/api/v1/tournaments";
  public static final String LEADERBOARD_ENDPOINT = "https://stoked-depth-428423-j7.uc.r.appspot.com/api/v1/players?tournamentId=" + TOURNAMENT_FORMAT;
  public static final String PGA_TOURNAMENTS_ENDPOINT = "https://stoked-depth-428423-j7.uc.r.appspot.com/api/v1/pga-tournaments";
  public static final String PGA_LEADERBOARD_PLAYERS_ENDPOINT = "https://stoked-depth-428423-j7.uc.r.appspot.com/api/v1/pga-leaderboard-players?tournamentId=" + TOURNAMENT_FORMAT;
  public static final String PGA_PLAYER_SCORECARD_ENDPOINT = "https://stoked-depth-428423-j7.uc.r.appspot.com/api/v1/pga-player-scorecards?tournamentId=" + TOURNAMENT_FORMAT;

  private static final Gson GSON = new GsonBuilder().create();

  public static List<Tournament> getTournaments() {
    final JSONArray json;
    try {
      json = Utils.getJSONArrayFromURL(TOURNAMENTS_ENDPOINT);
    } catch (final IOException | JSONException e) {
      Log.e(AppEngineApiClient.class.getSimpleName(), String.format("Error reading from endpoint '%s'", TOURNAMENTS_ENDPOINT), e);
      return null;
    }

    return Tournament.allFromApiJson(json);
  }

  public static TournamentLeaderboard getLeaderboard(final int tournamentId) {
    final String endpoint = LEADERBOARD_ENDPOINT.replace(TOURNAMENT_FORMAT, Integer.toString(tournamentId));
    final TournamentLeaderboard leaderboard;
    try {
      final JSONArray playersJson = Utils.getJSONArrayFromURL(endpoint);
      leaderboard = TournamentLeaderboard.builder().players(LeaderboardPlayer.allFromApiJson(playersJson)).build();
    } catch (final IOException | JSONException e) {
      Log.e(AppEngineApiClient.class.getSimpleName(), String.format("Error reading from endpoint '%s'", endpoint), e);
      return null;
    }

    return leaderboard;
  }

  public static List<Tournament> getPgaTournaments() {
    try {
      final String jsonStr = Utils.getResponseFromURL(PGA_TOURNAMENTS_ENDPOINT, json -> json);
      final List<Schedule.Tournament> pgaTournament = GSON.fromJson(jsonStr, new TypeToken<List<Schedule.Tournament>>() {}.getType());

      // TODO: Fix to do this properly
      final LocalDate now = LocalDate.now(ZoneId.of("UTC"));
      return pgaTournament.stream()
          // TODO: Only main events for now - fix to filter and separate
          .filter(t -> t.getId().startsWith("R"))
          .map(t -> {
            final LocalDate startDate = Instant.ofEpochMilli(t.getStartDate()).atZone(ZoneId.of("UTC")).toLocalDate();
            // TODO: Fix
            final LocalDate endDate = startDate.plusDays(4);
            return Tournament.builder()
                .id(t.getId())
                .tournamentId(t.getId())
                .name(t.getTournamentName())
                .startDate(startDate)
                .endDate(endDate)
                // TODO: Fix these
                .isInProgress(!now.isBefore(startDate) && !now.isAfter(endDate))
                .isOver(now.isAfter(endDate))
                .build();
          }).collect(Collectors.toList());
    } catch (final IOException | JSONException e) {
      Log.e(AppEngineApiClient.class.getSimpleName(), String.format("Error reading from endpoint '%s'", PGA_TOURNAMENTS_ENDPOINT), e);
      return null;
    }
  }

  public static TournamentLeaderboard getPgaLeaderboard(final String tournamentId) {
    final String endpointLeaderboard = PGA_LEADERBOARD_PLAYERS_ENDPOINT.replace(TOURNAMENT_FORMAT, tournamentId);
    final List<LeaderboardV3.PlayerRowV3> leaderboardPlayers;
    try {
      final String jsonStr = Utils.getResponseFromURL(endpointLeaderboard, json -> json);
      leaderboardPlayers = GSON.fromJson(jsonStr, new TypeToken<List<LeaderboardV3.PlayerRowV3>>() {}.getType());
      leaderboardPlayers.sort(Comparator.comparingInt(LeaderboardV3.PlayerRowV3::getLeaderboardSortOrder));
    } catch (final IOException | JSONException e) {
      Log.e(AppEngineApiClient.class.getSimpleName(), String.format("Error reading from endpoint '%s'", endpointLeaderboard), e);
      return null;
    }

    final String endpointScorecard = PGA_PLAYER_SCORECARD_ENDPOINT.replace(TOURNAMENT_FORMAT, tournamentId);
    final List<ScorecardV3> playerScorecards;
    try {
      final String jsonStr = Utils.getResponseFromURL(endpointScorecard, json -> json);
      playerScorecards = GSON.fromJson(jsonStr, new TypeToken<List<ScorecardV3>>() {}.getType());
    } catch (final IOException | JSONException e) {
      Log.e(AppEngineApiClient.class.getSimpleName(), String.format("Error reading from endpoint '%s'", endpointScorecard), e);
      return null;
    }

    final Map<String, ScorecardV3> scorecardByPlayerId =
        playerScorecards.stream().collect(Collectors.toMap(x -> x.getPlayer().getId(), x -> x));

    // TODO: Fix to do this properly
    final List<LeaderboardPlayer> players = new ArrayList<>();
    for (final LeaderboardV3.PlayerRowV3 p : leaderboardPlayers) {
      if (p.getPlayer() == null || p.getPlayer().getId() == null) {
        // For example, project cut shows up as a "player row" but with null player context
        continue;
      }
      final ScorecardV3 scorecard = scorecardByPlayerId.get(p.getPlayer().getId());
      if (scorecard == null) {
        Log.i("AppEngineApiClient", "No scorecard found for: " + p.getPlayer());
        continue;
      }
      final List<LeaderboardPlayerRound> rounds = new ArrayList<>();
      for (final ScorecardV3.RoundScore roundScore : optionalIter(scorecard.getRoundScores())) {
        final List<LeaderboardPlayerRoundHole> holes = new ArrayList<>();
        for (final ScorecardV3.RoundScore.NineHoles.Hole hole : optionalIter(roundScore.getFirstNine().getHoles())) {
          holes.add(LeaderboardPlayerRoundHole.builder()
              .number(hole.getHoleNumber())
              .par(hole.getPar())
              .score(isInteger(hole.getScore()) ? Integer.parseInt(hole.getScore()) : null)
              .build());
        }
        for (final ScorecardV3.RoundScore.NineHoles.Hole hole : optionalIter(roundScore.getSecondNine().getHoles())) {
          holes.add(LeaderboardPlayerRoundHole.builder()
              .number(hole.getHoleNumber())
              .par(hole.getPar())
              .score(isInteger(hole.getScore()) ? Integer.parseInt(hole.getScore()) : null)
              .build());
        }
        rounds.add(LeaderboardPlayerRound.builder()
            .number(roundScore.getRoundNumber())
            .holes(holes)
            .build());
      }
      players.add(LeaderboardPlayer.builder()
          .name(p.getPlayer().getDisplayName())
          .rank(p.getScoringData().getPosition())
          .country(p.getPlayer().getCountry())
          .totalScore(p.getScoringData().getTotal())
          .rounds(rounds)
          .build());
    }
    return TournamentLeaderboard.builder()
        .players(players)
        .build();
  }
}
