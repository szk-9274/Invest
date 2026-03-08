import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { listAllBacktests } from './backtest';

describe('listAllBacktests', () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    fetchMock.mockReset();
  });

  it('uses relative /api base URL by default', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({ backtests: [] }),
    });

    await listAllBacktests();

    expect(fetchMock).toHaveBeenCalledWith('/api/backtest/list');
  });
});
