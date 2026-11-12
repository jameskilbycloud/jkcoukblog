// Tests for the /api/sizer/* proxy in _worker.template.js.
//
// Run with: node --test 'tests/worker/*.test.mjs'
//
// The worker template is a plain ES module whose only export is the default
// fetch handler (Workers treats named exports as entrypoints), so these go
// through fetch() with a fake env and a stubbed global fetch for the three
// upstreams: the Access signing keys, the CSP token exchange and the Sizer
// API. The point of the suite is the access control: without a valid Access
// JWT, no route may reach VMware.

import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const TEMPLATE = fileURLToPath(new URL('../../_worker.template.js', import.meta.url));
const modPath = join(mkdtempSync(join(tmpdir(), 'worker-')), 'worker.mjs');
writeFileSync(modPath, readFileSync(TEMPLATE, 'utf8'));
const worker = (await import(pathToFileURL(modPath).href)).default;

const TEAM = 'example-team';
const ISSUER = `https://${TEAM}.cloudflareaccess.com`;
const AUD = 'aud-tag-123';
const CSP_URL = 'https://console.cloud.vmware.com/csp/gateway/am/api/auth/api-tokens/authorize';
const SIZER_URL = 'https://vmc.vmware.com/api/vmc-sizer/v5/recommendation';

const b64url = bytes => Buffer.from(bytes).toString('base64url');
const keypair = await crypto.subtle.generateKey(
  { name: 'RSASSA-PKCS1-v1_5', modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: 'SHA-256' },
  true, ['sign', 'verify']);
const otherKeypair = await crypto.subtle.generateKey(
  { name: 'RSASSA-PKCS1-v1_5', modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: 'SHA-256' },
  true, ['sign', 'verify']);
const publicJwk = { ...(await crypto.subtle.exportKey('jwk', keypair.publicKey)), kid: 'k1', alg: 'RS256' };

async function makeJwt(claims = {}, { key = keypair.privateKey, kid = 'k1' } = {}) {
  const now = Math.floor(Date.now() / 1000);
  const header = b64url(JSON.stringify({ alg: 'RS256', kid, typ: 'JWT' }));
  const payload = b64url(JSON.stringify({ iss: ISSUER, aud: [AUD], email: 'james@example.com', iat: now, exp: now + 600, ...claims }));
  const sig = await crypto.subtle.sign('RSASSA-PKCS1-v1_5', key, new TextEncoder().encode(`${header}.${payload}`));
  return `${header}.${payload}.${b64url(new Uint8Array(sig))}`;
}

let calls;
beforeEach(() => {
  calls = [];
  globalThis.fetch = async (url, init = {}) => {
    calls.push({ url: String(url), init });
    if (url === `${ISSUER}/cdn-cgi/access/certs`) return Response.json({ keys: [publicJwk] });
    if (url === CSP_URL) return Response.json({ access_token: 'short-lived', expires_in: 1800 });
    if (url === SIZER_URL) return Response.json({ sddcList: [{ ok: true }] });
    throw new Error(`unexpected fetch ${url}`);
  };
});

const ENV = { CF_ACCESS_TEAM_DOMAIN: TEAM, CF_ACCESS_AUD: AUD, VMC_CSP_API_TOKEN: 'long-lived-secret' };

async function call(path, { method = 'GET', jwt, body, env = ENV } = {}) {
  const headers = {};
  if (jwt) headers['Cf-Access-Jwt-Assertion'] = jwt;
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  const req = new Request(`https://jameskilby.co.uk${path}`, {
    method, headers, body: body === undefined ? undefined : JSON.stringify(body)
  });
  return worker.fetch(req, env, { waitUntil() {} });
}

const VMS = [
  { vm: 'web01', power_state: 'on', vcpu: 4, consumed_vcpu: 1.2, vram_gib: 16, consumed_vram_gib: 9, provisioned_gib: 120, in_use_gib: 80 },
  { vm: 'old02', power_state: 'off', vcpu: 2, vram_gib: 4, provisioned_gib: 40, in_use_gib: 10 }
];

const reachedVmware = () => calls.some(c => c.url === CSP_URL || c.url === SIZER_URL);

// ── access control ──────────────────────────────────────────────────────────

test('no Access JWT: every route is 401 and nothing reaches VMware', async () => {
  for (const [path, method] of [['/api/sizer/status', 'GET'], ['/api/sizer/signin', 'GET'], ['/api/sizer/recommendation', 'POST']]) {
    const res = await call(path, { method, body: method === 'POST' ? { vms: VMS } : undefined });
    assert.equal(res.status, 401, path);
    assert.equal((await res.json()).signin, '/api/sizer/signin');
  }
  assert.equal(reachedVmware(), false);
});

test('Access not configured on the site fails closed, even with a JWT', async () => {
  const res = await call('/api/sizer/recommendation', {
    method: 'POST', jwt: await makeJwt(), body: { vms: VMS }, env: { VMC_CSP_API_TOKEN: 'x' }
  });
  assert.equal(res.status, 401);
  assert.equal((await res.json()).accessConfigured, false);
  assert.equal(reachedVmware(), false);
});

