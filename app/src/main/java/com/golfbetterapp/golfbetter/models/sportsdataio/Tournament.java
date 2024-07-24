package com.golfbetterapp.golfbetter.models.sportsdataio;

import static com.golfbetterapp.golfbetter.Utils.nullableArray;
import static com.golfbetterapp.golfbetter.Utils.nullableDouble;
import static com.golfbetterapp.golfbetter.Utils.nullableInt;
import static com.golfbetterapp.golfbetter.Utils.nullableStr;
import static com.golfbetterapp.golfbetter.Utils.parseArray;

import com.golfbetterapp.golfbetter.clients.SportsDataIoAppEngineClient;

import org.json.JSONArray;
import org.json.JSONObject;

import java.nio.charset.StandardCharsets;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

import lombok.Builder;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.SneakyThrows;
import lombok.ToString;

/**
 * Represents a tournament, which is the API response for {@link SportsDataIoAppEngineClient#TOURNAMENT_FORMAT},
 * as well as a subfield in {@link TournamentLeaderboard}.
 */
@Getter
@Builder(toBuilder = true)
@ToString
@EqualsAndHashCode
public class Tournament {
  private UUID id;
  private Integer tournamentId;
  private String name;
  private LocalDate startDate;
  private LocalDate endDate;
  private Boolean isOver;
  private Boolean isInProgress;
  private String venue;
  private String location;
  private Integer par;
  private Integer yards;
  private Double purse;
  private String startDateTime;  // TODO: what is this?
  private Boolean canceled;
  private Boolean covered;  // TODO: what is this?
  private Boolean teeTimesSet;
  private String city;
  private String state;
  private String zipCode;
  private String country;
  private String timezone;
  private String format;
  private String sportRadarTournamentId;  // TODO: what is this?
  private String oddsCoverage;  // TODO: what is this?

  private List<TournamentRound> rounds;

  @SneakyThrows
  public static Tournament fromApiJson(JSONObject json, final boolean isNestedDataCol) {
    if (isNestedDataCol) {
      json = json.getJSONObject("data");
    }

    final int tournamentId = json.getInt("TournamentID");
    final String startDateStr = nullableStr(json, "StartDate");
    final String endDateStr = nullableStr(json, "EndDate");
    return Tournament.builder()
        .id(UUID.nameUUIDFromBytes(Integer.toString(tournamentId).getBytes(StandardCharsets.UTF_8)))
        .tournamentId(tournamentId)
        .name(json.getString("Name"))
        .startDate(startDateStr != null ? LocalDate.parse(startDateStr.replace("T00:00:00", "")) : null)
        .endDate(endDateStr != null ? LocalDate.parse(endDateStr.replace("T00:00:00", "")) : null)
        // TODO: are some of these fields actually nullable, or is that just the randomized test data?
        .isOver(json.optBoolean("IsOver", false))
        .isInProgress(json.optBoolean("IsInProgress", false))
        .venue(nullableStr(json, "Venue"))
        .location(nullableStr(json, "Location"))
        .par(nullableInt(json, "Par"))
        .yards(nullableInt(json, "Yards"))
        .purse(nullableDouble(json, "Purse"))
        .startDateTime(nullableStr(json, "StartDateTime"))
        .canceled(json.optBoolean("Canceled", false))
        .covered(json.optBoolean("Covered", false))
        .city(json.getString("City"))
        .state(json.getString("State"))
        .zipCode(json.getString("ZipCode"))
        .country(json.getString("Country"))
        .timezone(json.getString("TimeZone"))
        .format(json.getString("Format"))
        .sportRadarTournamentId(json.getString("SportRadarTournamentID"))
        .oddsCoverage(json.getString("OddsCoverage"))
        .rounds(TournamentRound.allFromApiJson(nullableArray(json, "Rounds")))
        .build();
  }

  public static List<Tournament> allFromApiJson(final JSONArray json) {
    return parseArray(json, (JSONObject obj) -> fromApiJson(obj, true));
  }
}
