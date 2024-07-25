package com.golfbetterapp.golfbetter;

import android.content.Context;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.Instant;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.function.Function;

import lombok.SneakyThrows;

public class Utils {
  static final Duration DEFAULT_TIMEOUT = Duration.ofSeconds(10);
  static final ExecutorService EXECUTOR = Executors.newFixedThreadPool(20);

  /**
   * Makes a GET API call and returns a {@link JSONObject} representing the response.
   */
  public static void getJSONObjectFromURL(final Context context, final String urlString, final boolean withToken, final ApiCallback<JSONObject> callback) {
    getJSONObjectFromURL(context, urlString, DEFAULT_TIMEOUT, withToken, callback);
  }
  /**
   * Makes a GET API call and returns a {@link JSONArray} representing the response.
   */
  public static void getJSONArrayFromURL(final Context context, final String urlString, final boolean withToken, final ApiCallback<JSONArray> callback) {
    getJSONArrayFromURL(context, urlString, DEFAULT_TIMEOUT, withToken, callback);
  }

  /**
   * Makes a GET API call and returns a {@link JSONObject} representing the response.
   */
  public static void getJSONObjectFromURL(final Context context, final String urlString, final Duration timeout, final boolean withToken, final ApiCallback<JSONObject> callback) {
    getResponseFromURL(context, urlString, JSONObject::new, timeout, withToken, callback);
  }

  /**
   * Makes a GET API call and returns a {@link JSONArray} representing the response.
   */
  public static void getJSONArrayFromURL(final Context context, final String urlString, final Duration timeout, final boolean withToken, final ApiCallback<JSONArray> callback) {
    getResponseFromURL(context, urlString, JSONArray::new, timeout, withToken, callback);
  }

  /**
   * Makes a GET API call and returns a {@code T} representing the response.
   */
  public static <T> void getResponseFromURL(final Context context, final String urlString, final JsonParser<T> respParser, final boolean withToken, final ApiCallback<T> callback) {
    final URL url;
    try {
      url = new URL(urlString);
    } catch (final MalformedURLException e) {
      callback.onFailure(e);
      return;
    }
    getResponseFromURL(context, url, respParser, DEFAULT_TIMEOUT, withToken, callback);
  }

  /**
   * Makes a POST API call and returns a {@code T} representing the response.
   */
  public static <T> void postToURL(final Context context, final String urlString, final String jsonData, final JsonParser<T> respParser, final boolean withToken, final ApiCallback<T> callback) {
    final URL url;
    try {
      url = new URL(urlString);
    } catch (final MalformedURLException e) {
      callback.onFailure(e);
      return;
    }
    postToURL(context, url, jsonData, respParser, DEFAULT_TIMEOUT, withToken, callback);
  }

  /**
   * Makes a GET API call and returns a {@code T} representing the response.
   */
  public static <T> void getResponseFromURL(final Context context, final String urlString, final JsonParser<T> respParser, final Duration timeout, final boolean withToken, final ApiCallback<T> callback) {
    final URL url;
    try {
      url = new URL(urlString);
    } catch (final MalformedURLException e) {
      callback.onFailure(e);
      return;
    }
    getResponseFromURL(context, url, respParser, timeout, withToken, callback);
  }

  /**
   * Makes a GET API call and returns a {@code T} representing the response.
   */
  public static <T> void getResponseFromURL(final Context context, final URL url, final JsonParser<T> respParser, final Duration timeout, final boolean withToken, final ApiCallback<T> callback) {
    if (withToken) {
      TokenManager.getInstance().getIdToken(context, new TokenManager.IdTokenCallback() {
        @Override
        public void onSuccess(final String idToken) {
          EXECUTOR.execute(() -> makeGetRequest(url, respParser, timeout, idToken, callback));
        }

        @Override
        public void onFailure(final Exception e) {
          callback.onFailure(e);
        }
      });
    } else {
      makeGetRequest(url, respParser, timeout, null, callback);
    }
  }

