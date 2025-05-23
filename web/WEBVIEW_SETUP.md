# Setting Up WebView Android App

This web app is designed to work seamlessly in an Android WebView with proper theme support and optimizations.

## WebView Setup

### 1. Configure WebView in Android

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var webView: WebView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webView)
        setupWebView()
    }

    private fun setupWebView() {
        webView.apply {
            settings.apply {
                javaScriptEnabled = true
                domStorageEnabled = true
                databaseEnabled = true
                setGeolocationEnabled(false)
                mediaPlaybackRequiresUserGesture = false
            }

            // Add JavaScript Interface for theme sync
            addJavascriptInterface(WebAppInterface(this@MainActivity), "Android")
        }

        // Load the web app
        webView.loadUrl("http://localhost:3000") // Change to your production URL
    }
}
```

### 2. JavaScript Interface for Theme Sync

```kotlin
class WebAppInterface(private val context: Context) {
    @JavascriptInterface
    fun isDarkMode(): Boolean {
        return when (context.resources?.configuration?.uiMode?.and(Configuration.UI_MODE_NIGHT_MASK)) {
            Configuration.UI_MODE_NIGHT_YES -> true
            else -> false
        }
    }
}
```

### 3. Theme Sync Implementation

```kotlin
override fun onConfigurationChanged(newConfig: Configuration) {
    super.onConfigurationChanged(newConfig)
    val isDark = newConfig.uiMode and Configuration.UI_MODE_NIGHT_MASK == Configuration.UI_MODE_NIGHT_YES
    webView.evaluateJavascript("window.setWebViewTheme(${isDark})", null)
}
```

## Webview Optimizations

The web app includes several optimizations for WebView:

1. Touch-optimized inputs and buttons
2. System theme sync
3. Mobile-specific styles
4. Hidden scrollbars for native feel
5. Proper font sizing to prevent zooming
6. Hardware acceleration support

## Theme Integration

1. The web app automatically detects system theme changes
2. Manual theme control is available through JavaScript
3. Theme preferences are persisted
4. Smooth transitions between themes

## Testing WebView Integration

1. Start the development server:
   ```bash
   cd web
   npm run dev
   ```

2. Configure Android emulator network:
   ```bash
   adb reverse tcp:3000 tcp:3000
   ```

3. Build and run the Android app

## Production Deployment

1. Build the web app:
   ```bash
   cd web
   npm run build
   ```

2. Upload the build to your hosting service

3. Update the WebView URL in Android to point to your production URL

## Troubleshooting

1. Theme not syncing:
   - Verify JavaScript interface is properly registered
   - Check console logs for errors
   - Ensure `setWebViewTheme` function is accessible

2. Performance issues:
   - Enable hardware acceleration
   - Verify WebView settings
   - Check for memory leaks

3. Layout problems:
   - Verify viewport settings
   - Check media queries
   - Test on different screen sizes
