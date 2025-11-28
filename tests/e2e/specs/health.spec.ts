import { test, expect, Page } from '@playwright/test';
import axios from 'axios';

/**
 * E2E Test Suite: System Health & Basic Integration
 * 
 * Tests:
 * - Health Check Endpoint
 * - Database Connectivity
 * - API Response Times
 * - Service Availability
 */

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

test.describe('System Health Checks', () => {

    test('should return healthy status from /health endpoint', async ({ request }) => {
        const response = await request.get(`${BASE_URL}/health`);

        expect(response.ok()).toBeTruthy();
        expect(response.status()).toBe(200);

        const healthData = await response.json();
        expect(healthData).toHaveProperty('status');
        expect(healthData.status).toBe('healthy');
    });

    test('should have database connection', async ({ request }) => {
        const response = await request.get(`${BASE_URL}/health`);
        const healthData = await response.json();

        expect(healthData).toHaveProperty('services');
        expect(healthData.services).toHaveProperty('database');
        expect(healthData.services.database).toBe('connected');
    });

    test('should respond within acceptable time (< 2s)', async ({ request }) => {
        const startTime = Date.now();
        await request.get(`${BASE_URL}/health`);
        const responseTime = Date.now() - startTime;

        expect(responseTime).toBeLessThan(2000);
    });

    test('should have valid uptime metric', async ({ request }) => {
        const response = await request.get(`${BASE_URL}/health`);
        const healthData = await response.json();

        expect(healthData).toHaveProperty('uptime');
        expect(typeof healthData.uptime).toBe('number');
        expect(healthData.uptime).toBeGreaterThan(0);
    });
});

test.describe('API Integration Tests', () => {

    test('should handle CORS correctly', async ({ request }) => {
        const response = await request.get(`${BASE_URL}/health`, {
            headers: {
                'Origin': 'https://example.com'
            }
        });

        const headers = response.headers();
        expect(headers).toHaveProperty('access-control-allow-origin');
    });

    test('should return proper content-type headers', async ({ request }) => {
        const response = await request.get(`${BASE_URL}/health`);
        const headers = response.headers();

        expect(headers['content-type']).toContain('application/json');
    });
});

test.describe('Error Handling Tests', () => {

    test('should handle 404 routes gracefully', async ({ request }) => {
        const response = await request.get(`${BASE_URL}/non-existent-route`);
        expect(response.status()).toBe(404);
    });

    test('should reject invalid HTTP methods on webhook', async ({ request }) => {
        const response = await request.get(`${BASE_URL}/webhook`);
        // Webhook should only accept POST
        expect(response.status()).not.toBe(200);
    });
});

