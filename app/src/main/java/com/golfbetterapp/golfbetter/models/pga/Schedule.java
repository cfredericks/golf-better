package com.golfbetterapp.golfbetter.models.pga;

import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

import java.util.List;

@Getter
@Setter
@ToString
public class Schedule {
  private List<TournamentMonthGroup> completed;
  private List<TournamentMonthGroup> upcoming;
  private List<Filter> filters;
  private String seasonYear;
  private String tour;

  @Getter
  @Setter
  @ToString
  public static class TournamentMonthGroup {
    private String month;
    private String year;
    private int monthSort;
    private List<Tournament> tournaments;
  }

  @Getter
  @Setter
  @ToString
  public static class Filter {
    private String type;
    private String name;
  }

  @Getter
  @Setter
  @ToString
  public static class Tournament {
    private String tournamentName;
    private String id;
    private String beautyImage;
    private String champion;
    private List<Champion> champions;
    private String championEarnings;
    private String championId;
    private String city;
    private String country;
    private String countryCode;
    private String courseName;
    private String date;
    private String dateAccessibilityText;
    private String purse;
    private String sortDate;
    private long startDate;
    private String state;
    private String stateCode;
    private String status;
    private String tournamentStatus;
    private String ticketsURL;
    private String tourStandingHeading;
    private String tourStandingValue;
    private String tournamentLogo;
    private String display;
    private int sequenceNumber;
    private TournamentCategoryInfo tournamentCategoryInfo;

    @Getter
    @Setter
    @ToString
    public static class Champion {
      private String displayName;
      private String playerId;
    }

    @Getter
    @Setter
    @ToString
    public static class TournamentCategoryInfo {
      private String type;
      private String logoLight;
      private String logoDark;
      private String label;
    }
  }
}
