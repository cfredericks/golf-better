package com.cfredericks.golfbetter.models.sportsdataio;

import static com.cfredericks.golfbetter.Utils.nullableBool;
import static com.cfredericks.golfbetter.Utils.nullableInt;
import static com.cfredericks.golfbetter.Utils.nullableStr;
import static com.cfredericks.golfbetter.Utils.parseArray;
import static com.cfredericks.golfbetter.Utils.parseDate;
import static com.cfredericks.golfbetter.Utils.parseTime;

import org.json.JSONArray;
import org.json.JSONObject;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

import lombok.Builder;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.SneakyThrows;
import lombok.ToString;

/**
 * Represents information about a player's round, which is a subfield in {@link LeaderboardPlayer}.
 */
@Getter
@Builder(toBuilder = true)
@ToString
@EqualsAndHashCode
public class LeaderboardPlayerRound {
  private UUID id;
  private Integer playerRoundId;
  private Integer playerTournamentId;
  private Integer number;
  private LocalDate day;
  private Instant teeTime;
  private Boolean backNineStart;  // TODO: is this a boolean?

  private Integer par;
  private Integer score;
  private Boolean bogeyFree;
  private Integer doubleEagles;
  private Integer eagles;
  private Integer birdies;
  private Integer pars;
  private Integer bogeys;
  private Integer doubleBogeys;
  private Integer tripleBogeys;
  private Integer worseThanDoubleBogey;
  private Integer worseThanTripleBogey;
  private Integer holeInOnes;

  // TODO: why are these a double and not an int?
  private Double longestBirdieOrBetterStreak;
  private Double consecutiveBirdieOrBetterCount;
  private Double bounceBackCount;

  private Boolean includesFiveOrMoreBirdiesOrBetter;
  private Boolean includesStreakOfThreeBirdiesOrBetter;
  private Boolean includesStreakOfFourBirdiesOrBetter;
  private Boolean includesStreakOfFiveBirdiesOrBetter;
  private Boolean includesStreakOfSixBirdiesOrBetter;

  private List<LeaderboardPlayerRoundHole> holes;

  @SneakyThrows
  public static LeaderboardPlayerRound fromApiJson(final JSONObject json) {
    final int playerRoundId = json.getInt("PlayerRoundID");
    final int playerTournamentId = json.getInt("PlayerTournamentID");
    final String dayStr = nullableStr(json, "Day");
    final String teeTimeStr = nullableStr(json, "TeeTime");
    return LeaderboardPlayerRound.builder()
        .id(UUID.nameUUIDFromBytes((playerRoundId + "|" + playerTournamentId).getBytes(StandardCharsets.UTF_8)))
        .playerRoundId(playerRoundId)
        .playerTournamentId(playerTournamentId)
        .number(json.getInt("Number"))
        .day(parseDate(dayStr))
        .teeTime(parseTime(teeTimeStr))
        // TODO: are some of these fields actually nullable, or is that just the randomized test data?
        .backNineStart(nullableBool(json, "BackNineStart"))
        .par(json.getInt("Par"))
        .score(nullableInt(json, "Score"))
        .bogeyFree(nullableBool(json, "BogeyFree"))
        .doubleEagles(json.getInt("DoubleEagles"))
        .eagles(json.getInt("Eagles"))
        .birdies(json.getInt("Birdies"))
        .pars(json.getInt("Pars"))
        .bogeys(json.getInt("Bogeys"))
        .doubleBogeys(json.getInt("DoubleBogeys"))
        .tripleBogeys(json.getInt("TripleBogeys"))
        .worseThanDoubleBogey(json.getInt("WorseThanDoubleBogey"))
        .worseThanTripleBogey(json.getInt("WorseThanTripleBogey"))
        .holeInOnes(json.getInt("HoleInOnes"))
        .longestBirdieOrBetterStreak(json.getDouble("LongestBirdieOrBetterStreak"))
        .consecutiveBirdieOrBetterCount(json.getDouble("ConsecutiveBirdieOrBetterCount"))
        .bounceBackCount(json.getDouble("BounceBackCount"))
        .includesFiveOrMoreBirdiesOrBetter(json.getBoolean("IncludesFiveOrMoreBirdiesOrBetter"))
        .includesStreakOfThreeBirdiesOrBetter(json.getBoolean("IncludesStreakOfThreeBirdiesOrBetter"))
        .includesStreakOfFourBirdiesOrBetter(json.getBoolean("IncludesStreakOfFourBirdiesOrBetter"))
        .includesStreakOfFiveBirdiesOrBetter(json.getBoolean("IncludesStreakOfFiveBirdiesOrBetter"))
        .includesStreakOfSixBirdiesOrBetter(json.getBoolean("IncludesStreakOfSixBirdiesOrBetter"))
        .holes(LeaderboardPlayerRoundHole.allFromApiJson(json.getJSONArray("Holes")))
        .build();
  }

  public static List<LeaderboardPlayerRound> allFromApiJson(final JSONArray json) {
    return parseArray(json, LeaderboardPlayerRound::fromApiJson);
  }
}
