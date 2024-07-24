package com.golfbetterapp.golfbetter.models;

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
public class Tournament {
  private String id;
  private String name;
  private String courseName;
  private String status;
  private LocalDate startDate;
  private LocalDate endDate;
  private Boolean isOver;
  private Boolean isInProgress;
  private String venue;
  private String location;
  private Integer par;
  private Integer yards;
  private String purse;
  private String city;
  private String state;
  private String country;
  private String format;

  private List<TournamentRound> rounds;
}
