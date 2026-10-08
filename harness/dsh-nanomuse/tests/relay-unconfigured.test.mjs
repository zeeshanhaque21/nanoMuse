// No relay configured (the fork's default): the cloud service must still start, and every call
// to the relay refuses with `relay_unconfigured` before a request leaves. A configured origin
// keeps sending its requests to that origin.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { Relay, RelayError } from '../lib/relay.js'
import { SyncRelay } from '../lib/sync.js'

const refuses = (e) => e instanceof RelayError && e.code === 'relay_unconfigured'

test('an unconfigured relay constructs and refuses every call before any request', async () => {
  let requests = 0
  const fetchImpl = async () => {
    requests++
    return new Response('{}')
  }
  const relay = new Relay('', fetchImpl)
  assert.equal(relay.origin, '')
  await assert.rejects(relay.requestCode('someone@example.org'), refuses)
  const sync = new SyncRelay('', fetchImpl)
  await assert.rejects(sync.state('key'), refuses)
  assert.equal(requests, 0)
})

test('a configured relay sends its requests to that origin', async () => {
  const seen = []
  const fetchImpl = async (url) => {
    seen.push(String(url))
    return new Response('{}', { status: 200 })
  }
  await new Relay('https://relay.example.org/', fetchImpl).requestCode('someone@example.org')
  assert.deepEqual(seen, ['https://relay.example.org/v1/auth/code'])
})
