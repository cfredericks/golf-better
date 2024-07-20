package com.cfredericks.golfbetter.models;

import java.util.List;
import java.util.UUID;

import lombok.Builder;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.ToString;

/**
 * Represents a single bet that is part of a {@link BetSession}.
 */
@Getter
@Builder(toBuilder = true)
@ToString
@EqualsAndHashCode
public class Bet {
  private UUID id;
  private String name;
  private UUID betSessionId;
  // maybe be null even if betSessionId is not, depending on if we've loaded join data
  private BetSession betSession;
  // empty for all players in bet session
  private List<Integer> otherPlayerIdsInBet;
  // maybe be null/empty even if otherPlayerIdsInBet is not, depending on if we've loaded join data
  private List<Player> otherPlayersInBet;
  private float dollarAmount;
  private BetType betType;
  private int round; // 0 for entire tournament
  private MetricType metricType;
  private PlayerType playerType;
  private RoundType roundType;
  private String metricPayloadJson;
  private String playerPayloadJson;
  private String roundPayloadJson;

  // Computed later - usually only a single player
  private List<Integer> winningPlayerIds;
  private List<Player> winningPlayers;

  public enum MetricType {
    Score, NumDoubleBogeys, NumBogeys, NumPars, NumBirdies, NumEagles, NumParsOrBetter, NumBirdieOrBetter
  }

  public enum ComparatorType {
    Most, Fewest
  }

  public enum PlayerType {
    AllPlayers, AnyPlayer
  }

  public enum RoundType {
    EntireRound, Front9, Back9, Any9, EvenHoles, OddHoles
  }

  public enum BetType {
    SinglePayout, MultiplierFromDelta
  }
}
