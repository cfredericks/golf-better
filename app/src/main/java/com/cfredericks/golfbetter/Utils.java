package com.cfredericks.golfbetter;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.time.Duration;
import java.time.Instant;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;

import lombok.SneakyThrows;

public class Utils {
  static final Duration DEFAULT_TIMEOUT = Duration.ofSeconds(10);

  /**
   * Makes a GET API call and returns a {@link JSONObject} representing the response.
   */
  public static JSONObject getJSONObjectFromURL(final String urlString) throws IOException, JSONException {
    return getJSONObjectFromURL(urlString, DEFAULT_TIMEOUT);
  }
  /**
   * Makes a GET API call and returns a {@link JSONObject} representing the response.
   */
  public static JSONArray getJSONArrayFromURL(final String urlString) throws IOException, JSONException {
    return getJSONArrayFromURL(urlString, DEFAULT_TIMEOUT);
  }

  /**
   * Makes a GET API call and returns a {@link JSONObject} representing the response.
   */
  public static JSONObject getJSONObjectFromURL(final String urlString, final Duration timeout) throws IOException, JSONException {
    return getResponseFromURL(urlString, JSONObject::new, timeout);
  }

  /**
   * Makes a GET API call and returns a {@link JSONArray} representing the response.
   */
  public static JSONArray getJSONArrayFromURL(final String urlString, final Duration timeout) throws IOException, JSONException {
    return getResponseFromURL(urlString, JSONArray::new, timeout);
  }

  /**
   * Makes a GET API call and returns a {@code T} representing the response.
   */
  public static <T> T getResponseFromURL(final String urlString, final JsonParser<T> respParser, final Duration timeout) throws IOException, JSONException {
    return getResponseFromURL(new URL(urlString), respParser, timeout);
  }

  /**
   * Makes a GET API call and returns a {@code T} representing the response.
   */
  public static <T> T getResponseFromURL(final URL url, final JsonParser<T> respParser, final Duration timeout) throws IOException, JSONException {
    final HttpURLConnection urlConnection = (HttpURLConnection) url.openConnection();
    urlConnection.setRequestMethod("GET");
    urlConnection.setReadTimeout((int) timeout.toMillis());
    urlConnection.setConnectTimeout((int) timeout.toMillis());
    urlConnection.setDoOutput(true);
    urlConnection.connect();

    return parseResponse(url.openStream(), respParser);
  }

  /**
   * Returns a {@link String}, and returns {@code null} if it doesn't exist or is {@code null},
   * rather than throwing a {@link JSONException} like the built in methods.
   */
  public static String nullableStr(final JSONObject json, final String key) {
    if (!json.isNull(key)) {
      try {
        return json.getString(key);
      } catch (final JSONException e) {
        return null;
      }
    }

    return null;
  }

  /**
   * Returns a {@link Boolean}, and returns {@code null} if it doesn't exist or is {@code null},
   * rather than throwing a {@link JSONException} like the built in methods.
   */
  public static Boolean nullableBool(final JSONObject json, final String key) {
    if (!json.isNull(key)) {
      try {
        return json.getBoolean(key);
      } catch (final JSONException e) {
        return null;
      }
    }

    return null;
  }

  /**
   * Returns a {@link Integer}, and returns {@code null} if it doesn't exist or is {@code null},
   * rather than throwing a {@link JSONException} like the built in methods.
   */
  public static Integer nullableInt(final JSONObject json, final String key) {
    if (!json.isNull(key)) {
      try {
        return json.getInt(key);
      } catch (final JSONException e) {
        return null;
      }
    }

    return null;
  }

  /**
   * Returns a {@link Double}, and returns {@code null} if it doesn't exist or is {@code null},
   * rather than throwing a {@link JSONException} like the built in methods.
   */
  public static Double nullableDouble(final JSONObject json, final String key) {
    if (!json.isNull(key)) {
      try {
        return json.getDouble(key);
      } catch (final JSONException e) {
        return null;
      }
    }

    return null;
  }

  /**
   * Returns a {@link JSONArray}, and returns and empty array if it doesn't exist or is {@code null},
   * rather than throwing a {@link JSONException} like the built in methods.
   */
  public static JSONArray nullableArray(final JSONObject json, final String key) {
    if (!json.isNull(key)) {
      try {
        return json.getJSONArray(key);
      } catch (final JSONException e) {
        return new JSONArray();
      }
    }

    return new JSONArray();
  }

  /**
   * Convert a {@link JSONArray} to a parsed Java {@link List}.
   */
  @SneakyThrows
  public static <OutT, ElemT> List<OutT> parseArray(final JSONArray json, final Function<ElemT, OutT> objParser) {
      final List<OutT> objs = new ArrayList<>();
      for (int i = 0; i < json.length(); i++) {
        objs.add(objParser.apply((ElemT) json.get(i)));
      }
      return objs;
  }

  /**
   * Functional interface for parsing JSON that can throw a {@link JSONException}.
   */
  public interface JsonParser<T> {
    T apply(final String s) throws JSONException;
  }

  private static <T> T parseResponse(final InputStream dataStream, final JsonParser<T> respParser) throws IOException, JSONException {
    final StringBuilder sb = new StringBuilder();
    try (final BufferedReader br = new BufferedReader(new InputStreamReader(dataStream))) {
      String line;
      while ((line = br.readLine()) != null) {
        if (sb.length() > 0) {
          sb.append("\n");
        }
        sb.append(line);
      }
    }

    return respParser.apply(sb.toString());
  }

  public static LocalDate parseDate(final String date) {
    if (date == null) {
      return null;
    }
    return LocalDate.parse(date.replace("T00:00:00", ""));
  }

  public static Instant parseTime(final String timestamp) {
    if (timestamp == null) {
      return null;
    }

    if (timestamp.contains("T") && !timestamp.endsWith("Z")) {
      return Instant.parse(timestamp + "Z");
    }

    if (timestamp.contains("T")) {
      return Instant.parse(timestamp);
    }

    return Instant.parse(timestamp + "T00:00:00Z");
  }
}
