package com.golfbetterapp.golfbetter.models.pga;

import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

@Getter
@Setter
@ToString
public class Player {
  private String id;
  private Boolean isActive;
  private String firstName;
  private String lastName;
  private String shortName;
  private boolean amateur;
  private String displayName;
  private String alphaSort;
  private String abbreviations;
  private String abbreviationsAccessibilityText;
  private String country;
  private String countryFlag;
  private String headshot;
  private String lineColor;
  private boolean tourBound;
  private String bettingProfile;
  private PlayerBio playerBio;

  @Getter
  @Setter
  @ToString
  public static class PlayerBio {
    private String id;
    private Integer age;
    private String education;
    private Integer turnedPro;
  }
}
