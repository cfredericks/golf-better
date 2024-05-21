package com.example.golfbetter;

import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.widget.ArrayAdapter;

import com.example.golfbetter.databinding.FragmentApiQueryBinding;
import com.example.golfbetter.models.Tournament;
import com.example.golfbetter.models.TournamentLeaderboard;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.stream.Collectors;

/**
 * Helpers for querying the api.sportsdata.io API endpoints.
 */
// TODO: Separate API and parsing code from UI code
public class SportsDataApiClient {
  // TODO: Allow passing this in or looking it up
  private static final String API_KEY = "";

  public static final String TOURNAMENT_FORMAT = "{tournament}";
  public static final String TOURNAMENTS_ENDPOINT = "https://api.sportsdata.io/golf/v2/json/Tournaments";
  public static final String LEADERBOARD_ENDPOINT = "https://api.sportsdata.io/golf/v2/json/Leaderboard/" + TOURNAMENT_FORMAT;

  public static void updateTournaments(final FragmentApiQueryBinding binding) {
    final ExecutorService executor = Executors.newSingleThreadExecutor();
    final Handler handler = new Handler(Looper.getMainLooper());
    executor.execute(() -> {
      // Background work here
      final JSONArray json;
      try {
        json = Utils.getJSONArrayFromURL(TOURNAMENTS_ENDPOINT + "?key=" + API_KEY);
      } catch (final IOException | JSONException e) {
        Log.e(SportsDataApiClient.class.getSimpleName(), String.format("Error reading from endpoint '%s'", TOURNAMENTS_ENDPOINT), e);
        return;
      }
      handler.post(() -> {
        // UI Thread work here
        // binding.textviewApiQuery.setText(json.toString(2));
        final List<Tournament> tournaments = Tournament.allFromApiJson(json);
        final List<Tournament> runningTournaments = tournaments.stream().filter(Tournament::getIsInProgress).collect(Collectors.toList());

        Log.d(SportsDataApiClient.class.getSimpleName(), String.format("All running tournaments: %s", runningTournaments));
        Log.d(SportsDataApiClient.class.getSimpleName(), String.format("All tournaments: %s", tournaments));

        final ArrayAdapter<String> tournamentsAd
            = new ArrayAdapter<>(
            binding.tournamentsSpinner.getContext(),
            android.R.layout.simple_spinner_item,
            tournaments.stream().map(t -> t.getName() + " (" + t.getTournamentId() + ")").collect(Collectors.toList()));
        binding.tournamentsSpinner.setAdapter(tournamentsAd);
      });
    });
  }

  public static void updateLeaderboard(final int tournamentId, final FragmentApiQueryBinding binding) {
    final ExecutorService executor = Executors.newSingleThreadExecutor();
    final Handler handler = new Handler(Looper.getMainLooper());
    final String endpoint = LEADERBOARD_ENDPOINT.replace(TOURNAMENT_FORMAT, Integer.toString(tournamentId));
    executor.execute(() -> {
      // Background work here
      final JSONObject json;
      try {
        json = Utils.getJSONObjectFromURL(endpoint + "?key=" + API_KEY);
      } catch (final IOException | JSONException e) {
        Log.e(SportsDataApiClient.class.getSimpleName(), String.format("Error reading from endpoint '%s'", endpoint), e);
        return;
      }
      handler.post(() -> {
        // UI Thread work here
        // binding.textviewApiQuery.setText(json.toString(2));
        final TournamentLeaderboard leaderboard = TournamentLeaderboard.fromApiJson(json);

        Log.d(SportsDataApiClient.class.getSimpleName(), String.format("Leaderboard: %s", leaderboard));

        // Extract players and populate dropdown
         final ArrayAdapter<String> playersAd
             = new ArrayAdapter<>(
             binding.playersSpinner.getContext(),
             android.R.layout.simple_spinner_item,
             leaderboard.getPlayers().stream().map(p -> p.getName () + " (pos=" + p.getRank() + " score=" + p.getTotalScore() + ")").collect(Collectors.toList()));
         binding.playersSpinner.setAdapter(playersAd);
      });
    });
  }
}
