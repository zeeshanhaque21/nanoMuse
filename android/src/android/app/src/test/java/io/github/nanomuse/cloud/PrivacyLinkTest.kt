package io.github.nanomuse.cloud

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class PrivacyLinkTest {
    @Test fun `the shipped default opens nothing`() {
        assertNull(NanoMuseCloud.openablePrivacyUrl(NanoMuseCloud.PRIVACY_URL))
    }

    @Test fun `a blank link opens nothing`() {
        assertNull(NanoMuseCloud.openablePrivacyUrl(""))
        assertNull(NanoMuseCloud.openablePrivacyUrl("   "))
    }

    @Test fun `a configured link opens as given`() {
        assertEquals("https://relay.example.org/privacy", NanoMuseCloud.openablePrivacyUrl("https://relay.example.org/privacy"))
    }
}
