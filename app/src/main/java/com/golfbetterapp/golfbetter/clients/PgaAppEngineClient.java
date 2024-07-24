package com.golfbetterapp.golfbetter.clients;

import static com.golfbetterapp.golfbetter.Utils.optionalIter;
import static com.golfbetterapp.golfbetter.Utils.parseScore;

import android.util.Log;

import com.golfbetterapp.golfbetter.Utils;
import com.golfbetterapp.golfbetter.models.LeaderboardPlayerRound;
import com.golfbetterapp.golfbetter.models.LeaderboardPlayerRoundHole;
import com.golfbetterapp.golfbetter.models.Player;
import com.golfbetterapp.golfbetter.models.Tournament;
import com.golfbetterapp.golfbetter.models.TournamentLeaderboard;
import com.golfbetterapp.golfbetter.models.pga.LeaderboardV3;
import com.golfbetterapp.golfbetter.models.pga.Schedule;
import com.golfbetterapp.golfbetter.models.pga.ScorecardV3;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;

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
public class PgaAppEngineClient {
  public static final String TOURNAMENT_FORMAT = "{tournament}";
  public static final String TOURNAMENTS_ENDPOINT = "https://stoked-depth-428423-j7.uc.r.appspot.com/api/v1/pga-tournaments";
  public static final String LEADERBOARD_PLAYERS_ENDPOINT = "https://stoked-depth-428423-j7.uc.r.appspot.com/api/v1/pga-leaderboard-players?tournamentId=" + TOURNAMENT_FORMAT;
  public static final String PLAYER_SCORECARD_ENDPOINT = "https://stoked-depth-428423-j7.uc.r.appspot.com/api/v1/pga-player-scorecards?tournamentId=" + TOURNAMENT_FORMAT;

  private static final Gson GSON = new GsonBuilder().create();

  public static List<Tournament> getTournaments() {
    try {
      final String jsonStr = Utils.getResponseFromURL(TOURNAMENTS_ENDPOINT, json -> json);
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
                .name(t.getTournamentName())
                .startDate(startDate)
                .purse(t.getPurse())
                .city(t.getCity())
                .state(t.getState())
                .country(t.getCountry())
                .courseName(t.getCourseName())
                .status(t.getStatus())
                // TODO: Fix these
                .endDate(endDate)
                .isInProgress(!now.isBefore(startDate) && !now.isAfter(endDate))
                .isOver(now.isAfter(endDate))
                .build();
          }).collect(Collectors.toList());
    } catch (final IOException | JSONException e) {
      Log.e(PgaAppEngineClient.class.getSimpleName(), String.format("Error reading from endpoint '%s'", TOURNAMENTS_ENDPOINT), e);
      return null;
    }
  }

  public static TournamentLeaderboard getLeaderboard(final String tournamentId) {
    final String endpointLeaderboard = LEADERBOARD_PLAYERS_ENDPOINT.replace(TOURNAMENT_FORMAT, tournamentId);
    final List<LeaderboardV3.PlayerRowV3> leaderboardPlayers;
    try {
      final String jsonStr = Utils.getResponseFromURL(endpointLeaderboard, json -> json);
      leaderboardPlayers = GSON.fromJson(jsonStr, new TypeToken<List<LeaderboardV3.PlayerRowV3>>() {}.getType());
      leaderboardPlayers.sort(Comparator.comparingInt(LeaderboardV3.PlayerRowV3::getLeaderboardSortOrder));
    } catch (final IOException | JSONException e) {
      Log.e(PgaAppEngineClient.class.getSimpleName(), String.format("Error reading from endpoint '%s'", endpointLeaderboard), e);
      return null;
    }

    final String endpointScorecard = PLAYER_SCORECARD_ENDPOINT.replace(TOURNAMENT_FORMAT, tournamentId);
    final List<ScorecardV3> playerScorecards;
    try {
      final String jsonStr = Utils.getResponseFromURL(endpointScorecard, json -> json);
      playerScorecards = GSON.fromJson(jsonStr, new TypeToken<List<ScorecardV3>>() {}.getType());
    } catch (final IOException | JSONException e) {
      Log.e(PgaAppEngineClient.class.getSimpleName(), String.format("Error reading from endpoint '%s'", endpointScorecard), e);
      return null;
    }

    final Map<String, ScorecardV3> scorecardByPlayerId =
        playerScorecards.stream().collect(Collectors.toMap(x -> x.getPlayer().getId(), x -> x));

    // TODO: Fix to do this properly
    final List<Player> players = new ArrayList<>();
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
        // TODO: Concatenate iterables for DRY-ness
        for (final ScorecardV3.RoundScore.NineHoles.Hole hole : optionalIter(roundScore.getFirstNine().getHoles())) {
          final Integer score = parseScore(hole.getScore());
          holes.add(LeaderboardPlayerRoundHole.builder()
              .tournamentId(tournamentId)
              .playerId(p.getPlayer().getId())
              .number(hole.getHoleNumber())
              .status(hole.getStatus())
              .par(hole.getPar())
              .yardage(hole.getYardage())
              .score(score)
              .toPar(score != null ? score - hole.getPar() : null)
              .build());
        }
        for (final ScorecardV3.RoundScore.NineHoles.Hole hole : optionalIter(roundScore.getSecondNine().getHoles())) {
          final Integer score = parseScore(hole.getScore());
          holes.add(LeaderboardPlayerRoundHole.builder()
              .tournamentId(tournamentId)
              .playerId(p.getPlayer().getId())
              .number(hole.getHoleNumber())
              .status(hole.getStatus())
              .par(hole.getPar())
              .yardage(hole.getYardage())
              .score(score)
              .toPar(score != null ? score - hole.getPar() : null)
              .build());
        }
        rounds.add(LeaderboardPlayerRound.builder()
            .tournamentId(tournamentId)
            .playerId(p.getPlayer().getId())
            .number(roundScore.getRoundNumber())
            .par(roundScore.getParTotal())
            .score(parseScore(roundScore.getTotal()))
            .toPar(parseScore(roundScore.getScoreToPar()))
            .holes(holes)
            // TODO: Populate these
            // .backNineStart(roundScore.)
            // .teeTime(roundScore.)
            // .day(roundScore.)
            .build());
      }
      players.add(Player.builder()
          .id(p.getId())
          .tournamentId(tournamentId)
          .name(p.getPlayer().getDisplayName())
          .rank(p.getScoringData().getPosition())
          .country(p.getPlayer().getCountry())
          .totalScore(parseScore(p.getScoringData().getTotal()))
          .totalStrokes(parseScore(p.getScoringData().getTotalStrokes()))
          .totalThrough(p.getScoringData().getThru())
          .rounds(rounds)
          .build());
    }
    return TournamentLeaderboard.builder()
        .players(players)
        // TODO: populate these
        // .tournament(Tournament.builder().build())
        .build();
  }
}
