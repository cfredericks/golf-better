package com.cfredericks.golfbetter.models.pga;

public class Player {
  private String id;
  private Boolean isActive;
  private String firstName;
  private String lastName;
  private String shortName;
  private String displayName;
  private String alphaSort;
  private String country;
  private String countryFlag;
  private String headshot;
  private PlayerBio playerBio;

  public static class PlayerBio {
    private String id;
    private Integer age;
    private String education;
    private Integer turnedPro;
  }
}
