package com.golfbetterapp.golfbetter;

import android.content.Context;

import androidx.credentials.GetPasswordOption;
import androidx.credentials.exceptions.GetCredentialException;
import android.os.Build;
import android.os.SystemClock;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.credentials.Credential;
import androidx.credentials.CredentialManager;
import androidx.credentials.CredentialManagerCallback;
import androidx.credentials.GetCredentialRequest;
import androidx.credentials.GetCredentialResponse;
import androidx.credentials.PasswordCredential;

import com.google.firebase.FirebaseApp;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;

public class TokenManager {
    private static final TokenManager INSTANCE = new TokenManager();

    private String idToken;
    private long expirationTime;

    private TokenManager() {
    }

    public static synchronized TokenManager getInstance() {
        return INSTANCE;
    }

    public interface IdTokenCallback {
        void onSuccess(final String idToken);
        void onFailure(final Exception e);
    }

    public void getIdToken(final Context context, final IdTokenCallback callback) {
        if (idToken != null && SystemClock.elapsedRealtime() < expirationTime) {
            Log.d("TokenManager", "Using cached id token");
            callback.onSuccess(idToken);
        } else {
            final FirebaseUser user = FirebaseAuth.getInstance().getCurrentUser();
            if (user != null) {
                Log.d("TokenManager", "Using token for existing firebase user: " + user.getEmail());
                user.getIdToken(true)
                        .addOnCompleteListener(task -> {
                            if (task.isSuccessful()) {
                                idToken = task.getResult().getToken();
                                expirationTime = SystemClock.elapsedRealtime() + 60 * 60 * 1000; // 1 hour
                                callback.onSuccess(idToken);
                            } else {
                                callback.onFailure(task.getException());
                            }
                        });
            } else {
                Log.d("TokenManager", "Attempting to login to firebase...");
                // Attempt to retrieve credentials using CredentialManager
                final CredentialManager credentialManager = CredentialManager.create(context);
                final GetCredentialRequest request = new GetCredentialRequest.Builder()
                    .addCredentialOption(new GetPasswordOption())
                    .build();

                credentialManager.getCredentialAsync(context, request, null, context.getMainExecutor(), new CredentialManagerCallback<GetCredentialResponse, GetCredentialException>() {
                        @Override
                        public void onResult(final GetCredentialResponse resp) {
                          Log.i("TokenManager", "Got response: " + resp);
                            final Credential credential = resp.getCredential();
                            if (credential instanceof PasswordCredential) {
                                final String email = ((PasswordCredential) credential).getId();
                                final String password = ((PasswordCredential) credential).getPassword();
                                signInWithFirebase(email, password, callback);
                            } else {
                                callback.onFailure(new Exception("Invalid credential type"));
                            }
                        }

                        @Override
                        public void onError(@NonNull final GetCredentialException e) {
                            Log.w("TokenManager", "signInResult:failed", e);
                        }
                      });
            }
        }
    }

    private void signInWithFirebase(final String email, final String password, final IdTokenCallback callback) {
        FirebaseAuth.getInstance().signInWithEmailAndPassword(email, password)
            .addOnCompleteListener(task -> {
                if (task.isSuccessful()) {
                    final FirebaseUser user = task.getResult().getUser();
                    if (user != null) {
                        user.getIdToken(true).addOnCompleteListener(tokenTask -> {
                            if (tokenTask.isSuccessful()) {
                                idToken = tokenTask.getResult().getToken();
                                expirationTime = SystemClock.elapsedRealtime() + 60 * 60 * 1000; // 1 hour
                                callback.onSuccess(idToken);
                            } else {
                                callback.onFailure(tokenTask.getException());
                            }
                        });
                    } else {
                        callback.onFailure(new Exception("User sign-in failed"));
                    }
                } else {
                    callback.onFailure(task.getException());
                }
            });
    }
}