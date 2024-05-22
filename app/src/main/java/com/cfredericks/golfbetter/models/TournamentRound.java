package com.cfredericks.golfbetter.models;

import static com.cfredericks.golfbetter.Utils.nullableStr;
import static com.cfredericks.golfbetter.Utils.parseArray;

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
 * Represents information about a round in a tournament, which is a subfield in {@link Tournament}.
 */
@Getter
@Builder(toBuilder = true)
@ToString
@EqualsAndHashCode
public class TournamentRound {
  private UUID id;
  private Integer tournamentId;
  private Integer roundId;
  private Integer number;
  private LocalDate day;

  @SneakyThrows
  public static TournamentRound fromApiJson(final JSONObject json) {
    final int tournamentId = json.getInt("TournamentID");
    final int roundId = json.getInt("RoundID");
    final String dayStr = nullableStr(json, "Day");
    return TournamentRound.builder()
        .id(UUID.nameUUIDFromBytes((tournamentId + "|" + roundId).getBytes(StandardCharsets.UTF_8)))
        .tournamentId(tournamentId)
        .roundId(roundId)
        .number(json.getInt("Number"))
        .day(dayStr != null ? LocalDate.parse(dayStr.replace("T00:00:00", "")) : null)
        .build();
  }

  public static List<TournamentRound> allFromApiJson(final JSONArray json) {
    return parseArray(json, TournamentRound::fromApiJson);
  }
}
