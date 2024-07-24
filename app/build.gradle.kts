plugins {
    alias(libs.plugins.androidApplication)
    id("com.google.gms.google-services")
}

android {
    namespace = "com.golfbetterapp.golfbetter"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.golfbetterapp.golfbetter"
        minSdk = 28
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    buildFeatures {
        viewBinding = true
    }
}

dependencies {
    implementation(libs.appcompat)
    implementation(libs.material)
    implementation(libs.constraintlayout)
    implementation(libs.navigation.fragment)
    implementation(libs.navigation.ui)
    implementation(libs.recyclerview)
    implementation(libs.gson)
    implementation(libs.play.services.auth)
    implementation(libs.googleid)
    implementation(libs.firebase.ui.auth)
    implementation(libs.firebase.auth)
    testImplementation(libs.junit)
    testImplementation(libs.json)
    testImplementation(libs.mockito)
    androidTestImplementation(libs.ext.junit)
    androidTestImplementation(libs.espresso.core)

    compileOnly(libs.lombok)
    annotationProcessor(libs.lombok)
}