test('JWTs that must be rejected', async () => {
  const now = Math.floor(Date.now() / 1000);
  const bad = {
    'wrong audience': await makeJwt({ aud: ['someone-else'] }),
    'wrong issuer': await makeJwt({ iss: 'https://evil.cloudflareaccess.com' }),
    'expired': await makeJwt({ exp: now - 10 }),
    'signed by another key': await makeJwt({}, { key: otherKeypair.privateKey }),
    'unknown kid': await makeJwt({}, { kid: 'nope' }),
    'garbage': 'not.a.jwt'
  };
  for (const [why, jwt] of Object.entries(bad)) {
    const res = await call('/api/sizer/recommendation', { method: 'POST', jwt, body: { vms: VMS } });
    assert.equal(res.status, 401, why);
  }
  assert.equal(reachedVmware(), false);
});

// ── behaviour once signed in ────────────────────────────────────────────────

test('status reports whether the CSP token is configured, never the token', async () => {
  const jwt = await makeJwt();
  const on = await (await call('/api/sizer/status', { jwt })).json();
  assert.deepEqual(on, { configured: true, user: 'james@example.com' });
  const off = await (await call('/api/sizer/status', { jwt, env: { ...ENV, VMC_CSP_API_TOKEN: '' } })).json();
  assert.equal(off.configured, false);
  assert.ok(!JSON.stringify(on).includes('long-lived-secret'));
});

test('signin sends you back to the analyzer', async () => {
  const res = await call('/api/sizer/signin', { jwt: await makeJwt() });
  assert.equal(res.status, 302);
  assert.equal(res.headers.get('Location'), '/vmc-analyzer/#design');
});

test('recommendation maps the VMs like the Python server and proxies with a bearer token', async () => {
  const res = await call('/api/sizer/recommendation', {
    method: 'POST', jwt: await makeJwt(), body: { vms: VMS, hostType: 'i4i', stretched: false }
  });
  assert.equal(res.status, 200);
  const body = await res.json();
  assert.deepEqual(body.sizer_response, { sddcList: [{ ok: true }] });

  const sent = calls.find(c => c.url === SIZER_URL);
  assert.equal(sent.init.headers.Authorization, 'Bearer short-lived');
  const payload = JSON.parse(sent.init.body);
  assert.deepEqual(payload, body.sizer_request);
  assert.equal(payload.configurations.sddcHostType, 'I4I');
  assert.equal(payload.configurations.clusterType, 'SAZ');
  assert.equal(payload.workloadProfiles[0].storagePreference, 'AUTO');
  const [web, old] = payload.workloadProfiles[0].vmList;
  assert.deepEqual(web, {
    vmId: '1', vmName: 'web01', vmState: 'RUNNING',
    vmComputeInfo: { vCpu: 4, vCpuOverall: 1.2 },
    vmMemoryInfo: { vRam: 16, vRamConsumed: 9 },          // GiB, not MiB
    vmStorageInfo: { vmdkTotal: 120, vmdkUsed: 80 }
  });
  assert.equal(old.vmState, 'POWERED_OFF');
  assert.deepEqual(old.vmComputeInfo, { vCpu: 2, vCpuOverall: 0 });
});

test('stretched clusters are MAZ with vSAN-only storage', async () => {
  const res = await call('/api/sizer/recommendation', {
    method: 'POST', jwt: await makeJwt(), body: { vms: VMS, hostType: 'nonsense', stretched: true }
  });
  const { sizer_request: p } = await res.json();
  assert.equal(p.configurations.clusterType, 'MAZ');
  assert.equal(p.configurations.sddcHostType, 'AUTO');
  assert.equal(p.workloadProfiles[0].storagePreference, 'vSAN_ONLY');
  assert.equal(p.workloadProfiles[0].extStorageVendorType, null);
});

test('bad requests are rejected before any VMware call', async () => {
  const jwt = await makeJwt();
  assert.equal((await call('/api/sizer/recommendation', { method: 'POST', jwt, body: { vms: [] } })).status, 400);
  assert.equal((await call('/api/sizer/recommendation', { method: 'POST', jwt, body: { nope: 1 } })).status, 400);
  const noToken = await call('/api/sizer/recommendation', {
    method: 'POST', jwt, body: { vms: VMS }, env: { ...ENV, VMC_CSP_API_TOKEN: '' }
  });
  assert.equal(noToken.status, 400);
  assert.equal(reachedVmware(), false);
});

test('upstream status passes through so a mapping error is visible', async () => {
  const realFetch = globalThis.fetch;
  globalThis.fetch = async (url, init) => url === SIZER_URL
    ? new Response(JSON.stringify({ message: 'bad field' }), { status: 400 })
    : realFetch(url, init);
  const res = await call('/api/sizer/recommendation', { method: 'POST', jwt: await makeJwt(), body: { vms: VMS } });
  assert.equal(res.status, 400);
  assert.deepEqual((await res.json()).sizer_response, { message: 'bad field' });
});

test('responses are never cached', async () => {
  const res = await call('/api/sizer/status', { jwt: await makeJwt() });
  assert.equal(res.headers.get('Cache-Control'), 'no-store');
});
