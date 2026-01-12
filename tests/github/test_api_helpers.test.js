'use strict';

const assert = require('node:assert/strict');
const { test } = require('node:test');

const { selectGithubClientForRateLimit } = require('../../.github/scripts/api-helpers');

class FakeOctokit {
  constructor(options = {}) {
    this.auth = options.auth;
  }
}

function buildGithubClient({ remaining, limit = 5000, resetSeconds = 3600 }) {
  const reset = Math.floor(Date.now() / 1000) + resetSeconds;
  return {
    rest: {
      rateLimit: {
        get: async () => ({
          data: {
            resources: {
              core: { remaining, limit, reset },
            },
          },
        }),
      },
    },
    constructor: FakeOctokit,
  };
}

test('selectGithubClientForRateLimit keeps the current client when safe', async () => {
  const github = buildGithubClient({ remaining: 800 });
  const result = await selectGithubClientForRateLimit(github, {
    env: { SERVICE_BOT_PAT: 'token-ignored' },
  });

  assert.equal(result.github, github);
  assert.equal(result.usedFallback, false);
  assert.equal(result.reason, 'rate-limit-ok');
  assert.equal(result.status.safe, true);
});

test('selectGithubClientForRateLimit falls back to PAT when low', async () => {
  const github = buildGithubClient({ remaining: 12 });
  const result = await selectGithubClientForRateLimit(github, {
    env: { SERVICE_BOT_PAT: 'pat-token' },
  });

  assert.equal(result.usedFallback, true);
  assert.equal(result.reason, 'pat-fallback');
  assert.equal(result.status.safe, false);
  assert.equal(result.github instanceof FakeOctokit, true);
  assert.equal(result.github.auth, 'pat-token');
});

test('selectGithubClientForRateLimit keeps the current client without PAT', async () => {
  const github = buildGithubClient({ remaining: 12 });
  const result = await selectGithubClientForRateLimit(github, { env: {} });

  assert.equal(result.github, github);
  assert.equal(result.usedFallback, false);
  assert.equal(result.reason, 'no-pat');
  assert.equal(result.status.safe, false);
});

test('selectGithubClientForRateLimit handles missing client', async () => {
  const result = await selectGithubClientForRateLimit(null);

  assert.equal(result.github, null);
  assert.equal(result.usedFallback, false);
  assert.equal(result.reason, 'missing-client');
});

test('selectGithubClientForRateLimit respects PAT env precedence', async () => {
  const github = buildGithubClient({ remaining: 12 });
  const result = await selectGithubClientForRateLimit(github, {
    env: {
      ACTIONS_BOT_PAT: 'preferred-token',
      SERVICE_BOT_PAT: 'fallback-token',
    },
  });

  assert.equal(result.usedFallback, true);
  assert.equal(result.reason, 'pat-fallback');
  assert.equal(result.github.auth, 'preferred-token');
});

test('selectGithubClientForRateLimit avoids fallback without constructor', async () => {
  const github = Object.create(null);
  github.rest = {
    rateLimit: {
      get: async () => ({
        data: {
          resources: {
            core: { remaining: 12, limit: 5000, reset: Math.floor(Date.now() / 1000) + 3600 },
          },
        },
      }),
    },
  };
  const result = await selectGithubClientForRateLimit(github, {
    env: { SERVICE_BOT_PAT: 'pat-token' },
  });

  assert.equal(result.github, github);
  assert.equal(result.usedFallback, false);
  assert.equal(result.reason, 'no-octokit');
});
