package com.cfredericks.golfbetter;

import androidx.annotation.NonNull;
import androidx.credentials.Credential;
import androidx.credentials.CredentialManager;

import androidx.credentials.exceptions.GetCredentialException;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.credentials.CredentialManagerCallback;
import androidx.credentials.CustomCredential;
import androidx.credentials.GetCredentialRequest;
import androidx.credentials.GetCredentialResponse;
import androidx.credentials.PasswordCredential;
import androidx.credentials.PublicKeyCredential;
import androidx.navigation.NavController;
import androidx.navigation.Navigation;
import androidx.navigation.ui.AppBarConfiguration;
import androidx.navigation.ui.NavigationUI;

import com.cfredericks.golfbetter.databinding.ActivityMainBinding;
import com.google.android.libraries.identity.googleid.GetGoogleIdOption;
import com.google.android.libraries.identity.googleid.GoogleIdTokenCredential;
import com.google.android.material.snackbar.Snackbar;

import java.util.UUID;

public class MainActivity extends AppCompatActivity {
  private static final String ANDROID_CLIENT_ID = "901053117124-0i8ecbbme8cre1hl3287ddg19kr2u1mp.apps.googleusercontent.com";
  private static final String WEB_CLIENT_ID = "901053117124-pv70p11m4vdl7qkmphqbgf6e9a8ui8pn.apps.googleusercontent.com";
  private CredentialManager credentialManager;

  private AppBarConfiguration appBarConfiguration;

  private String signedInUser;

  @Override
  protected void onCreate(final Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    credentialManager = CredentialManager.create(this);

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

  private void signIn() {
    final GetGoogleIdOption googleIdOption = new GetGoogleIdOption.Builder()
        .setFilterByAuthorizedAccounts(false)
        .setServerClientId(WEB_CLIENT_ID)
        .setAutoSelectEnabled(true)
        .setNonce(UUID.randomUUID().toString())
        .build();
    final GetCredentialRequest request = new GetCredentialRequest.Builder()
        .addCredentialOption(googleIdOption)
        .build();

    credentialManager.getCredentialAsync(
        this,
        request,
        null,
        getMainExecutor(),
        new CredentialManagerCallback<GetCredentialResponse, GetCredentialException>() {
          @Override
          public void onResult(final GetCredentialResponse resp) {
            Log.w("MainActivity", "signInResult:success: " + resp);
            handleSignIn(resp);
          }

          @Override
          public void onError(@NonNull final GetCredentialException e) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
              Log.w("MainActivity", "signInResult:failed", e);
            }
          }
        });
  }

  public void handleSignIn(final GetCredentialResponse result) {
    // Handle the successfully returned credential.
    final Credential credential = result.getCredential();
    if (credential instanceof PublicKeyCredential) {
      final String responseJson = ((PublicKeyCredential) credential).getAuthenticationResponseJson();
      Log.i("MainActivity", "Got PublicKeyCredential: " + responseJson);
      // Share responseJson i.e. a GetCredentialResponse on your server to validate and authenticate
    } else if (credential instanceof PasswordCredential) {
      final String username = ((PasswordCredential) credential).getId();
      final String password = ((PasswordCredential) credential).getPassword();
      Log.i("MainActivity", "PasswordCredential: user=" + username + ", pw=" + password);
      handleSignIn(username);
      return;
    } else if (credential instanceof CustomCredential) {
      if (GoogleIdTokenCredential.TYPE_GOOGLE_ID_TOKEN_CREDENTIAL.equals(credential.getType())) {
        try {
          // Use googleIdTokenCredential and extract id to validate and
          // authenticate on your server.
          final GoogleIdTokenCredential googleIdTokenCredential = GoogleIdTokenCredential
              .createFrom(credential.getData());
          handleSignIn(googleIdTokenCredential.getId());
          Log.e("MainActivity", "Got GoogleIdTokenCredential: id=" + googleIdTokenCredential.getId() + ", name=" + googleIdTokenCredential.getDisplayName() + ", data=" + googleIdTokenCredential.getData());
          return;
        } catch (final Exception e) {
          Log.e("MainActivity", "Received an invalid google id token response for data: " + credential.getData(), e);
        }
      } else {
        Log.e("MainActivity", "Unexpected type of custom credential: " + credential.getType() + "(" + credential.getClass().getCanonicalName() + "), data=" + credential);
      }
    } else {
      // Catch any unrecognized credential type here.
      Log.e("MainActivity", "Unexpected type of credential: " + credential.getType() + "(" + credential.getClass().getCanonicalName() + "), data=" + credential);
    }

    if (signedInUser == null) {
      Log.e("MainActivity", "Unable to extract username");
    }

    handleSignOut();
  }

  public void handleSignIn(final String user) {
    signedInUser = user;
    findViewById(R.id.sign_in_button).setVisibility(View.GONE);
    findViewById(R.id.sign_out_button).setVisibility(View.VISIBLE);
    findViewById(R.id.current_user).setVisibility(View.VISIBLE);
    findViewById(R.id.content_main_container).setVisibility(View.VISIBLE);
    ((TextView)findViewById(R.id.current_user)).setText(signedInUser);
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