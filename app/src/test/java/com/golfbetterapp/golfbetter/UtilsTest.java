package com.golfbetterapp.golfbetter;

import static com.golfbetterapp.golfbetter.Utils.nullableArray;
import static com.golfbetterapp.golfbetter.Utils.nullableBool;
import static com.golfbetterapp.golfbetter.Utils.nullableDouble;
import static com.golfbetterapp.golfbetter.Utils.nullableInt;
import static com.golfbetterapp.golfbetter.Utils.nullableStr;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.when;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLStreamHandler;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.HashSet;
import java.util.Set;

public class UtilsTest {
    @Mock
    private HttpURLConnection mockUrlConnection;

    @Mock
    private InputStream mockInputStream;

    @Before
    public void setUp() throws Exception {
        MockitoAnnotations.openMocks(this);
        when(mockUrlConnection.getInputStream()).thenReturn(mockInputStream);
    }

    @Test
    public void test_nullableStr() throws JSONException {
        final JSONObject json = new JSONObject();
        json.put("known", "foo");
        json.put("null", null);
        assertNull(nullableStr(json, "unknown"));
        assertNull(nullableStr(json, "null"));
        assertEquals("foo", nullableStr(json, "known"));
    }

    @Test
    public void test_nullableBool() throws JSONException {
        final JSONObject json = new JSONObject();
        json.put("known", true);
        json.put("null", null);
        assertNull(nullableBool(json, "unknown"));
        assertNull(nullableBool(json, "null"));
        assertEquals(true, nullableBool(json, "known"));
    }

    @Test
    public void test_nullableInt() throws JSONException {
        final JSONObject json = new JSONObject();
        json.put("known", 7);
        json.put("null", null);
        assertNull(nullableInt(json, "unknown"));
        assertNull(nullableInt(json, "null"));
        assertEquals(7, (int) nullableInt(json, "known"));
    }

    @Test
    public void test_nullableDouble() throws JSONException {
        final JSONObject json = new JSONObject();
        json.put("known", 1.3);
        json.put("null", null);
        assertNull(nullableDouble(json, "unknown"));
        assertNull(nullableDouble(json, "null"));
        assertEquals(1.3, (double) nullableDouble(json, "known"), 0.00001);
    }

    @Test
    public void test_nullableArray() throws JSONException {
        final JSONArray arr = new JSONArray();
        arr.put(1);
        arr.put(2);
        final JSONObject json = new JSONObject();
        json.put("known", arr);
        json.put("null", null);
        assertEquals(0, nullableArray(json, "unknown").length());
        assertEquals(0, nullableArray(json, "null").length());
        assertEquals(arr, nullableArray(json, "known"));
    }

    @Test
    public void test_parseArray() {
        final JSONArray arr = new JSONArray();
        arr.put("a");
        arr.put("b");
        final Set<String> expected = new HashSet<>();
        expected.add("a");
        expected.add("b");
        assertEquals(expected, new HashSet<>(Utils.parseArray(arr, String::toString)));
    }

    @Test
    public void test_getResponseFromURL() throws JSONException, IOException {
        final ByteArrayInputStream is = new ByteArrayInputStream(
            "abc\r\ndef".getBytes(StandardCharsets.UTF_8));
        doReturn(is).when(mockUrlConnection).getInputStream();

        //make getLastModified() return first 10, then 11
        when(mockUrlConnection.getLastModified()).thenReturn(10L, 11L);

        final URLStreamHandler stubUrlHandler = new URLStreamHandler() {
            @Override
            protected URLConnection openConnection(final URL u) {
                return mockUrlConnection;
            }
        };
        final URL url = new URL("foo", "bar", 99, "/foobar", stubUrlHandler);
        final String actual = Utils.getResponseFromURL(url, x -> x, Duration.ofSeconds(5));
        // "/r/n" replaced by "/n" by BufferedReader.readLine()
        assertEquals("abc\ndef", actual);
    }
}