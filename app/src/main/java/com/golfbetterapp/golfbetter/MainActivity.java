package com.golfbetterapp.golfbetter;

import androidx.annotation.Nullable;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;
import androidx.navigation.NavController;
import androidx.navigation.Navigation;
import androidx.navigation.ui.AppBarConfiguration;
import androidx.navigation.ui.NavigationUI;

import com.golfbetterapp.golfbetter.clients.PgaAppEngineClient;
import com.golfbetterapp.golfbetter.databinding.ActivityMainBinding;
import com.golfbetterapp.golfbetter.databinding.ActivityMainBinding;
import com.firebase.ui.auth.AuthUI;
import com.firebase.ui.auth.IdpResponse;
import com.google.android.material.snackbar.Snackbar;
import com.google.firebase.FirebaseApp;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;

import java.util.Arrays;
import java.util.List;

public class MainActivity extends AppCompatActivity {
  private static final int RC_SIGN_IN = 123;
  private AppBarConfiguration appBarConfiguration;

  private String signedInUser;

  @Override
  protected void onCreate(final Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    FirebaseApp.initializeApp(this);

    final ActivityMainBinding binding = ActivityMainBinding.inflate(getLayoutInflater());
    setContentView(binding.getRoot());

    setSupportActionBar(binding.toolbar);
    // Hide the action bar
    if (getSupportActionBar() != null) {
      getSupportActionBar().hide();
    }

    final NavController navController = Navigation.findNavController(this, R.id.nav_host_fragment_content_main);
    appBarConfiguration = new AppBarConfiguration.Builder(navController.getGraph()).build();
    NavigationUI.setupActionBarWithNavController(this, navController, appBarConfiguration);

    final Button signinButton = findViewById(R.id.sign_in_button);
    signinButton.setOnClickListener(new View.OnClickListener() {
      @Override
      public void onClick(View v) {
        signIn();
      }
    });

    final Button signoutButton = findViewById(R.id.sign_out_button);
    signoutButton.setOnClickListener(new View.OnClickListener() {
      @Override
      public void onClick(View v) {
        handleSignOut();
      }
    });

    binding.fab.setOnClickListener(new View.OnClickListener() {
      @Override
      public void onClick(final View view) {
        Snackbar.make(view, "Replace with your own action", Snackbar.LENGTH_LONG).setAnchorView(R.id.fab).setAction("Action", null).show();
      }
    });
  }

  @Override
  public boolean onCreateOptionsMenu(final Menu menu) {
    // Inflate the menu; this adds items to the action bar if it is present.
    getMenuInflater().inflate(R.menu.menu_main, menu);
    return true;
  }

  @Override
  public boolean onOptionsItemSelected(final MenuItem item) {
    // Handle action bar item clicks here. The action bar will
    // automatically handle clicks on the Home/Up button, so long
    // as you specify a parent activity in AndroidManifest.xml.
    int id = item.getItemId();

    //noinspection SimplifiableIfStatement
    if (id == R.id.action_settings) {
      return true;
    }

    return super.onOptionsItemSelected(item);
  }

  @Override
  public boolean onSupportNavigateUp() {
    final NavController navController = Navigation.findNavController(this, R.id.nav_host_fragment_content_main);
    return NavigationUI.navigateUp(navController, appBarConfiguration) || super.onSupportNavigateUp();
  }

  @Override
  protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
    super.onActivityResult(requestCode, resultCode, data);

    if (requestCode == RC_SIGN_IN) {
      final IdpResponse response = IdpResponse.fromResultIntent(data);
      if (resultCode == RESULT_OK) {
        // Successfully signed in
        final FirebaseUser user = FirebaseAuth.getInstance().getCurrentUser();
        Log.i("MainActivity", "Got firebase user: " + user.getEmail());
        handleSignIn(user.getEmail());
        //updateUI(user);
      } else {
        // Sign-in failed
        Log.e("MainActivity", "Firebase login failed");
        //updateUI(null);
      }
    }
  }

  private void signIn() {
    // Choose authentication providers
    final List<AuthUI.IdpConfig> providers = Arrays.asList(
        new AuthUI.IdpConfig.GoogleBuilder().build()
    );

    // Create and launch sign-in intent
    final Intent signInIntent = AuthUI.getInstance()
        .createSignInIntentBuilder()
        .setAvailableProviders(providers)
        .build();
    startActivityForResult(signInIntent, RC_SIGN_IN);
  }

  public void handleSignIn(final String user) {
    signedInUser = user;
    findViewById(R.id.sign_in_button).setVisibility(View.GONE);
    findViewById(R.id.sign_out_button).setVisibility(View.VISIBLE);
    findViewById(R.id.current_user).setVisibility(View.VISIBLE);
    findViewById(R.id.content_main_container).setVisibility(View.VISIBLE);
    ((TextView)findViewById(R.id.current_user)).setText(signedInUser);

    // Signal tournament refresh to LeaderboardFragment
    final Intent intent = new Intent(LeaderboardFragment.REFRESH_TOURNAMENTS_INTENT);
    LocalBroadcastManager.getInstance(this).sendBroadcast(intent);

    PgaAppEngineClient.updateUser(this, new Utils.ApiCallback<Void>() {
      @Override
      public void onSuccess(final Void result) {
        Log.i("MainActivity", "Successfully posted user");
      }

      @Override
      public void onFailure(final Exception e) {
        Log.e("MainActivity", "Error posting user", e);
      }
    });
  }

  public void handleSignOut() {
    signedInUser = null;
    findViewById(R.id.sign_in_button).setVisibility(View.VISIBLE);
    findViewById(R.id.sign_out_button).setVisibility(View.GONE);
    findViewById(R.id.current_user).setVisibility(View.GONE);
    findViewById(R.id.content_main_container).setVisibility(View.GONE);
    ((TextView)findViewById(R.id.current_user)).setText(null);
  }
}