package com.golfbetterapp.golfbetter;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.HorizontalScrollView;
import android.widget.ImageView;
import android.widget.Spinner;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;

import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.golfbetterapp.golfbetter.clients.PgaAppEngineClient;
import com.golfbetterapp.golfbetter.models.Player;
import com.golfbetterapp.golfbetter.models.LeaderboardPlayerRound;
import com.golfbetterapp.golfbetter.models.LeaderboardPlayerRoundHole;
import com.golfbetterapp.golfbetter.models.Tournament;
import com.golfbetterapp.golfbetter.models.TournamentLeaderboard;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class LeaderboardFragment extends Fragment {
  public static final String REFRESH_TOURNAMENTS_INTENT = "REFRESH_TOURNAMENTS";

  private final ExecutorService executorService = Executors.newSingleThreadExecutor();
  private Spinner tournamentSpinner;
  private RecyclerView leaderboardRecyclerView;
  private TournamentAdapter tournamentAdapter;
  private LeaderboardAdapter leaderboardAdapter;
  private List<Tournament> tournaments;
  private TournamentLeaderboard leaderboard;

  private final BroadcastReceiver REFRESH_RECEIVER = new BroadcastReceiver() {
    @Override
    public void onReceive(final Context context, final Intent intent) {
      if (REFRESH_TOURNAMENTS_INTENT.equals(intent.getAction())) {
        // Handle the refresh action
        fetchTournamentData();
      }
    }
  };

  @Override
  public View onCreateView(final LayoutInflater inflater, final ViewGroup container, final Bundle savedInstanceState) {
    final View view = inflater.inflate(R.layout.fragment_leaderboard, container, false);

    // Register the local broadcast receiver
    LocalBroadcastManager.getInstance(requireContext()).registerReceiver(
        REFRESH_RECEIVER, new IntentFilter(REFRESH_TOURNAMENTS_INTENT));

    tournaments = new ArrayList<>();

    tournamentSpinner = view.findViewById(R.id.tournament_spinner);
    leaderboardRecyclerView = view.findViewById(R.id.leaderboard_recycler_view);
    leaderboardRecyclerView.setLayoutManager(new LinearLayoutManager(getContext()));

    tournamentAdapter = new TournamentAdapter(getContext(), android.R.layout.simple_spinner_item, tournaments);
    tournamentAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
    tournamentSpinner.setAdapter(tournamentAdapter);

    leaderboardAdapter = new LeaderboardAdapter(leaderboard);
    leaderboardRecyclerView.setAdapter(leaderboardAdapter);

    tournamentSpinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
      @Override
      public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
        final Tournament selectedTournament = tournaments.get(position);
        fetchPlayersData(selectedTournament.getId());
      }

      @Override
      public void onNothingSelected(AdapterView<?> parent) {
        // No action needed
      }
    });

    view.findViewById(R.id.refresh_button).setOnClickListener(new View.OnClickListener() {
      @Override
      public void onClick(final View v) {
        fetchTournamentData();
      }
    });

    return view;
  }

  @Override
  public void onDestroy() {
    super.onDestroy();
    // Unregister the local broadcast receiver
    LocalBroadcastManager.getInstance(requireContext()).unregisterReceiver(REFRESH_RECEIVER);
  }

  private void fetchTournamentData() {
    executorService.execute(() -> {
      PgaAppEngineClient.getTournaments(getContext(), new Utils.ApiCallback<List<Tournament>>() {
        @Override
        public void onSuccess(final List<Tournament> result) {
          tournaments = result;
          Log.i("LeaderboardFragment", "Got PG tournaments: " + tournaments);
          tournaments.sort(Comparator.comparing(Tournament::getStartDate));

          // Get active or next tournament to set default selection
          int activeTournamentIdx = -1;
          int prevTournamentIdx = -1;
          Tournament activeTournament = null;
          Tournament prevTournament = null;
          LocalDate today = LocalDate.now();
          for (int i = 0; i < tournaments.size(); i++) {
            final Tournament tournament = tournaments.get(i);
            if (tournament.getIsInProgress() != null && tournament.getIsInProgress()) {
              activeTournament = tournament;
              activeTournamentIdx = i;
            } else if (tournament.getStartDate() != null && tournament.getEndDate() != null && !tournament.getStartDate().isAfter(today) && !tournament.getEndDate().isBefore(today)) {
              activeTournament = tournament;
              activeTournamentIdx = i;
            }

            if (tournament.getStartDate() != null && tournament.getEndDate() != null && tournament.getEndDate().isBefore(today) && (prevTournament == null || tournament.getEndDate().isAfter(prevTournament.getStartDate()))) {
              prevTournament = tournament;
              prevTournamentIdx = i;
            }
          }
          Log.i("LeaderboardFragment", "Got tournament API response: " + tournaments);
          Log.i("LeaderboardFragment", "Active tournament: " + activeTournament);
          Log.i("LeaderboardFragment", "Prev tournament: " + prevTournament);
          if (getActivity() != null) {
            final int finalActiveTournamentIdx = activeTournamentIdx;
            final int finalNextTournamentIdx = prevTournamentIdx;
            getActivity().runOnUiThread(() -> {
              tournamentAdapter.updateTournaments(tournaments);
              tournamentSpinner.setSelection(finalActiveTournamentIdx >= 0 ? finalActiveTournamentIdx :
                  finalNextTournamentIdx >= 0 ? finalNextTournamentIdx : tournaments.size() - 1);
            });
          }
        }

        @Override
        public void onFailure(final Exception e) {
          Log.e("LeaderboardFragment", "Error reading tournaments", e);
        }
      });
    });
  }

  private void fetchPlayersData(final String tournamentId) {
    executorService.execute(() -> {
      if (getActivity() != null) {
        getActivity().runOnUiThread(() -> {
          leaderboardAdapter.updateLeaderboard(null);
        });
      }

      PgaAppEngineClient.getLeaderboard(tournamentId, getContext(), new Utils.ApiCallback<TournamentLeaderboard>() {
        @Override
        public void onSuccess(final TournamentLeaderboard result) {
          leaderboard = result;
          if (getActivity() != null) {
            getActivity().runOnUiThread(() -> {
              leaderboardAdapter.updateLeaderboard(leaderboard);
            });
          }
        }

        @Override
        public void onFailure(final Exception e) {
          Log.e("LeaderboardFragment", "Error querying leaderboard", e);
        }
      });
    });
  }

  private static class TournamentAdapter extends ArrayAdapter<Tournament> {
    private List<Tournament> tournaments;

    public TournamentAdapter(final Context context, int resource, List<Tournament> tournaments) {
      super(context, resource, tournaments);
      this.tournaments = tournaments;
    }

    void updateTournaments(final List<Tournament> tournaments) {
      if (tournaments == null) {
        this.tournaments = new ArrayList<>();
      } else {
        this.tournaments = tournaments;
      }
      notifyDataSetChanged();
    }

    @Override
    public int getCount() {
      return tournaments != null ? tournaments.size() : 0;
    }

    @Override
    public Tournament getItem(final int position) {
      return tournaments != null ? tournaments.get(position) : null;
    }

    @Override
    public View getView(final int position, final View convertView, final ViewGroup parent) {
      final View view = super.getView(position, convertView, parent);
      setColor(view, position);
      return view;
    }

    @Override
    public View getDropDownView(final int position, final View convertView, ViewGroup parent) {
      final View view = super.getDropDownView(position, convertView, parent);
      setColor(view, position);
      return view;
    }

    private void setColor(final View view, final int position) {
      final TextView textView = (TextView) view;
      final Tournament tournament = tournaments.get(position);

      final LocalDate today = LocalDate.now();

      boolean isOver = false;
      boolean isActive = false;
      if (tournament.getIsInProgress() != null && tournament.getIsInProgress()) {
        isActive = true;
      } else if (tournament.getStartDate() != null && tournament.getEndDate() != null && !tournament.getStartDate().isAfter(today) && !tournament.getEndDate().isBefore(today)) {
        isActive = true;
      } else if (tournament.getIsOver() != null && tournament.getIsOver()) {
        isOver = true;
      } else if (tournament.getEndDate() != null && tournament.getEndDate().isBefore(today)) {
        isOver = true;
      }

      if (isActive) {
        textView.setBackgroundColor(Color.rgb(0, 0x88, 0));
      } else if (isOver) {
        textView.setBackgroundColor(Color.GRAY);
      } else {
        textView.setBackgroundColor(Color.TRANSPARENT);
      }

      textView.setText(tournament.getStartDate() + " - " + tournament.getName());
    }
  }

  private static class LeaderboardAdapter extends RecyclerView.Adapter<LeaderboardAdapter.PlayerViewHolder> {
    private List<Player> players;

    LeaderboardAdapter(final TournamentLeaderboard leaderboard) {
      if (leaderboard != null) {
        this.players = leaderboard.getPlayers();
      }
    }

    void updateLeaderboard(final TournamentLeaderboard leaderboard) {
      if (leaderboard == null) {
        this.players = new ArrayList<>();
      } else {
        this.players = leaderboard.getPlayers();
      }
      notifyDataSetChanged();
    }

    @Override
    public PlayerViewHolder onCreateViewHolder(final ViewGroup parent, final int viewType) {
      final View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_player, parent, false);
      return new PlayerViewHolder(view);
    }

    @Override
    public void onBindViewHolder(final PlayerViewHolder holder, final int position) {
      final Player player = players.get(position);
      holder.bind(player);
    }

    @Override
    public int getItemCount() {
      return players != null ? players.size() : 0;
    }

    static class PlayerViewHolder extends RecyclerView.ViewHolder {
      private final TextView playerName;
      private final TextView playerRank;
      private final TextView playerScore;
      private final TextView playerCountry;
      private final ImageView expandIcon;
      private final ViewGroup roundsContainer;
      private boolean isExpanded = false;

      PlayerViewHolder(final View itemView) {
        super(itemView);
        playerName = itemView.findViewById(R.id.player_name);
        playerRank = itemView.findViewById(R.id.player_rank);
        playerScore = itemView.findViewById(R.id.player_score);
        playerCountry = itemView.findViewById(R.id.player_country);
        expandIcon = itemView.findViewById(R.id.expand_icon);
        roundsContainer = itemView.findViewById(R.id.rounds_container);

        expandIcon.setOnClickListener(v -> {
          if (isExpanded) {
            roundsContainer.setVisibility(View.GONE);
            expandIcon.setImageResource(R.drawable.ic_expand_more);
          } else {
            roundsContainer.setVisibility(View.VISIBLE);
            expandIcon.setImageResource(R.drawable.ic_expand_less);
          }
          isExpanded = !isExpanded;
        });
      }

      void bind(final Player player) {
        playerName.setText(player.getName());
        playerRank.setText(player.getRank() != null ? player.getRank() : "");
        playerScore.setText(player.getTotalScore() != null ? String.valueOf(player.getTotalScore()) : "");
        playerCountry.setText(player.getCountry());
        displayRounds(player.getRounds());
      }

      private void displayRounds(final List<LeaderboardPlayerRound> rounds) {
        roundsContainer.removeAllViews();

        int roundNumber = 1;
        for (final LeaderboardPlayerRound round : rounds) {
          // Add round label
          final TextView roundLabel = new TextView(itemView.getContext());
          roundLabel.setText("Round " + roundNumber++);
          roundLabel.setTypeface(null, Typeface.BOLD);
          roundLabel.setPadding(8, 8, 8, 8);
          if (roundNumber > 1) {
            roundsContainer.addView(new TextView(itemView.getContext()));
          }
          roundsContainer.addView(roundLabel);

          final HorizontalScrollView horizontalScrollView = new HorizontalScrollView(itemView.getContext());
          final TableLayout tableLayout = new TableLayout(itemView.getContext());
          tableLayout.setStretchAllColumns(true);

          final TableRow holeNumberRow = new TableRow(itemView.getContext());
          final TableRow parRow = new TableRow(itemView.getContext());
          final TableRow shotsRow = new TableRow(itemView.getContext());

          addCellToRow(holeNumberRow, "Hole", true, true);
          addCellToRow(parRow, "Par", true, false);
          addCellToRow(shotsRow, "Shots", true, false);

          boolean alternateColor = false;

          for (final LeaderboardPlayerRoundHole hole : round.getHoles()) {
            addCellToRow(holeNumberRow, String.valueOf(hole.getNumber()), false, true, alternateColor);
            addCellToRow(parRow, String.valueOf(hole.getPar()), false, false, alternateColor);
            addCellToRowWithColor(shotsRow, hole.getScore() != null ? String.valueOf(hole.getScore()) : "",
                hole.getScore(), hole.getPar(), alternateColor);
            alternateColor = !alternateColor;
          }

          tableLayout.addView(holeNumberRow);
          tableLayout.addView(parRow);
          tableLayout.addView(shotsRow);

          horizontalScrollView.addView(tableLayout);
          roundsContainer.addView(horizontalScrollView);
        }
      }

      private void addCellToRow(final TableRow row, String text, final boolean isHeader, final boolean isHoleRow) {
        addCellToRow(row, text, isHeader, isHoleRow, false);
      }

      private void addCellToRow(final TableRow row, final String text, final boolean isHeader,
                                final boolean isHoleRow, final boolean alternateColor) {
        final TextView textView = new TextView(itemView.getContext());
        textView.setText(text);
        textView.setPadding(8, 8, 8, 8);
        if (isHeader) {
          textView.setTypeface(null, Typeface.BOLD);
        }
        if (isHoleRow) {
          textView.setBackgroundColor(Color.DKGRAY);
          textView.setTextColor(Color.WHITE);
        } else if (alternateColor) {
          textView.setBackgroundColor(Color.LTGRAY);
        } else {
          textView.setBackgroundColor(Color.WHITE);
        }

        // Apply border drawable to the TextView
        //textView.setBackgroundResource(R.drawable.cell_border);

        row.addView(textView);
      }

      private void addCellToRowWithColor(final TableRow row, final String text, final Integer shots, final int par,
                                         final boolean alternateColor) {
        final TextView textView = new TextView(itemView.getContext());
        textView.setText(text);
        textView.setPadding(8, 8, 8, 8);

        if (shots == null) {
          textView.setBackgroundColor(alternateColor ? Color.LTGRAY : Color.WHITE);
        } else if (shots < par) {
          if ((par - shots) == 1) {
            textView.setBackground(ContextCompat.getDrawable(itemView.getContext(), R.drawable.green_circle));
          } else {
            textView.setBackground(ContextCompat.getDrawable(itemView.getContext(), R.drawable.blue_circle));
          }
        } else if (shots > par) {
          textView.setBackground(ContextCompat.getDrawable(itemView.getContext(), R.drawable.red_square));
        } else {
          textView.setBackgroundColor(alternateColor ? Color.LTGRAY : Color.WHITE);
        }

        // if (shots < par) {
        //   textView.setBackgroundColor(Color.GREEN);
        // } else if (shots > par) {
        //   textView.setBackgroundColor(Color.RED);
        // } else {
        //   textView.setBackgroundColor(alternateColor ? Color.LTGRAY : Color.WHITE);
        // }

        // Apply border drawable to the TextView
        //textView.setBackgroundResource(R.drawable.cell_border);

        row.addView(textView);
      }
    }
  }
}

