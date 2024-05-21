package com.example.golfbetter.models;

import org.json.JSONObject;

import java.nio.charset.StandardCharsets;
import java.util.UUID;

import lombok.Builder;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.SneakyThrows;
import lombok.ToString;

/**
 * Represents a golf course.
 */
@Getter
@Builder(toBuilder = true)
@ToString
@EqualsAndHashCode
public class Course {
  private UUID id;
  private Integer courseId;
  private String remoteId;
  private String name;
  private String abbreviation;
  private String city;
  private String state;
  private String country;

  @SneakyThrows
  public static Course fromPgaApiJson(final JSONObject json) {
    final int courseId = json.getInt("course_id");
    return Course.builder().id(UUID.nameUUIDFromBytes(Integer.toString(courseId).getBytes(StandardCharsets.UTF_8))).courseId(courseId).remoteId(json.getString("remote_id")).name(json.getString("name")).abbreviation(json.getString("abbreviation")).city(json.getString("city")).state(json.getString("state")).country(json.getString("country")).build();
  }
}
