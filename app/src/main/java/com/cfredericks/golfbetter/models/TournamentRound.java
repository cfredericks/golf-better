package com.cfredericks.golfbetter.models;

import java.time.LocalDate;
import java.util.UUID;

import lombok.Builder;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.ToString;

@Getter
@Builder(toBuilder = true)
@ToString
@EqualsAndHashCode
public class TournamentRound {
  private String tournamentId;
  private Integer number;
  private LocalDate day;
}
