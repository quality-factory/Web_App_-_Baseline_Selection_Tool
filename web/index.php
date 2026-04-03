<?php
/**
 * BST SPA router — security headers, rate limiting, GT&C acceptance logging (FR-P16).
 *
 * This is the entry point for all BST requests. It sets security headers,
 * enforces rate limiting, and serves the SPA shell.
 */

declare(strict_types=1);

// ── Security headers (architecture §13.4) ───────────────────────────────
header("Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'");
header('Strict-Transport-Security: max-age=31536000; includeSubDomains');
header('X-Frame-Options: DENY');
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: no-referrer');

// ── Rate limiting (FR-P12: 60 req/min/IP) ───────────────────────────────
$clientIp = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
$rateLimit = 60;
$ratePeriod = 60; // seconds

if (extension_loaded('apcu') && apcu_enabled()) {
    // APCu-based rate limiting (preferred)
    $cacheKey = 'bst_rate_' . $clientIp;
    $current = apcu_fetch($cacheKey, $success);
    if ($success === false) {
        apcu_store($cacheKey, 1, $ratePeriod);
    } else {
        if ($current >= $rateLimit) {
            header('Retry-After: ' . $ratePeriod);
            http_response_code(429);
            header('Content-Type: application/json; charset=utf-8');
            echo json_encode(['error' => 'rate_limit_exceeded']);
            exit;
        }
        apcu_inc($cacheKey);
    }
} else {
    // File-based fallback (OTD-06)
    $rateTmpDir = sys_get_temp_dir() . '/bst_rate';
    if (!is_dir($rateTmpDir)) {
        @mkdir($rateTmpDir, 0700, true);
    }
    $rateFile = $rateTmpDir . '/' . md5($clientIp) . '.json';
    $rateData = ['count' => 0, 'window_start' => time()];

    if (file_exists($rateFile)) {
        $raw = @file_get_contents($rateFile);
        if ($raw !== false) {
            $parsed = json_decode($raw, true);
            if (is_array($parsed)) {
                $rateData = $parsed;
            }
        }
    }

    // Reset window if expired
    if (time() - $rateData['window_start'] > $ratePeriod) {
        $rateData = ['count' => 0, 'window_start' => time()];
    }

    if ($rateData['count'] >= $rateLimit) {
        header('Retry-After: ' . $ratePeriod);
        http_response_code(429);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode(['error' => 'rate_limit_exceeded']);
        exit;
    }

    $rateData['count']++;
    @file_put_contents($rateFile, json_encode($rateData), LOCK_EX);
}

// ── GT&C acceptance logging (FR-P16) ────────────────────────────────────
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['gtc_action'])) {
    $logDir = __DIR__ . '/../logs';
    if (!is_dir($logDir)) {
        @mkdir($logDir, 0700, true);
    }
    $logFile = $logDir . '/gtc_acceptance.log';

    $logEntry = json_encode([
        'timestamp'       => date('c'),
        'ip_address'      => $clientIp,
        'gtc_version'     => $_POST['gtc_version'] ?? 'unknown',
        'action'          => $_POST['gtc_action'] === 'accepted' ? 'accepted' : 'declined',
        'user_agent_hash' => hash('sha256', $_SERVER['HTTP_USER_AGENT'] ?? ''),
    ]);

    // Write-once append (FM-P05: failure logged but does not block)
    $writeResult = @file_put_contents($logFile, $logEntry . "\n", FILE_APPEND | LOCK_EX);
    if ($writeResult === false) {
        error_log('BST: GT&C acceptance log write failed');
    }

    http_response_code(204);
    exit;
}

// ── Serve SPA shell ─────────────────────────────────────────────────────
$requestUri = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH);

// Route API requests
if (preg_match('#^.*/api/baselines\.php$#', $requestUri)) {
    require __DIR__ . '/api/baselines.php';
    exit;
}

// Route static assets
$staticExtensions = ['js', 'css', 'txt', 'ico', 'png', 'jpg', 'svg'];
$ext = pathinfo($requestUri, PATHINFO_EXTENSION);
if (in_array($ext, $staticExtensions, true)) {
    return false; // Let the web server handle static files
}

// All other routes: serve the SPA shell
readfile(__DIR__ . '/index.html');
