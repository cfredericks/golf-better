import {
  signInWithPopup,
  signOut as firebaseSignOut,
  GoogleAuthProvider,
  onAuthStateChanged as firebaseOnAuthStateChanged,
  type User as FirebaseUser,
} from 'firebase/auth';
import { auth } from './firebase';
import type { User } from '../types';

const googleProvider = new GoogleAuthProvider();

export const signInWithGoogle = async (): Promise<User> => {
  const result = await signInWithPopup(auth, googleProvider);
  const user = result.user;
  return {
    id: user.uid,
    email: user.email ?? '',
    name: user.displayName ?? user.email ?? '',
    photoUrl: user.photoURL ?? undefined,
  };
};

export const signOut = async (): Promise<void> => {
  await firebaseSignOut(auth);
};

export const onAuthStateChanged = (
  callback: (user: User | null) => void
): (() => void) => {
  return firebaseOnAuthStateChanged(auth, (firebaseUser: FirebaseUser | null) => {
    if (firebaseUser) {
      callback({
        id: firebaseUser.uid,
        email: firebaseUser.email ?? '',
        name: firebaseUser.displayName ?? firebaseUser.email ?? '',
        photoUrl: firebaseUser.photoURL ?? undefined,
      });
    } else {
      callback(null);
    }
  });
};

export const getIdToken = async (): Promise<string | null> => {
  const user = auth.currentUser;
  if (!user) return null;
  return user.getIdToken();
};

export const getCurrentUser = (): User | null => {
  const user = auth.currentUser;
  if (!user) return null;
  return {
    id: user.uid,
    email: user.email ?? '',
    name: user.displayName ?? user.email ?? '',
    photoUrl: user.photoURL ?? undefined,
  };
};
