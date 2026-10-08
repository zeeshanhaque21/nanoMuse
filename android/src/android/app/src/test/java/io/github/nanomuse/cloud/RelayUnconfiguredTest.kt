package io.github.nanomuse.cloud

import org.junit.Assert.assertEquals
import org.junit.Test

class RelayUnconfiguredTest {
    @Test fun `no relay is refused with the relay's own code, before any request`() {
        var refused: NanoMuseCloud.CloudException? = null
        try {
            NanoMuseCloud.requireRelay("")
        } catch (e: NanoMuseCloud.CloudException) {
            refused = e
        }
        assertEquals("relay_unconfigured", refused?.code)
    }

    @Test fun `a configured relay is passed through unchanged`() {
        assertEquals("https://relay.example.org", NanoMuseCloud.requireRelay("https://relay.example.org"))
    }
}
