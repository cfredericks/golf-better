package com.golfbetterapp.golfbetter.models.pga;

import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

import java.util.List;

@Getter
@Setter
@ToString
public class LeaderboardV3 {
  private String __typename;
  private String id;
  private String timezone;
  private String tournamentId;
  private String leaderboardRoundHeader;
  private String formatType;
  private List<PlayerRowV3> players;
  private List<Course> courses;
  private List<Message> messages;
  private String tournamentStatus;
  private List<Round> rounds;
  private boolean isPlayoffActive;
  private boolean scorecardEnabled;
  private boolean profileEnabled;
  private boolean subEvent;
  private List<FeatureItem> leaderboardFeatures;
  private boolean standingsEnabled;
  private String standingsHeader;
  private boolean hideSov;
  private boolean disableOdds;

  @Getter
  @Setter
  @ToString
  public static class PlayerRowV3 {
    private String __typename;
    private String id;
    private int leaderboardSortOrder;
    private Player player;
    private ScoringData scoringData;

    @Getter
    @Setter
    @ToString
    public static class Player {
      private String id;
      private String firstName;
      private String lastName;
      private boolean amateur;
      private String displayName;
      private String abbreviations;
      private String abbreviationsAccessibilityText;
      private String country;
      private String countryFlag;
      private String shortName;
      private String lineColor;
      private boolean tourBound;
      private String bettingProfile;
    }

    @Getter
    @Setter
    @ToString
    public static class ScoringData {
      private String position;
      private String total;
      private int totalSort;
      private String thru;
      private int thruSort;
      private String score;
      private int scoreSort;
      private String courseId;
      private int groupNumber;
      private int currentRound;
      private String oddsToWin;
      private String oddsSwing;
      private String oddsOptionId;
      private double oddsSort;
      private boolean backNine;
      private String roundHeader;
      private List<String> rounds;
      private String movementDirection;
      private String movementAmount;
      private String playerState;
      private String rankingMovement;
      private String rankingMovementAmount;
      private int rankingMovementAmountSort;
      private String totalStrokes;
      private String official;
      private int officialSort;
      private String projected;
      private int projectedSort;
      private boolean hasStoryContent;
      private List<String> storyContentRounds;
      private String roundStatus;
      private String rankLogoLight;
      private String rankLogoDark;
    }
  }

  @Getter
  @Setter
  @ToString
  public static class Course {
    private String __typename;
    private String id;
    private String courseName;
    private String courseCode;
    private String scoringLevel;
    private boolean hostCourse;
  }

  @Getter
  @Setter
  @ToString
  public static class Message {
    // Define message fields as necessary
  }

  @Getter
  @Setter
  @ToString
  public static class Round {
    private int roundNumber;
    private String displayText;
  }

  @Getter
  @Setter
  @ToString
  public static class FeatureItem {
    private String __typename;
    private String name;
    private String leaderboardFeatures;
    private boolean isNew;
    private String tooltipText;
    private String tooltipTitle;
  }
}
