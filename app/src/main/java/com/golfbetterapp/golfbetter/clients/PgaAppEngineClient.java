package com.golfbetterapp.golfbetter.clients;

import static com.golfbetterapp.golfbetter.Utils.optionalIter;
import static com.golfbetterapp.golfbetter.Utils.parseScore;

import android.content.Context;
import android.util.Log;

import com.golfbetterapp.golfbetter.Utils;
import com.golfbetterapp.golfbetter.models.LeaderboardPlayerRound;
import com.golfbetterapp.golfbetter.models.LeaderboardPlayerRoundHole;
import com.golfbetterapp.golfbetter.models.Player;
import com.golfbetterapp.golfbetter.models.Tournament;
import com.golfbetterapp.golfbetter.models.TournamentLeaderboard;
import com.golfbetterapp.golfbetter.models.User;
import com.golfbetterapp.golfbetter.models.pga.LeaderboardV3;
import com.golfbetterapp.golfbetter.models.pga.Schedule;
import com.golfbetterapp.golfbetter.models.pga.ScorecardV3;
import com.google.firebase.auth.FirebaseAuth;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;

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

  public static final String APP_SERVER_URL = "https://stoked-depth-428423-j7.uc.r.appspot.com";
  // public static final String APP_SERVER_URL = "http://10.0.2.2:8080"; // For local dev
  public static final String TOURNAMENTS_ENDPOINT = APP_SERVER_URL + "/api/v1/pga-tournaments";
  public static final String LEADERBOARD_PLAYERS_ENDPOINT = APP_SERVER_URL + "/api/v1/pga-leaderboard-players?tournamentId=" + TOURNAMENT_FORMAT;
  public static final String PLAYER_SCORECARD_ENDPOINT = APP_SERVER_URL + "/api/v1/pga-player-scorecards?tournamentId=" + TOURNAMENT_FORMAT;
  public static final String USERS_ENDPOINT = APP_SERVER_URL + "/api/v1/users";

  private static final Gson GSON = new GsonBuilder().create();

  public static void getTournaments(final Context context, final Utils.ApiCallback<List<Tournament>> callback) {
      Utils.getResponseFromURL(context, TOURNAMENTS_ENDPOINT, json -> json, true, new Utils.ApiCallback<String>() {
        @Override
        public void onSuccess(final String result) {
          try {
            final List<Schedule.Tournament> pgaTournament = GSON.fromJson(result, new TypeToken<List<Schedule.Tournament>>() {
            }.getType());

            // TODO: Fix to do this properly
            final LocalDate now = LocalDate.now(ZoneId.of("UTC"));
            callback.onSuccess(pgaTournament.stream()
                // TODO: Only main events for now - fix to filter and separate
                .filter(t -> t.getId().startsWith("R")).map(t -> {
                  final LocalDate startDate = Instant.ofEpochMilli(t.getStartDate()).atZone(ZoneId.of("UTC")).toLocalDate();
                  // TODO: Fix
                  final LocalDate endDate = startDate.plusDays(4);
                  return Tournament.builder().id(t.getId()).name(t.getTournamentName()).startDate(startDate).purse(t.getPurse()).city(t.getCity()).state(t.getState()).country(t.getCountry()).courseName(t.getCourseName()).status(t.getStatus())
                      // TODO: Fix these
                      .endDate(endDate).isInProgress(!now.isBefore(startDate) && !now.isAfter(endDate)).isOver(now.isAfter(endDate)).build();
                }).collect(Collectors.toList()));
          } catch (final Exception e) {
            callback.onFailure(e);
          }
        }

        @Override
        public void onFailure(final Exception e) {
          callback.onFailure(e);
        }
      });
  }

  public static void getLeaderboard(final String tournamentId, final Context context, final Utils.ApiCallback<TournamentLeaderboard> callback) {
    final String endpointLeaderboard = LEADERBOARD_PLAYERS_ENDPOINT.replace(TOURNAMENT_FORMAT, tournamentId);
    Utils.getResponseFromURL(context, endpointLeaderboard, json -> json, true, new Utils.ApiCallback<String>() {
      @Override
      public void onSuccess(final String result) {
        final List<LeaderboardV3.PlayerRowV3> leaderboardPlayers;
        try {
          leaderboardPlayers = GSON.fromJson(result, new TypeToken<List<LeaderboardV3.PlayerRowV3>>() {}.getType());
        } catch (final Exception e) {
          onFailure(e);
          return;
        }
        leaderboardPlayers.sort(Comparator.comparingInt(LeaderboardV3.PlayerRowV3::getLeaderboardSortOrder));

        final String endpointScorecard = PLAYER_SCORECARD_ENDPOINT.replace(TOURNAMENT_FORMAT, tournamentId);
        Utils.getResponseFromURL(context, endpointScorecard, json -> json, true, new Utils.ApiCallback<String>() {
          @Override
          public void onSuccess(final String result) {
            final List<ScorecardV3> playerScorecards;
            try {
              playerScorecards = GSON.fromJson(result, new TypeToken<List<ScorecardV3>>() {}.getType());
            } catch (final Exception e) {
              onFailure(e);
              return;
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
            callback.onSuccess(TournamentLeaderboard.builder()
                .players(players)
                // TODO: populate these
                // .tournament(Tournament.builder().build())
                .build());
          }

          @Override
          public void onFailure(final Exception e) {
            onFailure(e);
          }
        });
      }

      @Override
      public void onFailure(final Exception e) {
        callback.onFailure(e);
      }
    });
  }

  public static void updateUser(final Context context, final Utils.ApiCallback<Void> callback) {
    final String userId = FirebaseAuth.getInstance().getCurrentUser().getUid();
    final String name = FirebaseAuth.getInstance().getCurrentUser().getDisplayName();
    final String email = FirebaseAuth.getInstance().getCurrentUser().getEmail();
    Utils.postToURL(context, USERS_ENDPOINT, GSON.toJson(User.builder().id(userId).name(name).email(email).build()), null, true, new Utils.ApiCallback<String>() {
      @Override
      public void onSuccess(final String result) {
        // do nothing
      }

      @Override
      public void onFailure(final Exception e) {
        callback.onFailure(e);
      }
    });
  }
}
