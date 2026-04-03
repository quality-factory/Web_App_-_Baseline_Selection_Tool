<?php
/**
 * PHP-gated knowledge base endpoint (architecture §12.1, S7-B).
 *
 * Rate limit, bot user-agent rejection, serve baselines.json.
 */

declare(strict_types=1);

// ── Security headers ────────────────────────────────────────────────────
header("Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'");
header('Strict-Transport-Security: max-age=31536000; includeSubDomains');
header('X-Frame-Options: DENY');
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: no-referrer');

// ── Bot user-agent rejection (FR-P13) ───────────────────────────────────
$userAgent = $_SERVER['HTTP_USER_AGENT'] ?? '';
$botPatterns = [
    'GPTBot', 'ClaudeBot', 'Google-Extended', 'CCBot',
    'anthropic-ai', 'Applebot-Extended', 'Bytespider',
    'Scrapy', 'python-requests',
];

foreach ($botPatterns as $pattern) {
    if (stripos($userAgent, $pattern) !== false) {
        http_response_code(403);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode(['error' => 'forbidden']);
        exit;
    }
}

// ── Rate limiting (FR-P12: 60 req/min/IP) ───────────────────────────────
$clientIp = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
$rateLimit = 60;
$ratePeriod = 60;

if (extension_loaded('apcu') && apcu_enabled()) {
    $cacheKey = 'bst_api_rate_' . $clientIp;
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
    // File-based fallback
    $rateTmpDir = sys_get_temp_dir() . '/bst_rate';
    if (!is_dir($rateTmpDir)) {
        @mkdir($rateTmpDir, 0700, true);
    }
    $rateFile = $rateTmpDir . '/api_' . md5($clientIp) . '.json';
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

// ── Serve knowledge base ────────────────────────────────────────────────
$kbPath = __DIR__ . '/../../data/baselines.json';

if (!file_exists($kbPath) || !is_readable($kbPath)) {
    http_response_code(500);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(['error' => 'internal_error']);
    exit;
}

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: public, max-age=3600');
readfile($kbPath);
