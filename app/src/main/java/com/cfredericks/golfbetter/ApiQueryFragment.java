package com.cfredericks.golfbetter;

import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.navigation.fragment.NavHostFragment;

import com.cfredericks.golfbetter.databinding.FragmentApiQueryBinding;

public class ApiQueryFragment extends Fragment implements AdapterView.OnItemSelectedListener {
  private FragmentApiQueryBinding binding;

  @Override
  public View onCreateView(@NonNull LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
    binding = FragmentApiQueryBinding.inflate(inflater, container, false);
    return binding.getRoot();
  }

  public void onViewCreated(@NonNull View view, Bundle savedInstanceState) {
    super.onViewCreated(view, savedInstanceState);

    binding.tournamentsSpinner.setOnItemSelectedListener(this);

    binding.buttonApiQuery.setOnClickListener(v -> {
      NavHostFragment.findNavController(ApiQueryFragment.this).navigate(R.id.action_ApiQueryFragment_to_BetFragment);
    });

    binding.buttonQuery.setOnClickListener(v -> {
      SportsDataApiClient.updateTournaments(binding);
    });
  }

  @Override
  public void onDestroyView() {
    super.onDestroyView();
    binding = null;
  }

  @Override
  public void onItemSelected(final AdapterView<?> parent, final View view, final int position, final long id) {
    // Get selected tournament
    final String selected = ((ArrayAdapter<String>) binding.tournamentsSpinner.getAdapter()).getItem(position);

    // Extract tournament ID from the name of the tournament in the dropdown which is:
    //   {TOURNAMENT_ID} ({TOURNAMENT_ID})
    // TODO: Is there a better way to do this in Android and store state that can be indexed into?
    final int startIdx = selected.lastIndexOf("(");
    final int endIdx = selected.lastIndexOf(")");
    int tournamentId = Integer.parseInt(selected.substring(startIdx + 1, endIdx));

    // TODO: Remove before committing, but setting to PGA Championship since the data is random
    //       in the tournaments API response, so the above value is nonsense.
    tournamentId = 32;

    Log.i(ApiQueryFragment.class.getSimpleName(), String.format("Querying leaderboard with tournamentId=%d", tournamentId));
    SportsDataApiClient.updateLeaderboard(tournamentId, binding);
  }

  @Override
  public void onNothingSelected(final AdapterView<?> parent) {

  }
}