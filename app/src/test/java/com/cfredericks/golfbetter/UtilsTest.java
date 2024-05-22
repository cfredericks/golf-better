package com.cfredericks.golfbetter;

import static com.cfredericks.golfbetter.Utils.nullableArray;
import static com.cfredericks.golfbetter.Utils.nullableBool;
import static com.cfredericks.golfbetter.Utils.nullableDouble;
import static com.cfredericks.golfbetter.Utils.nullableInt;
import static com.cfredericks.golfbetter.Utils.nullableStr;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.junit.Test;

import java.util.HashSet;
import java.util.Set;

public class UtilsTest {
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
    public void test_fail() {
        assertEquals(1, 2);
    }
}