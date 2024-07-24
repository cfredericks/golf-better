package com.golfbetterapp.golfbetter.models;

import java.time.Instant;
import java.time.LocalDate;
import java.util.List;

import lombok.Builder;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.ToString;

@Getter
@Builder(toBuilder = true)
@ToString
@EqualsAndHashCode
public class LeaderboardPlayerRound {
  private String tournamentId;
  private String playerId;
  private Integer number;
  private LocalDate day;
  private Instant teeTime;
  private Boolean backNineStart;

  private Integer par;
  private Integer score;
  private Integer toPar;

  private List<LeaderboardPlayerRoundHole> holes;
}
