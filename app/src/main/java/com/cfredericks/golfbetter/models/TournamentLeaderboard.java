
package com.cfredericks.golfbetter.models;

import static com.cfredericks.golfbetter.Utils.nullableArray;
import static com.cfredericks.golfbetter.Utils.parseArray;

import com.cfredericks.golfbetter.SportsDataApiClient;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.List;

import lombok.Builder;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.SneakyThrows;
import lombok.ToString;

/**
 * Represents a leaderboard, which is the API response for {@link SportsDataApiClient#LEADERBOARD_ENDPOINT}.
 */
@Getter
@Builder(toBuilder = true)
@ToString
@EqualsAndHashCode
public class TournamentLeaderboard {
  private Tournament tournament;
  private List<LeaderboardPlayer> players;

  @SneakyThrows
  public static TournamentLeaderboard fromApiJson(final JSONObject json) {
    return TournamentLeaderboard.builder()
        .tournament(Tournament.fromApiJson(json.getJSONObject("Tournament"), false))
        .players(LeaderboardPlayer.allFromApiJson(nullableArray(json, "Players")))
        .build();
  }

  public static List<TournamentLeaderboard> allFromApiJson(final JSONArray json) {
    return parseArray(json, TournamentLeaderboard::fromApiJson);
  }
}
