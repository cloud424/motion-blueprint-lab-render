#!/usr/bin/env python3
"""No-network safety tests for GH post-publication artifact cleanup."""
import unittest
from cleanup_published_artifacts import verified_receipt, matching_artifacts

class PublishedCleanupTests(unittest.TestCase):
    def receipt(self):
        return {
            "episode":"EP02",
            "publication_state":"complete",
            "platforms":{
                "youtube":{"status":"public_verified","verification_method":"youtube_api","verified_at":"2026-11-14T02:00:00+08:00","url":"https://www.youtube.com/shorts/cJI-RxomXbs"},
                "facebook":{"status":"public_verified","verification_method":"facebook_graph_api","verified_at":"2026-11-14T02:00:00+08:00","url":"https://www.facebook.com/reel/1512437634109179/"},
                "instagram":{"status":"public_verified","verification_method":"instagram_graph_api","verified_at":"2026-11-14T02:00:00+08:00","url":"https://www.instagram.com/reel/DftyKIRHOmW/"},
                "tiktok":{"status":"public_verified","verification_method":"tiktok_native_page","verified_at":"2026-11-14T02:00:00+08:00","url":"https://www.tiktok.com/@motionblueprintlab/video/1234567890"}
            }
        }

    def test_four_sites_verified_allows_only_matching_episode(self):
        ok, ep = verified_receipt(self.receipt())
        self.assertTrue(ok)
        self.assertEqual(ep,"EP02")

    def test_buffer_sent_not_native_public_does_not_delete(self):
        receipt=self.receipt()
        receipt["platforms"]["tiktok"]["status"]="sent"
        receipt["platforms"]["tiktok"]["verification_method"]="buffer_sent"
        self.assertFalse(verified_receipt(receipt)[0])

    def test_three_sites_does_not_delete(self):
        receipt=self.receipt()
        del receipt["platforms"]["instagram"]
        self.assertFalse(verified_receipt(receipt)[0])

    def test_pending_does_not_delete(self):
        receipt=self.receipt()
        receipt["publication_state"]="pending"
        self.assertFalse(verified_receipt(receipt)[0])

    def test_wrong_domain_does_not_delete(self):
        receipt=self.receipt()
        receipt["platforms"]["youtube"]["url"]="https://attacker.example/shorts/abc"
        self.assertFalse(verified_receipt(receipt)[0])

    def test_matching_artifacts_never_hits_other_episodes(self):
        arts=[{"name":"EP02_PanamaCanal_PRIVATE_REVIEW","id":1},{"name":"EP01_Taipei101","id":2},{"name":"EP020_not_ep02","id":3},{"name":"EP02_render","id":4,"expired":True},{"name":"project-renders","id":5}]
        self.assertEqual([a["id"] for a in matching_artifacts("EP02",arts)],[1])

if __name__=="__main__":
    unittest.main()
