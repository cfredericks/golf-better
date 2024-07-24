package com.golfbetterapp.golfbetter.models;

import java.util.List;
import java.util.UUID;

import lombok.Builder;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.ToString;

/**
 * Represents a session of bets, which usually corresponds to a tournament.
 */
@Getter
@Builder(toBuilder = true)
@ToString
@EqualsAndHashCode
public class BetSession {
  private UUID id;
  private String name;
  // empty for all players
  private List<UUID> otherPlayerIdsInBetSession;
  // maybe be null/empty even if otherPlayerIdsInBetSession is not, depending on if we've loaded join data
  private List<Player> otherPlayersInBetSession;
  private List<UUID> betIds;
  private List<Bet> bets;
}
