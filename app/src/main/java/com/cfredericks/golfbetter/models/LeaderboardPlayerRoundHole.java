package com.cfredericks.golfbetter.models;

import lombok.Builder;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.ToString;

@Getter
@Builder(toBuilder = true)
@ToString
@EqualsAndHashCode
public class LeaderboardPlayerRoundHole {
  private String playerId;
  private String tournamentId;
  private String status;

  private Integer number;
  private Integer yardage;
  private Integer par;

  private Integer score;
  private Integer toPar;
}
