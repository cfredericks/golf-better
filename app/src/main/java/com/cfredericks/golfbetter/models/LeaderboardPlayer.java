package com.cfredericks.golfbetter.models;

import static com.cfredericks.golfbetter.Utils.nullableBool;
import static com.cfredericks.golfbetter.Utils.nullableDouble;
import static com.cfredericks.golfbetter.Utils.nullableInt;
import static com.cfredericks.golfbetter.Utils.nullableStr;
import static com.cfredericks.golfbetter.Utils.parseArray;
import static com.cfredericks.golfbetter.Utils.parseTime;

import org.json.JSONArray;
import org.json.JSONObject;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.List;
import java.util.UUID;

import lombok.Builder;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.SneakyThrows;
import lombok.ToString;

/**
 * Represents a player on a leaderboard, which is a subfield in {@link TournamentLeaderboard}.
 */
@Getter
@Builder(toBuilder = true)
@ToString
@EqualsAndHashCode
public class LeaderboardPlayer {
  private UUID id;
  private int playerTournamentId;
  private int playerId;
  private int tournamentId;
  private String name;
  private Integer rank;
  private String country;

  // TODO: why are some of these double instead of int?
  private Double totalScore;
  private Double totalStrokes;
  private Double totalThrough;
  private Double earnings;
  private Double fedexPoints;

  private Double doubleEagles;
  private Double eagles;
  private Double birdies;
  private Double pars;
  private Double bogeys;
  private Double doubleBogeys;
  private Double tripleBogeys;
  private Double worseThanDoubleBogey;
  private Double worseThanTripleBogey;
  private Double holeInOnes;

  private Double streaksOfThreeBirdiesOrBetter;
  private Double streaksOfFourBirdiesOrBetter;
  private Double streaksOfFiveBirdiesOrBetter;
  private Double streaksOfSixBirdiesOrBetter;

  private Double consecutiveBirdieOrBetterCount;
  private Double roundsWithFiveOrMoreBirdiesOrBetter;
  private Double bogeyFreeRounds;
  private Double roundsUnderSeventy;
  private Double madeCut;
  private Double win;
  private Double bounceBackCount;

  private Double fantasyPoints;  // TODO: is this PGA fantasy?
  private Double fantasyPointsDraftKings;
  private Double fantasyPointsFanDuel;
  private Double fantasyPointsFantasyDraft;
  private Double fantasyPointsYahoo;

  // TODO: what are these?
  private Double draftKingsSalary;
  private Double fanDuelSalary;
  private Double fantasyDraftSalary;

  private Instant teeTime;
  private String tournamentStatus;  // TODO: what is this?
  private Boolean isAlternate;
  private Boolean isWithdrawn;
  private Boolean madeCutDidNotFinish;
  private String oddsToWin;  // TODO: what format is this?
  private String oddsToWinDescription;  // TODO: what is this?

  private List<LeaderboardPlayerRound> rounds;

  @SneakyThrows
  public static LeaderboardPlayer fromApiJson(final JSONObject json) {
    final int playerTournamentId = json.getInt("PlayerTournamentID");
    final String teeTimeStr = nullableStr(json, "TeeTime");
    return LeaderboardPlayer.builder()
        .id(UUID.nameUUIDFromBytes(Integer.toString(playerTournamentId).getBytes(StandardCharsets.UTF_8)))
        .playerTournamentId(playerTournamentId)
        .playerId(json.getInt("PlayerID"))
        .tournamentId(json.getInt("TournamentID"))
        .name(json.getString("Name"))
        // TODO: are some of these fields actually nullable, or is that just the randomized test data?
        .rank(nullableInt(json, "Rank"))
        .country(json.getString("Country"))
        .totalScore(nullableDouble(json, "TotalScore"))
        .totalStrokes(nullableDouble(json, "TotalStrokes"))
        .totalThrough(nullableDouble(json, "TotalThrough"))
        .earnings(nullableDouble(json, "Earnings"))
        .fedexPoints(nullableDouble(json, "FedExPoints"))
        .doubleEagles(json.getDouble("DoubleEagles"))
        .eagles(json.getDouble("Eagles"))
        .birdies(json.getDouble("Birdies"))
        .pars(json.getDouble("Pars"))
        .bogeys(json.getDouble("Bogeys"))
        .doubleBogeys(json.getDouble("DoubleBogeys"))
        .tripleBogeys(json.getDouble("TripleBogeys"))
        .worseThanDoubleBogey(json.getDouble("WorseThanDoubleBogey"))
        .worseThanTripleBogey(json.getDouble("WorseThanTripleBogey"))
        .holeInOnes(json.getDouble("HoleInOnes"))
        .streaksOfThreeBirdiesOrBetter(json.getDouble("StreaksOfThreeBirdiesOrBetter"))
        .streaksOfFourBirdiesOrBetter(json.getDouble("StreaksOfFourBirdiesOrBetter"))
        .streaksOfFiveBirdiesOrBetter(json.getDouble("StreaksOfFiveBirdiesOrBetter"))
        .streaksOfSixBirdiesOrBetter(json.getDouble("StreaksOfSixBirdiesOrBetter"))
        .consecutiveBirdieOrBetterCount(json.getDouble("ConsecutiveBirdieOrBetterCount"))
        .roundsWithFiveOrMoreBirdiesOrBetter(json.getDouble("RoundsWithFiveOrMoreBirdiesOrBetter"))
        .bogeyFreeRounds(json.getDouble("BogeyFreeRounds"))
        .roundsUnderSeventy(json.getDouble("RoundsUnderSeventy"))
        .madeCut(json.getDouble("MadeCut"))
        .win(nullableDouble(json, "Win"))
        .bounceBackCount(json.getDouble("BounceBackCount"))
        .fantasyPoints(json.getDouble("FantasyPoints"))
        .fantasyPointsDraftKings(json.getDouble("FantasyPointsDraftKings"))
        .fantasyPointsFanDuel(json.getDouble("FantasyPointsFanDuel"))
        .fantasyPointsFantasyDraft(json.getDouble("FantasyPointsFantasyDraft"))
        .fantasyPointsYahoo(json.getDouble("FantasyPointsYahoo"))
        .draftKingsSalary(nullableDouble(json, "DraftKingsSalary"))
        .fanDuelSalary(nullableDouble(json, "FanDuelSalary"))
        .fantasyDraftSalary(nullableDouble(json, "FantasyDraftSalary"))
        .teeTime(parseTime(teeTimeStr))
        .tournamentStatus(nullableStr(json, "TournamentStatus"))
        .isAlternate(nullableBool(json, "IsAlternate"))
        .isWithdrawn(json.getBoolean("IsWithdrawn"))
        .madeCutDidNotFinish(json.getBoolean("MadeCutDidNotFinish"))
        .oddsToWin(nullableStr(json, "OddsToWin"))
        .oddsToWinDescription(nullableStr(json, "OddsToWinDescription"))
        .rounds(LeaderboardPlayerRound.allFromApiJson(json.getJSONArray("Rounds")))
        .build();
  }

  public static List<LeaderboardPlayer> allFromApiJson(final JSONArray json) {
    return parseArray(json, LeaderboardPlayer::fromApiJson);
  }
}
