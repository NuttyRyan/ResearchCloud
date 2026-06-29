import { afterEach, describe, expect, it, vi } from 'vitest';
import { api, ApiError, getToken, setToken } from './client';

describe('api client', () => {
  afterEach(() => {
    vi.restoreAllMocks();
    setToken(null);
  });

  it('stores and clears the auth token', () => {
    setToken('abc123');
    expect(getToken()).toBe('abc123');
    setToken(null);
    expect(getToken()).toBeNull();
  });

  it('parses FastAPI string error details into ApiError', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Connection not found' }), {
        status: 404,
      }),
    );
    await expect(api.listConnections()).rejects.toMatchObject({
      status: 404,
      message: 'Connection not found',
    });
  });

  it('parses FastAPI validation error arrays', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: [{ msg: 'field required' }] }), {
        status: 422,
      }),
    );
    const err = await api.listConnections().catch((e) => e);
    expect(err).toBeInstanceOf(ApiError);
    expect(err.message).toContain('field required');
  });
});