  /**
   * Makes a POST API call and returns a {@code T} representing the response.
   */
  public static <T> void postToURL(final Context context, final URL url, final String jsonData, final JsonParser<T> respParser, final Duration timeout, final boolean withToken, final ApiCallback<T> callback) {
    if (withToken) {
      TokenManager.getInstance().getIdToken(context, new TokenManager.IdTokenCallback() {
        @Override
        public void onSuccess(final String idToken) {
          EXECUTOR.execute(() -> makePostRequest(url, jsonData, respParser, timeout, idToken, callback));
        }

        @Override
        public void onFailure(final Exception e) {
          callback.onFailure(e);
        }
      });
    } else {
      makeGetRequest(url, respParser, timeout, null, callback);
    }
  }

  private static <T> void makeGetRequest(final URL url, final JsonParser<T> respParser, final Duration timeout, final String idToken, final ApiCallback<T> callback) {
    try {
      final HttpURLConnection urlConnection = (HttpURLConnection) url.openConnection();
      urlConnection.setRequestMethod("GET");
      urlConnection.setReadTimeout((int) timeout.toMillis());
      urlConnection.setConnectTimeout((int) timeout.toMillis());

      if (idToken != null) {
        urlConnection.setRequestProperty("Authorization", "Bearer " + idToken);
      }

      urlConnection.connect();
      callback.onSuccess(parseResponse(urlConnection.getInputStream(), respParser));
    } catch (final IOException | JSONException e) {
      callback.onFailure(e);
    }
  }

  private static <T> void makePostRequest(final URL url, final String jsonData, final JsonParser<T> respParser, final Duration timeout, final String idToken, final ApiCallback<T> callback) {
    try {
      final HttpURLConnection urlConnection = (HttpURLConnection) url.openConnection();
      urlConnection.setRequestMethod("POST");
      urlConnection.setRequestProperty("Content-Type", "application/json");
      urlConnection.setReadTimeout((int) timeout.toMillis());
      urlConnection.setConnectTimeout((int) timeout.toMillis());

      if (idToken != null) {
        urlConnection.setRequestProperty("Authorization", "Bearer " + idToken);
      }

      if (jsonData != null) {
        urlConnection.setDoOutput(true);
        try (final OutputStream os = urlConnection.getOutputStream()) {
          final byte[] dataBytes = jsonData.getBytes(StandardCharsets.UTF_8);
          os.write(dataBytes, 0, dataBytes.length);
        }
      }

      if (urlConnection.getResponseCode() >= HttpURLConnection.HTTP_OK && urlConnection.getResponseCode() < HttpURLConnection.HTTP_MULT_CHOICE) {
        if (respParser != null) {
          callback.onSuccess(parseResponse(urlConnection.getInputStream(), respParser));
        } else {
          callback.onSuccess(null);
        }
      } else {
        callback.onFailure(
            new IllegalStateException(
              String.format("Error posting user, got status code: %d", urlConnection.getResponseCode())));
      }
    } catch (final IOException | JSONException e) {
      callback.onFailure(e);
    }
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

  public static <T> Iterable<T> optionalIter(final Iterable<T> iter) {
    if (iter == null) {
      return Collections.emptyList();
    }

    return iter;
  }

  public static Integer parseScore(final String score) {
    if (score == null || score.isEmpty() || " ".equals(score) || "-".equals(score)) {
      return null;
    }

    if ("E".equals(score)) {
      return 0;
    }

    return Integer.parseInt(score);
  }

  public static boolean isInteger(String s) {
    return isInteger(s,10);
  }

  public static boolean isInteger(String s, int radix) {
    if(s.isEmpty()) return false;
    for(int i = 0; i < s.length(); i++) {
      if(i == 0 && s.charAt(i) == '-') {
        if(s.length() == 1) return false;
        else continue;
      }
      if(Character.digit(s.charAt(i),radix) < 0) return false;
    }
    return true;
  }

  public interface ApiCallback<T> {
    void onSuccess(final T result);
    void onFailure(final Exception e);
  }
}
