# MoneyKit Connect for Android

## Overview

MoneyKit Connect for Android is a quick and secure way to link bank accounts from within your
Android app. The SDK handles connecting to a financial institution in your app (credential
validation, multi-factor authentication, error handling, etc.) without passing sensitive information
to your server.

This project provides a basic example of how to integrate the MoneyKit Connect Android SDK into an 
Android app.

## Installation

Add the following line to your app's build.gradle file:

```kotlin
implementation("com.moneykit:connect:0.0.7")
```

## Documentation

See https://docs.moneykit.com/connect/android for documentation.

## Get Started

Follow the steps below to get started with a basic SDK integration.

### Create a Configuration

Starting the MoneyKit Connect flow begins with creating a `link_session_token`. Once the
`link_session_token` is passed to your app, create an instance of `MkConfiguration`, then create an
instance of `MkLinkHandler` passing in the previously created `MkConfiguration`, and call
`presentLinkFlow(context)` on the handler. Note that each time you open MoneyKit
Connect, you will need to get a new `link_session_token` from your server and create a new
`MkConfiguration` with it.

```kotlin
val linkSessionToken: String = "your_link_session_token"

val configuration = MkConfiguration(
    sessionToken = linkSession.linkSessionToken,
    onSuccess = { successType ->
        when (successType) {
            is MkLinkSuccessType.Linked -> {
                Timber.i("Linked - Token to exchange: ${successType.institution.token.value}")
            }

            is MkLinkSuccessType.Relinked -> {
                Timber.i("Relinked")
            }
        }
    },
    onExit = {
        Timber.i("Exited Link")
    },
)
```

### Create a Handler

A Handler is a one-time use object used to open a MoneyKit Connect session. The Handler must be
retained for the duration of the Connect flow. It will also be needed to respond to OAuth
Universal Link redirects.

```kotlin
val linkHandler = MkLinkHandler(configuration)
```

### Open MoneyKit Connect

Finally, open Link by calling `presentLinkFlow(context)` on the Handler object.
This will usually be done in a button’s target action. Context should be your current activity.

```kotlin
linkHandler.presentLinkFlow(this)
```
