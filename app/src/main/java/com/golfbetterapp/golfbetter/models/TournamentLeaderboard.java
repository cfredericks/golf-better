
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
public class TournamentLeaderboard {
  private Tournament tournament;
  private List<Player> players;
}
