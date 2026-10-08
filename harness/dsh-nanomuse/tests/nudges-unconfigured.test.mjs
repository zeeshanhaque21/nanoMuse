// The star-nudges policy is read through the relay's guard: with no origin configured the
// read refuses with `relay_unconfigured` before a request leaves; a configured origin reads
// its `/v1/nudges`.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { fetchNudgesPolicy } from '../lib/nudges.js'
import { RelayError } from '../lib/relay.js'

test('no relay origin: the nudges policy refuses before any request', async () => {
  let requests = 0
  const fetchImpl = async () => {
    requests++
    return new Response('{}')
  }
  await assert.rejects(
    fetchNudgesPolicy('', fetchImpl),
    (e) => e instanceof RelayError && e.code === 'relay_unconfigured',
  )
  assert.equal(requests, 0)
})

test('a configured origin reads the policy from its /v1/nudges', async () => {
  const seen = []
  const fetchImpl = async (url) => {
    seen.push(String(url))
    return new Response(JSON.stringify({ star: { enabled: false } }), { status: 200 })
  }
  assert.deepEqual(await fetchNudgesPolicy('https://relay.example.org', fetchImpl), {
    star: { enabled: false },
  })
  assert.deepEqual(seen, ['https://relay.example.org/v1/nudges'])
})
