package com.golfbetterapp.golfbetter.models.pga;

import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

import java.util.List;

@Getter
@Setter
@ToString
public class ScorecardV3 {
  private String __typename;
  private String tournamentName;
  private String id;
  private int currentRound;
  private boolean backNine;
  private int groupNumber;
  private Player player;
  private List<RoundScore> roundScores;
  private int currentHole;
  private String playerState;
  private boolean hideSov;
  private boolean profileEnabled;

  @Getter
  @Setter
  @ToString
  public static class RoundScore {
    private String __typename;
    private boolean complete;
    private int currentHole;
    private boolean currentRound;
    private NineHoles firstNine;
    private NineHoles secondNine;
    private int roundNumber;
    private int groupNumber;
    private String courseName;
    private String courseId;
    private int parTotal;
    private String total;
    private String scoreToPar;

    @Getter
    @Setter
    @ToString
    public static class NineHoles {
      private List<Hole> holes;
      private String totalLabel;
      private int parTotal;
      private String total;

      @Getter
      @Setter
      @ToString
      public static class Hole {
        private int holeNumber;
        private int par;
        private String score;
        private int sequenceNumber;
        private String status;
        private int yardage;
        private String roundScore;
      }
    }
  }
}
