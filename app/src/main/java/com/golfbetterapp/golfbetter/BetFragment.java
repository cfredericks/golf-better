package com.golfbetterapp.golfbetter;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.navigation.fragment.NavHostFragment;

import com.golfbetterapp.golfbetter.databinding.FragmentBetBinding;
import com.golfbetterapp.golfbetter.models.Bet;

import java.util.Arrays;
import java.util.stream.Collectors;

public class BetFragment extends Fragment {

  private FragmentBetBinding binding;

  @Override
  public View onCreateView(@NonNull LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {

    binding = FragmentBetBinding.inflate(inflater, container, false);
    return binding.getRoot();

  }

  public void onViewCreated(@NonNull View view, Bundle savedInstanceState) {
    super.onViewCreated(view, savedInstanceState);

    binding.buttonBet.setOnClickListener(v -> NavHostFragment.findNavController(BetFragment.this).navigate(R.id.action_BetFragment_to_LeaderboardFragment));

    final ArrayAdapter<String> metricsAd
        = new ArrayAdapter<>(
        this.getContext(),
        android.R.layout.simple_spinner_item,
        Arrays.stream(Bet.MetricType.values()).map(Enum::name).collect(Collectors.toList()));
    binding.metricsSpinner.setAdapter(metricsAd);

    final ArrayAdapter<String> comparatorsAd
        = new ArrayAdapter<>(
        this.getContext(),
        android.R.layout.simple_spinner_item,
        Arrays.stream(Bet.ComparatorType.values()).map(Enum::name).collect(Collectors.toList()));
    binding.comparatorsSpinner.setAdapter(comparatorsAd);

    final ArrayAdapter<String> playerTypesAd
        = new ArrayAdapter<>(
        this.getContext(),
        android.R.layout.simple_spinner_item,
        Arrays.stream(Bet.PlayerType.values()).map(Enum::name).collect(Collectors.toList()));
    binding.playerTypesSpinner.setAdapter(playerTypesAd);

    final ArrayAdapter<String> roundTypesAd
        = new ArrayAdapter<>(
        this.getContext(),
        android.R.layout.simple_spinner_item,
        Arrays.stream(Bet.RoundType.values()).map(Enum::name).collect(Collectors.toList()));
    binding.roundTypesSpinner.setAdapter(roundTypesAd);

    final ArrayAdapter<String> betsAd
        = new ArrayAdapter<>(
        this.getContext(),
        android.R.layout.simple_spinner_item,
        Arrays.stream(Bet.BetType.values()).map(Enum::name).collect(Collectors.toList()));
    binding.betsSpinner.setAdapter(betsAd);
  }

  @Override
  public void onDestroyView() {
    super.onDestroyView();
    binding = null;
  }

}