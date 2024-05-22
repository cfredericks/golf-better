package com.cfredericks.golfbetter.models;

import static com.cfredericks.golfbetter.Utils.nullableInt;
import static com.cfredericks.golfbetter.Utils.parseArray;

import org.json.JSONArray;
import org.json.JSONObject;

import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.UUID;

import lombok.Builder;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.SneakyThrows;
import lombok.ToString;

/**
 * Represents information about a hole from a player's round, which is a subfield in {@link LeaderboardPlayerRound}.
 */
@Getter
@Builder(toBuilder = true)
@ToString
@EqualsAndHashCode
public class LeaderboardPlayerRoundHole {
  private UUID id;
  private Integer playerRoundId;
  private Integer number;

  private Integer par;
  private Integer score;
  private Integer toPar;

  private Boolean holeInOne;
  private Boolean doubleEagle;
  private Boolean eagle;
  private Boolean birdie;
  private Boolean isPar;
  private Boolean bogey;
  private Boolean doubleBogey;
  private Boolean worseThanDoubleBogey;

  @SneakyThrows
  public static LeaderboardPlayerRoundHole fromApiJson(final JSONObject json) {
    final int playerRoundId = json.getInt("PlayerRoundID");
    final int number = json.getInt("Number");
    return LeaderboardPlayerRoundHole.builder()
        .id(UUID.nameUUIDFromBytes((playerRoundId + "|" + number).getBytes(StandardCharsets.UTF_8)))
        .playerRoundId(playerRoundId)
        .number(number)
        .par(json.getInt("Par"))
        // TODO: are some of these fields actually nullable, or is that just the randomized test data?
        .score(nullableInt(json, "Score"))
        .toPar(nullableInt(json, "ToPar"))
        .holeInOne(json.getBoolean("HoleInOne"))
        .doubleEagle(json.getBoolean("DoubleEagle"))
        .eagle(json.getBoolean("Eagle"))
        .birdie(json.getBoolean("Birdie"))
        .isPar(json.getBoolean("IsPar"))
        .bogey(json.getBoolean("Bogey"))
        .doubleBogey(json.getBoolean("DoubleBogey"))
        .worseThanDoubleBogey(json.getBoolean("WorseThanDoubleBogey"))
        .build();
  }

  public static List<LeaderboardPlayerRoundHole> allFromApiJson(final JSONArray json) {
    return parseArray(json, LeaderboardPlayerRoundHole::fromApiJson);
  }
}
