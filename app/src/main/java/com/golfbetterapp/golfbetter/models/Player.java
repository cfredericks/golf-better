package com.golfbetterapp.golfbetter.models;

import java.util.List;

import lombok.Builder;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.ToString;

@Getter
@Builder(toBuilder = true)
@ToString
@EqualsAndHashCode
public class Player {
  private String id;
  private String tournamentId;
  private String name;
  private String rank;
  private String country;

  private Integer totalScore;
  private Integer totalStrokes;
  private String totalThrough;

  private List<LeaderboardPlayerRound> rounds;
}
