package com.golfbetterapp.golfbetter.models;

import java.time.Instant;

import lombok.Builder;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.ToString;

@Getter
@Builder(toBuilder = true)
@ToString
@EqualsAndHashCode
public class User {
  private String id;
  private String name;
  private String email;
  private Instant created;
  private Instant lastUpdated;
  private Instant lastLogin;
}
